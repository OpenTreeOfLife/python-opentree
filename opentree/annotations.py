import os
import sys
import json
import dendropy
import random


from opentree import OT


#Entrez.email = "ejmctavish@ucmerced.edu"



_DEBUG = 1
def debug(msg):
    """short debugging command
    """
    if _DEBUG == 1:
        print(msg)


def generate_random_HEX_color():
    chars = '0123456789ABCDEF'
    color = '#'+''.join(random.sample(chars,6))
    return color

def generate_custom_synth_node_annotation(tree, custom_synth_dir, exclude_sources = None):
    """inputs:
    tree
    Tree in dendropy format. must be labelled with ott_ids, and internal node labels
    outputs:
    dictionary with keys node_labels

    """
    node_annotation = {}
    for node in tree:
        if node.label:
            node_annotation[node.label] = {}
        elif node.taxon:
            if node.taxon.label:
                node_annotation[node.taxon.label] = {}
    node_ids = node_annotation.keys()
    annot = json.load(open("{}/annotated_supertree/annotations.json".format(custom_synth_dir)))
    node_id_resp = annot['nodes']
    if exclude_sources:
        for source in exclude_sources:
            for node in node_id_resp:
                for typ in ['supported_by', 'strict_support','partial_path_of','conflict', 'terminal']:
                    if source in node_id_resp[node].get(typ,{}):
                        del node_id_resp[node][typ][source]
    for node in node_annotation:
        node_info = node_id_resp.get(node,{})
        strict_support = node_info.get('supported_by', {})
        ppo = node_info.get('partial_path_of', {})
        term = node_info.get('terminal', {})
        conflict = node_info.get('conflicts_with', {})
        node_annotation[node]['strict_support'] = len(strict_support.keys())
        gen_support = set(list(strict_support.keys()) + list(ppo.keys())  + list(term.keys()))
        node_annotation[node]['support'] = len(gen_support)
        node_annotation[node]['conflict'] = len(conflict)
    return node_annotation

def generate_custom_synth_source_traversal(tree, custom_synth_dir, source):
    """inputs:
    tree
    Tree in dendropy format. must be labelled with ott_ids, and internal node labels
    outputs:
    dictionary with keys node_labels

    """
    node_annotation = {}
    for node in tree:
        if node.label:
            node_annotation[node.label] = {}
        elif node.taxon:
            if node.taxon.label:
                node_annotation[node.taxon.label] = {}
    node_ids = node_annotation.keys()
    annot = json.load(open("{}/annotated_supertree/annotations.json".format(custom_synth_dir)))
    node_id_resp = annot['nodes']
    for node in node_annotation:
        node_info = node_id_resp.get(node,{})
        strict_support = node_info.get('supported_by', {})
        terminal_of = node_info.get('terminal', {})
        if source in strict_support.keys() or source in terminal_of.keys():
            node_annotation[node]['support'] = 1
        else:
            node_annotation[node]['support'] = 0
        ppo = node_info.get('partial_path_of', {})
        if source in ppo.keys():
            node_annotation[node]['ppo'] = 1
        else:
            node_annotation[node]['ppo'] = 0
        resolves = node_info.get('resolves', {})
        if source in resolves.keys():
            node_annotation[node]['resolves'] = 1
        else:
            node_annotation[node]['resolves'] = 0
        conflict = node_info.get('conflicts_with', {})
        if source in conflict.keys():
            node_annotation[node]['conflict'] = 1
        else:
            node_annotation[node]['conflict'] = 0
    return node_annotation

def generate_synth_node_annotation(tree, current_tax_version = "ott3.3"):
    """inputs:
    tree
    Tree in dendropy format. must be labelled with ott_ids
    outputs:
    dictionary with keys node_labels

    """
    node_annotation = {}
    for node in tree:
        if node.label:
            node_annotation[node.label] = {}
        elif node.taxon:
            if node.taxon.label:
                node_annotation[node.taxon.label] = {}
    for node_label in node_annotation:
        assert node_label.startswith('ott') or node_label.startswith('mrca')
        node_annotation[node_label] = {}
        node_annotation[node_label]['families'] = []
        node_annotation[node_label]['studies'] = []
        node_annotation[node_label]['strict_support'] = []
        node_annotation[node_label]['support'] = []
        node_annotation[node_label]['conflict'] = []
    node_ids = node_annotation.keys()
    resp = OT.synth_node_info(node_ids).response_dict
    node_id_resp = {}
    for node_info in resp:
        node_id_resp[node_info['node_id']] = node_info
    for node in node_annotation:
        supporting = node_id_resp[node].get('source_id_map')
        strict_support = node_id_resp[node].get('supported_by', {})
        ppo = node_id_resp[node].get('partial_path_of', {})
        conflict = node_id_resp[node].get('conflicts_with', {})
        if supporting.keys() == set([current_tax_version]):
            node_annotation[node]['studies'] = 0
        else:
            node_annotation[node]['studies'] = len(supporting.keys())
        if strict_support.keys() == set([current_tax_version]):
            node_annotation[node]['strict_support'] = 0
        else:
            node_annotation[node]['strict_support'] = len(strict_support.keys())
        gen_support = set(list(strict_support.keys()) + list(ppo.keys()))
        if 'ott3.2draft9' in gen_support:
            gen_support.remove(current_tax_version)
        node_annotation[node]['support'] = len(gen_support)
        node_annotation[node]['conflict'] = len(conflict)
    return node_annotation



def get_tips_for_nodes(node_list):
    node_tips = {}
    for node in node_list:
        synth_sub = OT.synth_subtree(node_id=node, label_format="id")
        sub_tips = [leaf.taxon.label for leaf in synth_sub.tree.leaf_node_iter()]
        node_tips[node] = sub_tips
    return(node_tips)
    

def get_ncbi_records(ncbi_id):
    from Bio import Entrez
    handle = Entrez.egquery(retmax=50, term="txid{}[Organism]".format(ncbi_id), idtype="acc")
    gen_record = Entrez.read(handle)
    eq_results = {}
    for db in gen_record['eGQueryResult']:
        try:
            count = int(db['Count'])
            if count > 0:
                eq_results[db['DbName']]=db
        except ValueError:
            pass
    return(eq_results)


def generate_all_tax_dict(taxonomy_file):
    all_tax_dict = {}
    header = ['ottid', 'parent_ottid', 'name','rank','source','uniqname','flags']
    for lin in open(taxonomy_file):
        lii=lin.split('\t|\t')
        all_tax_dict[lii[0]]=dict(zip(header, lii))
    return all_tax_dict


def get_gbif_ncbi_tip_info(ott_id, all_tax_dict):
    from pygbif import occurrences as occ
    """For an ott_id and a dictionary with taxon info, 
    call ncbi and GBIF apis and return mini_dict"""
    tmp_dict = all_tax_dict[ott_id.strip('ott')]
    tmp_dict['ncbi_ids'] = []
    tmp_dict['gbif_ids'] = []   
    tmp_dict['ncbi_eq_results'] = []
    tmp_dict['gbif_records'] = 0
    for source in tmp_dict['source'].split(','):
        if source.startswith('ncbi'):
            ncbi_id = source.split(':')[1]
            tmp_dict['ncbi_ids'].append(ncbi_id)
            eq_results = get_ncbi_records(ncbi_id)
            tmp_dict['ncbi_eq_results'].append(eq_results)
        if source.startswith('gbif'):
            gbif_id = source.split(':')[1]
            tmp_dict['gbif_ids'].append(gbif_id)
            tmp_dict['gbif_records'] += occ.count(taxonKey = gbif_id)
    return tmp_dict    


def generate_gbif_ncbi_node_annotations(nodes, node_tips, tip_dict):
    """Generate an annotations dictionary for a set of nodes.
    nodes_tip = a dictionary with keys that are node_ids listing all the tips descending from that node
    tip_dict = a dcitionary with infomration about each tip"""
    node_annotation = {}
    for nid in nodes:
        node_annotation[nid] = {}
        node_annotation[nid]['tips_counted'] = 0
        node_annotation[nid]['ncbi_ids'] = 0
        node_annotation[nid]['gbif_ids'] = 0
        node_annotation[nid]['genomes'] = 0
        node_annotation[nid]['genbank'] = 0
        node_annotation[nid]['gbif_occ'] = 0
        node_annotation[nid]['has_gbif_dat'] = 0
        node_annotation[nid]['has_gbif_id'] = 0
        node_annotation[nid]['has_nuc_dat'] = 0
        node_annotation[nid]['has_genome_dat'] = 0
        node_annotation[nid]['has_ncbi_id'] = 0
        node_annotation[nid]['total_descendents'] = len(node_tips[nid])
        for tip in node_tips[nid]:
            assert tip in tip_dict
            if tip in tip_dict:
                node_annotation[nid]['tips_counted'] += 1
                node_annotation[nid]['ncbi_ids'] +=len(tip_dict[tip].get('ncbi_ids',[]))
                tip_genomes = sum([int(res.get('genome',{'Count':0})['Count']) for res in tip_dict[tip]['ncbi_eq_results']])
                node_annotation[nid]['genomes'] += tip_genomes
                tip_genbank = sum([int(res.get('nuccore',{'Count':0})['Count']) for res in tip_dict[tip]['ncbi_eq_results']])
                node_annotation[nid]['genbank'] += tip_genbank
                node_annotation[nid]['gbif_occ'] += int(tip_dict[tip]['gbif_records'])
                node_annotation[nid]['gbif_ids'] +=len(tip_dict[tip].get('gbif_ids',[]))
                if len(tip_dict[tip].get('ncbi_ids',[])) >= 1:
                    node_annotation[nid]['has_ncbi_id'] += 1
                if len(tip_dict[tip].get('gbif_ids',[])) >= 1:
                    node_annotation[nid]['has_gbif_id'] += 1
                if int(tip_dict[tip]['gbif_records']) >= 1:
                    node_annotation[nid]['has_gbif_dat'] += 1
                if int(tip_genomes) >= 1:
                    node_annotation[nid]['has_genome_dat'] += 1
                if sum([int(res.get('nuccore',{'Count':0})['Count']) for res in tip_dict[tip]['ncbi_eq_results']]) >= 1:
                    node_annotation[nid]['has_nuc_dat'] +=1
        if node_annotation[nid]['tips_counted'] > 0:
            node_annotation[nid]['has_gbif_dat_perc'] = int((node_annotation[nid]['has_gbif_dat']/node_annotation[nid]['tips_counted'])*100)
            node_annotation[nid]['has_genome_dat_perc'] = float((node_annotation[nid]['has_genome_dat']/float(node_annotation[nid]['tips_counted']))*100)
            node_annotation[nid]['has_nuc_dat_perc'] = int((node_annotation[nid]['has_nuc_dat']/node_annotation[nid]['tips_counted'])*100)
            node_annotation[nid]['has_gbif_id_perc'] = int((node_annotation[nid]['has_gbif_id']/node_annotation[nid]['tips_counted'])*100)
            node_annotation[nid]['has_ncbi_id_perc'] = int((node_annotation[nid]['has_ncbi_id']/node_annotation[nid]['tips_counted'])*100)
        else:
            node_annotation[nid]['has_gbif_dat_perc'] = 0
            node_annotation[nid]['has_nuc_dat_perc'] = 0
            node_annotation[nid]['has_gbif_id_perc'] = 0
            node_annotation[nid]['has_ncbi_id_perc'] = 0
    return(node_annotation)
                

def write_itol_heatmap(filename, title, unit, node_annotation, param):
    """Write out an itol heatmap file to filename, with title and units label.
    annot dict must have keys which are node ids in tree on itol (may require underscore space subs..)
    param should be key of annot_dict[node_ids] = {}"""
    fi = open(filename, 'w')
    startstr = """DATASET_HEATMAP
    #In heatmaps, each ID is associated to multiple numeric values, which are displayed as a set of colored boxes defined by a color gradient
    #lines starting with a hash are comments and ignored during parsing
    #=================================================================#
    #                    MANDATORY SETTINGS                           #
    #=================================================================#
    #select the separator which is used to delimit the data below (TAB,SPACE or COMMA).This separator must be used throughout this file (except in the SEPARATOR line, which uses space).
    #SEPARATOR TAB
    SEPARATOR SPACE
    #SEPARATOR COMMA
    #label is used in the legend table (can be changed later)
    DATASET_LABEL {t}
    #dataset color (can be changed later)
    COLOR #ff0000
    #define labels for each individual field column
    FIELD_LABELS {u}
    #=================================================================#
    #                    OPTIONAL SETTINGS                            #
    #=================================================================#
    #Heatmaps can have an optional Newick formatted tree assigned. Its leaf IDs must exactly match the dataset FIELD_LABELS.
    #The tree will be used to sort the dataset fields, and will be displayed above the dataset. It can have branch lengths defined.
    #All newlines and spaces should be stripped from the tree, and COMMA cannot be used as the dataset separator if a FIELD_TREE is provided.
    #FIELD_TREE (((f1:0.2,f5:0.5):1,(f2:0.2,f3:0.3):1.2):0.5,(f4:0.1,f6:0.5):0.8):1;
    #=================================================================#
    #     all other optional settings can be set or changed later     #
    #           in the web interface (under 'Datasets' tab)           #
    #=================================================================#
    #Each dataset can have a legend, which is defined using LEGEND_XXX fields below
    #For each row in the legend, there should be one shape, color and label.
    #Optionally, you can define an exact legend position using LEGEND_POSITION_X and LEGEND_POSITION_Y. To use automatic legend positioning, do NOT define these values
    #Optionally, shape scaling can be present (LEGEND_SHAPE_SCALES). For each shape, you can define a scaling factor between 0 and 1.
    #Shape should be a number between 1 and 6, or any protein domain shape definition.
    #1: square
    #2: circle
    #3: star
    #4: right pointing triangle
    #5: left pointing triangle
    #6: checkmark
    #LEGEND_TITLE,Dataset legend
    #LEGEND_POSITION_X,100
    #LEGEND_POSITION_Y,100
    #LEGEND_SHAPES,1,2,3
    #LEGEND_COLORS,#ff0000,#00ff00,#0000ff
    #LEGEND_LABELS,value1,value2,value3
    #LEGEND_SHAPE_SCALES,1,1,0.5
    #left margin, used to increase/decrease the spacing to the next dataset. Can be negative, causing datasets to overlap.
    #MARGIN 0
    #width of the individual boxes
    #STRIP_WIDTH 25
    #always show internal values; if set, values associated to internal nodes will be displayed even if these nodes are not collapsed. It could cause overlapping in the dataset display.
    #SHOW_INTERNAL 0
    #show dashed lines between leaf labels and the dataset
    #DASHED_LINES 1
    #if a FIELD_TREE is present, it can be hidden by setting this option to 0
    #SHOW_TREE 1
    #define the color for the NULL values in the dataset. Use the letter X in the data to define the NULL values
    #COLOR_NAN #000000
    #automatically create and display a legend based on the color gradients and values defined below
    #AUTO_LEGEND 1
    #define the heatmap gradient colors. Values in the dataset will be mapped onto the corresponding color gradient.
    COLOR_MIN #0000ff
    COLOR_MAX #ff0000
    #you can specify a gradient with three colors (e.g red to yellow to green) by setting 'USE_MID_COLOR' to 1, and specifying the midpoint color
    #USE_MID_COLOR 1
    #COLOR_MID #ffff00
    #By default, color gradients will be calculated based on dataset values. You can force different values to use in the calculation by setting the values below:
    #USER_MIN_VALUE 0
    #USER_MID_VALUE 500
    #USER_MAX_VALUE 1000
    #border width; if set above 0, a border of specified width (in pixels) will be drawn around individual cells
    #BORDER_WIDTH,0
    #border color; used only when BORDER_WIDTH is above 0
    #BORDER_COLOR,#0000ff
    #Internal tree nodes can be specified using IDs directly, or using the 'last common ancestor' method described in iTOL help pages
    #=================================================================#
    #       Actual data follows after the "DATA" keyword              #
    #=================================================================#
    DATA\n
    """.format(t=title, u=unit)
    fi.write(startstr)
    for node in node_annotation:
        desc = node_annotation[node][param]
        fi.write("{} {}\n".format(node, desc))    
    fi.close()




def write_itol_support(node_annotation, title = "support", max_support=5, filename='support_anno.txt', param='studies'):
    """Write out an itol branch support file to filename, with title and units label.
    annot dict must have keys which are node ids in tree on itol (may require underscore space subs..)
    param should be key of annot_dict[node_ids] = {}"""
    fi = open(filename, 'w')
    startstr = """DATASET_STYLE
    SEPARATOR TAB

    #label is used in the legend table (can be changed later)
    DATASET_LABEL\t{}

    #dataset color (can be changed later)
    COLOR\t#ffff00

    DATA\n""".format(title)
    fi.write(startstr)
    for node in node_annotation:
        if node_annotation[node][param]:
            relsupport = node_annotation[node][param]/max_support
            r = 0
            g = 255*relsupport
            b = 0
            color = "rgba({}, {}, {}, {})".format(r, g, b, 0.25+relsupport)
            fi.write("{}\tbranch\tclade\t{}\t1\tnormal\n".format(node,color))
        else:
            color = "rgba(0, 0, 0, 0.25)"
            fi.write("{}\tbranch\tclade\t{}\t1\tnormal\n".format(node,color))
    fi.close()


def write_itol_conflict(node_annotation, title = "conflict", max_conflict=5, filename='conflict_anno.txt', param='conflict'):
    """Write out an itol branch support file to filename, with title and units label.
    annot dict must have keys which are node ids in tree on itol (may require underscore space subs..)
    param should be key of annot_dict[node_ids] = {}"""
    fi = open(filename, 'w')
    startstr = """DATASET_STYLE
    SEPARATOR TAB

    #label is used in the legend table (can be changed later)
    DATASET_LABEL\t{}

    #dataset color (can be changed later)
    COLOR\t#ffff00

    DATA\n""".format(title)
    fi.write(startstr)
    for node in node_annotation:
        relconf = node_annotation[node][param]/max_conflict
        r = 255*relconf
        g = 0
        b = 0
        color = "rgba({}, {}, {}, {})".format(r, g, b, 0.25+relconf)
        fi.write("{}\tbranch\tclade\t{}\t1\tnormal\n".format(node,color))
            
    fi.close()


def write_itol_relabel(translation_dict, filename):
    """Keys in translation dict should be current labels, values new labels"""
    fi = open(filename, 'w')
    startstr = """LABELS
    #use this template to change the leaf labels, or define/change the internal node names (displayed in mouseover popups)

    #lines starting with a hash are comments and ignored during parsing

    #=================================================================#
    #                    MANDATORY SETTINGS                           #
    #=================================================================#
    #select the separator which is used to delimit the data below (TAB,SPACE or COMMA).This separator must be used throughout this file (except in the SEPARATOR line, which uses space).

    #SEPARATOR TAB
    #SEPARATOR SPACE
    SEPARATOR COMMA

    #Internal tree nodes can be specified using IDs directly, or using the 'last common ancestor' method described in iTOL help pages
    #=================================================================#
    #       Actual data follows after the "DATA" keyword              #
    #=================================================================#
    DATA
    #NODE_ID,LABEL\n"""
    fi.write(startstr)

    for current_label in translation_dict:
        fi.write("{},{}\n".format(current_label, translation_dict[current_label]))
    fi.close()




def write_itol_clades(node_label_dict, filename, font_size=4):
    """Keys in translation dict should be current labels, values new labels"""
    fi = open(filename, 'w')
    startstr = """DATASET_RANGE
    #Colored/labeled range datasets allow the highlighting of various clades or leaf ranges by using colored boxes or brackets.

    #=================================================================#
    #                    MANDATORY SETTINGS                           #
    #=================================================================#
    #select the separator which is used to delimit the data below (TAB,SPACE or COMMA).This separator must be used throughout this file.

    SEPARATOR COMMA

    #label is used in the legend table (can be changed later)
    DATASET_LABEL, Range

    #dataset color in the legend table
    COLOR,#ffff00


    #=================================================================#
    #                    OPTIONAL SETTINGS                            #
    #=================================================================#

    #=================================================================#
    #        all optional settings can be set or changed later        #
    #           in the web interface (under 'Datasets' tab)           #
    #=================================================================#

    #RANGE_TYPE defines how the rages will be visualized:
       #box: standard colored box/polygon. Various LINE_? fields in the range definition will be used for the border style. 
       #bracket: a line or bracket outside the tree

    RANGE_TYPE,box
    #
    #Box/polygon specific options, used when RANGE_TYPE is 'box'
    #

    #specify what the range boxes will cover: 'label','clade' or 'tree'
    RANGE_COVER,clade

    #simplify or smooth polygons when in unrooted display mode: 'none', 'simplify' or 'smooth'
    UNROOTED_SMOOTH,simplify

    #when RANGE_COVER is set to 'clade' or 'tree', you can disable the covering of labels (ie. limiting the boxes to the tree structure only)
    COVER_LABELS,0

    #if set to 1, ranges will cover any displayed extrernal datasets as well
    COVER_DATASETS,0

    #if set to 1, size of the boxes will be extended to fit their labels
    FIT_LABELS,0

    #
    #Bracket specific options, used when RANGE_TYPE is 'bracket'
    #

    #bracket style can be: 'none','square' or 'curved'
    BRACKET_STYLE,square

    #size of the bracket ends (for 'square' or 'curved' brackets)
    BRACKET_SIZE,20

    #shift the bracket position horizontally
    BRACKET_SHIFT,50

    #if set to 1, brackets will be displayed behind the last visible external dataset
    BRACKET_BEHIND_DATASETS,1

    #
    #Options related to range labels
    #

    SHOW_LABELS,1

    #the position of the label in the range box (or relative to the bracket): 'top-left','top-center','top-right',
    #                                                                         'center-left','center-center','center-right',
    #                                                                         'bottom-left','bottom-center','bottom-right'
    LABEL_POSITION,center-center

    #Display the labels vertically. In circular display mode (or with brackets in unrooted display mode), labels will be aligned to the circle
    LABELS_VERTICAL,0

    #labels remain straight, regardless of the tree rotation or other rotation parameters
    STRAIGHT_LABELS,0

    #rotate all labels by the specified angle
    LABEL_ROTATION,0

    #shift all labels horizontally and/or vertically
    LABEL_SHIFT_X,0
    LABEL_SHIFT_Y,0

    #add a colored outline to the label font; useful when displaying labels over similarly colored boxes (e.g. black font on a dark box)
    LABEL_OUTLINE_WIDTH,1
    LABEL_OUTLINE_COLOR,#ffffff

    #multiply the size of all labels by this factor
    LABEL_SIZE_FACTOR,1


    #Each dataset can have a legend, which is defined using LEGEND_XXX fields below
    #For each row in the legend, there should be one shape, color and label.
    #Optionally, you can define an exact legend position using LEGEND_POSITION_X and LEGEND_POSITION_Y. To use automatic legend positioning, do NOT define these values
    #Optionally, shape scaling can be present (LEGEND_SHAPE_SCALES). For each shape, you can define a scaling factor between 0 and 1.
    #To order legend entries horizontally instead of vertically, set LEGEND_HORIZONTAL to 1
    #Shape should be a number between 1 and 6, or any protein domain shape definition.
    #1: square
    #2: circle
    #3: star
    #4: right pointing triangle
    #5: left pointing triangle
    #6: checkmark

    #LEGEND_TITLE,Dataset legend
    #LEGEND_POSITION_X,100
    #LEGEND_POSITION_Y,100
    #LEGEND_HORIZONTAL,0
    #LEGEND_SHAPES,1,4,3
    #LEGEND_COLORS,#ff0000,#00ff00,#0000ff
    #LEGEND_LABELS,value1,value2,value3
    #LEGEND_SHAPE_SCALES,1,1,0.5



    #Internal tree nodes can be specified by using IDs directly, or by using the 'last common ancestor' method described in iTOL help pages
    #=================================================================#
    #       Actual data follows after the "DATA" keyword              #
    #=================================================================#
    #the following fields are available in each line:

    #START_NODE_ID,END_NODE_ID,FILL_COLOR,GRADIENT_COLOR,LINE_COLOR,LINE_STYLE,LINE_WIDTH,LABEL_TEXT,LABEL_COLOR,LABEL_SIZE_FACTOR,LABEL_STYLE

    #The range is defined through START_NODE_ID and END_NODE_ID.
    #If GRADIENT_FILL color is defined, the box will be filled with a gradient from FILL_COLOR to GRADIENT_COLOR.  Brackets will also be visualized as gradients.
    #LINE_COLOR will be used for the box/polygon border, or for the brackets. If not specified, FILL_COLOR will be used instead
    #LINE_STYLE can be 'solid', 'dashed' or 'dotted'
    #LABEL_STYLE can be 'normal', 'bold', 'italic' or 'bold-italic'

    DATA
    #Examples\n"""
    fi.write(startstr)


    for node in node_label_dict:
        color =  generate_random_HEX_color()
        clade_label = node_label_dict[node]
        fi.write("{n},{n},#ffffff,{c},#000000,solid,0,{cl},#000000,{f},bold\n".format(n=node, c=color, f= font_size, cl=clade_label))
    fi.close()