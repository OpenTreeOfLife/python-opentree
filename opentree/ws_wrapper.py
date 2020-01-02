#!/usr/bin/env python3
# Implementation file for the calling of HTTP methods and deserializing from JSON.
#   This file is intended as a low-level wrapper that most users would never call directly, but which handles
#   peforming the calls (and if requested) keeping a log of methods called or a curl representation of the
#   calls that were performed.
#

import json
import logging
import sys
import re
from enum import Enum

import requests


def _escape_dq(s):
    """Lightweight escaping function used in writing curl calls...

    """
    if not isinstance(s, str):
        if isinstance(s, bool):
            return 'true' if s else 'false'
        return s
    if '"' in s:
        ss = s.split('"')
        return '"{}"'.format('\\"'.join(ss))
    return '"{}"'.format(s)


class OTWebServicesError(Exception):
    """This type of error is raised when a web-service call fails for a reason that is
    impossible or difficult to diagnose. The string representation of the error should contain
    some helpful information.
    """

    def __init__(self, message, call_record=None):
        super().__init__(message)
        self.call_record = call_record


class OTClientError(OTWebServicesError):
    """This type of error is raised when the calling code does not make a legitimate request
    based on the Open Tree of Life API's (see https://opentreeoflife.github.io/develop/api).
    """

    def __init__(self, message, call_record=None):
        super().__init__(message, call_record=call_record)


class WebServiceCallRecord(object):
    def __init__(self, service_wrapper, url, http_method, headers, data):
        self._request_url = url
        self._request_headers = headers
        self._request_http_method = http_method
        self._request_data = data
        self._response_obj = None
        self._response_dict = None
        self._tree = None
        try:
            self._to_object_converter = service_wrapper.to_object_converter
        except:
            self._to_object_converter = None

    # noinspection PyPep8
    def generate_curl_string(self):
        """Returns a string that is a curl representation of the call
        """
        # may want to revisit this implementation

        v = self._request_http_method
        headers = self._request_headers
        data = self._request_data
        url = self._request_url
        varg = '' if v == 'GET' else '-X {} '.format(v)
        if headers:
            hal = ['-H {}:{}'.format(_escape_dq(k), _escape_dq(v)) for k, v in headers.items()]
            hargs = ' '.join(hal)
        else:
            hargs = ''
        dargs = " --data '{}'".format(json.dumps(data)) if data else ''
        return 'curl {v} {h} {u}{d}'.format(v=varg, u=url, h=hargs, d=dargs)

    def __str__(self):
        prefix = "Web-service call to {}".format(self._request_url)
        if self:
            return '{} succeeded.'.format(prefix)
        elif self._response_obj is None:
            return '{} has not been completed (in progress or has not been triggered yet).'.format(prefix)
        return '{} failed with http_status_code={}'.format(prefix, self.status_code)

    def write_response(self, out):
        out.write(str(self))
        if self._response_obj is None:
            out.write('\n')
            return
        out.write(' Response:\n')
        rdict = self.response_dict
        sf = json.dumps(rdict, sort_keys=True, indent=2, separators=(',', ': '), ensure_ascii=True)
        out.write('{}\n'.format(sf))

    @property
    def url(self):
        return self._request_url

    @property
    def response(self):
        return self._response_obj

    @property
    def status_code(self):
        return None if self._response_obj is None else self._response_obj.status_code

    @property
    def response_dict(self):
        if self._response_dict is None:
            if self._response_obj is None:
                return None
            self._response_dict = self._response_obj.json()
        return self._response_dict

    def __bool__(self):
        sc = self.status_code
        return sc is not None and sc == 200

    @property
    def tree(self):
        if self._tree is None:
            if not self:
                return None
            newick = self.response_dict['newick']
            if self._to_object_converter is None:
                self._tree = newick
            else:
                t = self._to_object_converter.tree_from_newick(newick,
                                                               suppress_internal_node_taxa=True)
                self._tree = t
        return self._tree


class WebServiceRunMode(Enum):
    RUN = 1
    CURL = 2
    CURL_ON_EXIT = 3


class WebServiceWrapper(object):
    def __init__(self, api_endpoint, run_mode=WebServiceRunMode.RUN):
        self._run_mode = run_mode
        self._generate_curl = run_mode in [WebServiceRunMode.CURL, WebServiceRunMode.CURL_ON_EXIT]
        self._perform_ws_calls = run_mode != WebServiceRunMode.CURL
        self._api_endpoint = api_endpoint
        self._api_version = 'v3'
        self._store_responses = False
        self._store_api_calls = True
        self.curl_strings = []
        self.call_history = []
        self.to_object_converter = None

    def _call_api(self, method_url_fragment, data=None,
                  http_method='POST', demand_success=True, headers=None):
        url = self.make_url(method_url_fragment)
        try:
            if headers is None:
                headers = {'content-type': 'application/json', 'accept': 'application/json', }
            elif isinstance(headers, str) and headers.lower() == 'text':
                headers = {'content-type': 'text/plain', 'accept': 'text/plain', }
            call_obj = self._http_request(url, http_method, data=data, headers=headers)
            if demand_success and not call_obj:
                if not self._perform_ws_calls:
                    return None
                m = 'Wrong HTTP status code from server. Expected 200. Got {}.'
                m = m.format(call_obj.status_code)
                raise OTWebServicesError(m, call_obj)
            return call_obj
        except:
            logging.exception("Error in {} to {}".format(http_method, url))
            raise

    def make_url(self, frag, front_end=False):
        while frag.startswith('/'):
            frag = frag[1:]
        while frag.startswith('/'):
            frag = frag[1:]
        while frag.endswith('/'):
            frag = frag[:-1]
        if self._api_endpoint == 'production':
            if front_end:
                return 'https://tree.opentreeoflife.org/{}/{}'.format(self._api_version, frag)
            return 'https://api.opentreeoflife.org/{}/{}'.format(self._api_version, frag)
        if self._api_endpoint == 'files':
            return 'https://files.opentreeoflife.org/{}'.format(frag)
        if self._api_endpoint == 'dev':
            if front_end:
                return 'https://devtree.opentreeoflife.org/{}/{}'.format(self._api_version, frag)
            return 'https://devapi.opentreeoflife.org/{}/{}'.format(self._api_version, frag)
        if self._api_endpoint == 'next':
            return 'https://nexttree.opentreeoflife.org/{}/{}'.format(self._api_version, frag)
        if self._api_endpoint == 'local':
            tax_pat = re.compile(r'^(v[0-9.]+)/([a-z_]+)/(.+)$')
            m = tax_pat.match(frag)
            if m:
                vers, top_level, tail_frag = m.groups()
                if top_level in ('taxonomy', 'tnrs'):
                    t = 'http://localhost:7474/db/data/ext/{}_{}/graphdb/{}'
                    return t.format(top_level, vers, tail_frag)
                elif top_level in ('tree_of_life',):
                    t = 'http://localhost:6543/{}/{}/{}'
                    return t.format(vers, top_level, tail_frag)
            raise NotImplemented('non-taxonomy local system_to_test')
        if self._api_endpoint.startswith('ot'):
            return 'https://{}.opentreeoflife.org/{}/{}'.format(self._api_endpoint, self._api_version, frag)
        if self._api_endpoint[0].isdigit():
            return 'http://{}/{}/{}'.format(self._api_endpoint, self._api_version, frag)
        raise OTClientError('api_endpoint = "{}" is not supported'.format(self._api_endpoint))

    def _http_request(self, url, http_method="GET", data=None, headers=None):
        """Performs an HTTP call and returns a tuple of (the request's response, call storage dict)
        the call storage dict will be None if this wrapper is not storing calls.
        """
        rec = WebServiceCallRecord(self, url, http_method, headers, data)
        if self._store_api_calls:
            self.call_history.append(rec)
        if self._generate_curl:
            self.curl_strings.append(rec.generate_curl_string())
        if not self._perform_ws_calls:
            if self._run_mode == WebServiceRunMode.CURL:
                sys.stderr.write('{}\n'.format(self.curl_strings[-1]))
            return rec
        if data:
            resp = requests.request(http_method,
                                    url,
                                    headers=headers,
                                    data=json.dumps(data),
                                    allow_redirects=True)
        else:
            resp = requests.request(http_method,
                                    url,
                                    headers=headers,
                                    allow_redirects=True)
        rec._response_obj = resp
        logging.debug('Sent {v} to {s}'.format(v=http_method, s=resp.url))
        return rec
