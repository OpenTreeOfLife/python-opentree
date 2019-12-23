#!/usr/bin/env python3
__version__ = "0.0.1"  # sync with setup.py

from .object_conversion import get_object_converter
from .ws_wrapper import (OTWebServicesError,
                         OTClientError,
                         WebServiceRunMode,
                         WebServiceWrapper,
                         )
import logging
import argparse
import atexit
import sys
import os


class OTWebServiceWrapper(WebServiceWrapper):
    """This class provides a wrapper to the Open Tree of Life web service methods.
    Actual HTTP calls are handled by methods implemented in the base class for clarity of this code.
    API method calls will be mappable to methods in this class. The methods implemented here do argument checking
    and conversion of the returned JSON to more usable objects.
    """

    def __init__(self, api_endpoint, run_mode=WebServiceRunMode.RUN):
        WebServiceWrapper.__init__(self, api_endpoint, run_mode=run_mode)
        self.to_object_converter = get_object_converter('dendropy')

    def tree_of_life_induced_subtree(self, node_ids=None, ott_ids=None, label_format="name_and_id"):
        d = {"label_format": label_format.lower().strip()}
        if not (node_ids or ott_ids):
            raise ValueError("Either node_ids or ott_ids must be provided")
        if node_ids:
            d["node_ids"] = [str(i) for i in node_ids]
        if ott_ids:
            d["ott_ids"] = [int(i) for i in ott_ids]
        return self._call_api('tree_of_life/induced_subtree', data=d, demand_success=False)

    def taxonomy_about(self):
        return self._call_api('taxonomy/about')

    def tree_of_life_about(self):
        return self._call_api('tree_of_life/about')


class OpenTree(object):
    """This class is intended to provide a high-level wrapper for interaction with OT web services and data.
    The method names are intended to be clear to a wide variety of users, rather than (necessarily matching
    the API calls directly.

    """

    def __init__(self, api_endpoint='production', run_mode=WebServiceRunMode.RUN):
        self._api_endpoint = api_endpoint
        self._run_mode = run_mode
        self._ws = None

    @property
    def ws(self):
        if self._ws is None:
            self._ws = OTWebServiceWrapper(api_endpoint=self._api_endpoint,
                                           run_mode=self._run_mode)
        return self._ws

    def about(self):
        tax_about = self.ws.taxonomy_about()
        tree_about = self.ws.tree_of_life_about()
        return {'taxonomy_about': tax_about,
                'synth_tree_about': tree_about
                }

    def induced_synth_tree(self, node_ids=None, ott_ids=None, label_format="name_and_id",
                           ignore_unknown_ids=True):
        while True:
            call_record = self.ws.tree_of_life_induced_subtree(node_ids=node_ids,
                                                               ott_ids=ott_ids,
                                                               label_format=label_format)
            if call_record:
                return call_record
            if not ignore_unknown_ids:
                msgtemplate = 'Call to induced_subtree failed with the message "{}"'
                message = call_record.response_dict['message']
                raise OTWebServicesError(msgtemplate.format(message))
            unknown_ids = call_record.response_dict['unknown']

            for u in unknown_ids:
                if node_ids and u in node_ids:
                    node_ids.remove(u)
                else:
                    assert u.startswith('ott')
                    ui = int(u[3:])
                    if ott_ids and (ui in ott_ids):
                        ott_ids.remove(ui)


def _write_calls_as_curl(ws_wrapper_obj):
    for line in ws_wrapper_obj.curl_strings:
        sys.stderr.write('{}\n'.format(line))


class OTCommandLineTool(object):
    """Helper class for writing a script that uses a common set of Open Tree command line
    options.
    """

    def __init__(self, usage, name=None):
        script_path = 'unknown' if not sys.argv else sys.argv[0]
        if name is None:
            name = os.path.split(script_path)[-1]
        self.name = name
        self.usage = usage
        self.parser = argparse.ArgumentParser(usage)
        self.api_endpoint = None
        self._add_default_open_tree_arguments()
        self.ot_factory = None

    def _add_default_open_tree_arguments(self):

        """Adds several standard command line arguments to the command line parser"""
        self.parser.add_argument('--version', action='store_true', help='request version information and exit')
        self.parser.add_argument('--logging-level', default='info', type=str,
                                 help='sets the logging level. Should be one of: '
                                      '"debug", "info", "warning", "error", or "critical"')
        self.parser.add_argument('--api-endpoint', default="production",
                                 help='Advanced option: specifies which server to contact of api calls.'
                                      'choices are "production", "dev", "local", "ot" + # or an IP address.')
        self.parser.add_argument('--run-mode', default='run', type=str,
                                 help='Sets the action to take when interacting with the Open Tree API. '
                                      '"run" is the normal mode. '
                                      '"curl" will emit a curl call to standard error instead of performing the '
                                      'web-service call; this usually causes the script to terminate in an error, but'
                                      ' the curl call can be helpful for debugging. "curl-on-exit" will perform the'
                                      ' web-service calls, and then write the curl calls used to stderr on exit.')

    def parse_cli(self, arg_list=None):
        """Parses `arg_list` or sys.argv (if None), handles basic options, returns OpenTree and args.

        May call sys.exit - if the user requested an option like --version to display info and exit.

        Returns an OpenTree instance configured with the specified api_endpoint and the args
            object returned by the argparse object's parse_args method"""
        if arg_list is None:
            arg_list = sys.argv[1:]
        args = self.parser.parse_args(arg_list)
        console = logging.StreamHandler()
        logging_level_dict = {"debug": logging.DEBUG,
                              "info": logging.INFO,
                              "warning": logging.WARNING,
                              "error": logging.ERROR,
                              "critical": logging.CRITICAL,
                              }
        log_lev = logging_level_dict.get(args.logging_level.lower())
        if log_lev is None:
            logging.critical('--logging-level="{}" not understood'.format(args.logging_level))
            sys.exit(1)
        console.setLevel(log_lev)
        if args.version:
            m = '{} using opentree python lib version {}\n'
            sys.stderr.write(m.format(self.name, __version__))
            sys.exit(0)
        api_endpoint = args.api_endpoint.lower()
        self.api_endpoint = api_endpoint
        run_mode_dict = {"run": WebServiceRunMode.RUN,
                         "curl": WebServiceRunMode.CURL,
                         "curl-on-exit": WebServiceRunMode.CURL_ON_EXIT
                         }
        run_mode = run_mode_dict.get(args.run_mode.lower())
        if run_mode is None:
            logging.critical('--run-mode="{}" not understood'.format(args.run_mode))
            sys.exit(1)
        self.ot_factory = lambda: OpenTree(api_endpoint, run_mode)
        ot = self.ot_factory()
        if run_mode == WebServiceRunMode.CURL_ON_EXIT:
            atexit.register(_write_calls_as_curl, ot.ws)
        return ot, args


# Default-configured wrapper
OT = OpenTree()
