#!/usr/bin/env python3

from .ot_object import OpenTree
from .ws_wrapper import (WebServiceRunMode,
                         )
from . import __version__
import logging
import argparse
import atexit
import sys
import os


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
