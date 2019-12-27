#!/usr/bin/env python3
__version__ = "0.0.1"  # sync with setup.py

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

# Default-configured wrapper
OT = OpenTree()
