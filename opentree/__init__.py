#!/usr/bin/env python3
__version__ = "0.0.1" # sync with setup.py
import requests
import logging
import json
import sys

_LOG = logging.getLogger('opentree')

class OTWebServicesError(Exception):
    pass

class OTClientError(Exception):
    pass


def debug(message):
    _LOG.debug(message)

class OTWebServiceWrapper(object):
    def __init__(self, api_endpoint, prefix=None):
        self._api_endpoint = api_endpoint
        self._api_version = 'v3'
        self.call_history = []

    def tree_of_life_induced_subtree(self, node_ids=None, ott_ids=None, label_format="name_and_id"):
        d = {"label_format": label_format.lower().strip()}
        if node_ids or ott_ids:
            if node_ids and ott_ids:
                raise ValueError("Only one of `node_ids` and `ott_ids` can be specified")
            if node_ids:
                 d["node_ids"] = [str(i) for i in node_ids]
            else:
                d["ott_ids"] = [int(i) for i in ott_ids]
        return self._call_api('tree_of_life/induced_subtree', data=d)

    def _call_api(self, method_url_fragment, data, http_method='POST'):
        url = self.make_url(method_url_fragment)
        try:
            return self.do_http_json(url, http_method, data=data)
        except:
            _LOG.exception("Error in {} to {}".format(http_method, url))
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
        if self._api_endpoint == 'dev':
            if front_end:
                return 'https://devtree.opentreeoflife.org/{}/{}'.format(self._api_version, frag)
            return 'https://devapi.opentreeoflife.org/{}/{}'.format(self._api_version, frag)
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

    def http_request(self, url, http_method="GET", data=None, headers=None):
        stored = {'url': url, 'http_method': http_method, 'headers': headers, 'data': data}
        self.call_history.append(stored)
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

        stored['status_code'] = resp.status_code
        debug('Sent {v} to {s}'.format(v=http_method, s=resp.url))
        return resp, stored

    def do_http_json(self,
                     url,
                     http_method='GET',
                     data=None,
                     headers=None,
                     expected_status=200,
                     return_raw_content=False):
        """Call `url` with the http method of `http_method`.
        If specified `data` is passed using json.dumps
        returns True if the response:
             has the expected status code, AND
             has the expected content (if expected_response is not None)
        """
        if headers is None:
            headers = {'content-type': 'application/json', 'accept': 'application/json', }
        resp, call_out = self.http_request(url, http_method, data=data, headers=headers)
        call_out['expected_status_code'] = expected_status
        if not return_raw_content:
            try:
                results = resp.json()
            except:
                try:
                    results = resp.text
                except:
                    results = None
            call_out['response_body'] = results

        if resp.status_code != expected_status:
            m = 'Wrong HTTP status code from server. Expected {}. Got {}.'.format(expected_status, resp.status_code)
            raise OTWebServicesError(m)
        if return_raw_content:
            return resp.text
        return results





class OpenTree(object):
    def __init__(self):
        self._api_endpoint = 'production'
        self._ws = None

    @property
    def ws(self):
        if self._ws is None:
            self._ws = OTWebServiceWrapper(self._api_endpoint)
        return self._ws

    def tree_for_ott_ids(self, ott_ids):
        return self.ws.tree_of_life_induced_subtree(ott_ids=ott_ids)

# Default-configured wrapper
OT = OpenTree()
