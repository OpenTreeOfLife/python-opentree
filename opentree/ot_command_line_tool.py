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


def process_ott_or_node_id_arg(args):
    ott_id, node_id = None, None
    if args.ott_id:
        unaltered_el = args.ott_id.strip()
        el = unaltered_el[3:] if unaltered_el.startswith('ott') else unaltered_el
        try:
            ott_id = int(el)
        except:
            sys.exit('Expecting each ott ID to be an integer or a string starting with "ott". '
                     'Found "{}"\n'.format(unaltered_el))
    if args.node_id:
        node_id = str(args.node_id).strip()
    if node_id and ott_id:
        sys.exit('Expecting either ott-id or node-id, but not both\n')
    return ott_id, node_id


def process_ott_and_node_id_list_args(args):
    ott_id_list, node_id_list = [], []
    if args.ott_ids:
        x = [i.strip().lower() for i in args.ott_ids.split(',')]
        for el in x:
            unaltered_el = el
            if el.startswith('ott'):
                el = el[3:]
            try:
                ott_id_list.append(int(el))
            except:
                sys.exit('Expecting each ott ID to be an integer or a string starting with "ott". '
                         'Found "{}"\n'.format(unaltered_el))
    try:
        # noinspection PyUnusedLocal
        nia = args.node_ids
    except AttributeError:
        pass
    else:
        if args.node_ids:
            node_id_list = [i.strip().lower() for i in args.node_ids.split(',')]
    return ott_id_list, node_id_list


class OTCommandLineTool(object):
    """Helper class for writing a script that uses a common set of Open Tree command line
    options.
    """

    def __init__(self, usage, name=None, common_args=None):
        script_path = 'unknown' if not sys.argv else sys.argv[0]
        if name is None:
            name = os.path.split(script_path)[-1]
        self.name = name
        self.usage = usage
        self.parser = argparse.ArgumentParser(usage)
        self.api_endpoint = None
        self._add_default_open_tree_arguments(common_args=common_args)
        self.ot_factory = None

    def _add_default_open_tree_arguments(self, common_args=None):

        """Adds several standard command line arguments to the command line parser"""
        cli = self.parser
        cli.add_argument('--version', action='store_true', help='request version information and exit')
        cli.add_argument('--logging-level', default='info', type=str,
                         help='sets the logging level. Should be one of: '
                              '"debug", "info", "warning", "error", or "critical"')
        cli.add_argument('--api-endpoint', default="production",
                         help='Advanced option: specifies which server to contact of api calls.'
                              'choices are "production", "dev", "local", "ot" + # or an IP address.')
        cli.add_argument('--run-mode', default='run', type=str,
                         help='Sets the action to take when interacting with the Open Tree API. '
                              '"run" is the normal mode. '
                              '"curl" will emit a curl call to standard error instead of performing the '
                              'web-service call; this usually causes the script to terminate in an error, but'
                              ' the curl call can be helpful for debugging. "curl-on-exit" will perform the'
                              ' web-service calls, and then write the curl calls used to stderr on exit.')
        if common_args and "ott-ids" in common_args:
            cli.add_argument('--ott-ids', default=None, type=str,
                             help='a comma separated list of OTT ids')
        if common_args and "node-ids" in common_args:
            cli.add_argument('--node-ids', default=None, type=str,
                             help='a comma separated list of node ids')
        if common_args and "ott-id" in common_args:
            cli.add_argument('--ott-id', default=None, type=str,
                             help='An OTT ids (integer or string starting with ott')
        if common_args and "node-id" in common_args:
            cli.add_argument('--node-id', default=None, type=str,
                             help='A node id (starting with "mrca" or "ott)')

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
