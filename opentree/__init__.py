#!/usr/bin/env python3
__version__ = "1.0.1"  # sync with setup.py

from .object_conversion import get_object_converter
from .ws_wrapper import (OTWebServicesError,
                         OTClientError,
                         WebServiceRunMode,
                         WebServiceWrapper,
                         )
from .ot_ws_wrapper import OTWebServiceWrapper
from .ot_command_line_tool import (OTCommandLineTool,
                                   process_ott_and_node_id_list_args,
                                   process_ott_or_node_id_arg)
from .ot_object import OpenTree
from .util import (get_suppressed_taxon_flag_expl_url,
                   ott_str_as_int,
                   write_node_info_links_to_input_trees)

# Default-configured wrapper
OT = OpenTree()
