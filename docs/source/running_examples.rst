Example scripts
===============
`opentree` comes packaged with a set of example scripts, wrapping common function calls.

These wrap most of the the API calls described in https://github.com/OpenTreeOfLife/germinator/wiki/Open-Tree-of-Life-Web-APIs,
and current API documentation is stored there.


About
-----
An about call returns the current version of the OpenTree synthetic tree and taxonomy::

    python examples/about.py

Response::

    taxonomy_about
    {
      "author": "open tree of life project",
      "name": "ott",
      "source": "ott3.2draft9",
      "version": "3.2",
      "weburl": "https://tree.opentreeoflife.org/about/taxonomy-version/ott3.2"
    }

    synth_tree_about
    {
      "date_created": "2019-12-23 11:41:23",
      "filtered_flags": [
        "major_rank_conflict",
        "major_rank_conflict_inherited",
        "environmental",
        "viral",
        "barren",
        "not_otu",
        "hidden",
        "was_container",
        "inconsistent",
        "hybrid",
        "merged"
      ],
      "num_source_studies": 1162,
      "num_source_trees": 1216,
      "root": {
        "node_id": "ott93302",
        "num_tips": 2391916,
        "taxon": {
          "name": "cellular organisms",
          "ott_id": 93302,
          "rank": "no rank",
          "tax_sources": [
            "ncbi:131567"
          ],
          "unique_name": "cellular organisms"
        }
      },
      "synth_id": "opentree12.3",
      "taxonomy_version": "3.2draft9"
    }


Studies calls
-------------

study_properties
~~~~~~~~~~~~~~~~
Get all searchable properties for trees and studies::

    python examples/study_properties.py



Find studies
~~~~~~~~~~~~

Search studies by property. 
Property can mb any of the above listed 'study properties', but the most common study search properties are:
    "ot:studyPublicationReference",
    "ot:focalCladeOTTTaxonName",
    "ot:curatorName",
The default response just returns the study ID, adding the --verbose flag retuns the full publication references.



To find studies published in the journal Copeia::

    python examples/find_studies.py --property "ot:studyPublicationReference" Copeia --verbose

Property can be any of the above listed 'study properties', but the most common study search properties are:
    "ot:studyPublicationReference",
    "ot:focalCladeOTTTaxonName",
    "ot:curatorName",




Response::

    "matched_studies": [
    {
      "ot:curatorName": [
        "Matt Girard"
      ],
      "ot:dataDeposit": "",
      "ot:focalClade": 814725,
      "ot:focalCladeOTTTaxonName": "Etheostoma",
      "ot:studyId": "ot_1930",
      "ot:studyPublication": "http://dx.doi.org/10.1643/ci-18-054",
      "ot:studyPublicationReference": "Matthews, William J., and Thomas F. Turner. \u201cRedescription and Recognition of Etheostoma Cyanorum from Blue River, Oklahoma.\u201d Copeia 107, no. 2 (April 11, 2019): 208. doi:10.1643/ci-18-054.",
      "ot:studyYear": 2019,
      "ot:tag": []
    },
    ... cut off for length

Find trees
~~~~~~~~~~

Search tress by property
Property can be any of the above listed 'tree properties', but the most common tree search properties are:


        "ot:branchLengthTimeUnit",
        "ot:inGroupClade",
        "ot:ottTaxonName",
        "ot:branchLengthDescription",
        "ntips",
        "ot:ottId",
        "ot:branchLengthMode",
    

To find trees that contain lemurs::

    python examples/find_trees.py --property ot:ottTaxonName Lemur

or to avoid spelling or typographical errors, you can use the ott id for lemurs, 913932 https://tree.opentreeoflife.org/taxonomy/browse?id=913932::

    python examples/find_trees.py --property ot:ottId 913932


Get study
~~~~~~~~~

Get the full study as nexson from study id::

    python examples/get_study.py pg_2067


Get tree
~~~~~~~~

Get a tree from a study in Newick or Nexus format

For example, to get one of the lemur trees found above::

    python examples/get_tree.py pg_2067 tree4259 --format newick


Taxonomy
--------


TNRS
~~~~
To get the taxonomic identifiers for a name::

    python examples/tnrs_match_names.py Lemur


if you think you may have typos, add --do-approximate-matching::

    python examples/tnrs_match_names.py Lemun --do-approximate-matching


To combine a genus and species, use quotation marks::

    python examples/tnrs_match_names.py "Bos taurus"

Approximate name matching can be sped up by restricting the 'context' for the searches
You can find out the possible contexts using::

    python examples/tnrs_contexts.py 


and then applying them::

    python examples/tnrs_match_names.py Lemun --do-approximate-matching --context Mammals



Taxon information
~~~~~~~~~~~~~~~~~

To get more information for taxon which you have the ott id for::

    python examples/taxon_info.py --ott-id 913932


Or the taxonomic subtree descending from a node::

    python examples/taxon_info.py --ott-id 913932


Taxon mrca
~~~~~~~~~~

To get the most recent common ancestor in the taxonomy for multiple taxa e.g. humans (ott:770309) and lemurs (ott:913932)(may differ from synth tree mrca)::

    python examples/taxon_mrca.py --ott-ids 770309,913932

You can pass in the ottids with or without 'ott' e.g. 'ott770309,ott913932', but there cannot be a space between taxa.


Synthetic tree
--------------

To get the most recent common ancestor in the synthetic tree for multiple taxa e.g. humans (ott:770309) and lemurs (ott:913932)::

Synth mrca
~~~~~~~~~~

    python examples/synth_mrca.py --ott-ids 770309,913932


Response::
    {
  "mrca": {
    "node_id": "mrcaott786ott3428",
    "num_tips": 743,
    "partial_path_of": {
      "ot_1366@Tr98763": "Tn14487470",
      "ot_722@tree1": "node47",
      "pg_1428@tree2855": "node610302",
      "pg_2812@tree6545": "node1135880"
    },
    "supported_by": {
      "pg_2647@tree6169": "node1053665",
      "pg_2741@tree6645": "node1159651"
    },
    "terminal": {
      "ot_508@tree2": "ott83926",
      "pg_2822@tree6569": "ott83926"
    }
  },
  "nearest_taxon": {
    "name": "Primates",
    "ott_id": 913935,
    "rank": "order",
    "tax_sources": [
      "ncbi:9443",
      "gbif:798",
      "irmng:11338"
    ],
    "unique_name": "Primates"
  },
  "source_id_map": {
    "ot_1366@Tr98763": {
      "git_sha": "3008105691283414a18a6c8a728263b2aa8e7960",
      "study_id": "ot_1366",
      "tree_id": "Tr98763"
    },
    "ot_508@tree2": {
      "git_sha": "3008105691283414a18a6c8a728263b2aa8e7960",
      "study_id": "ot_508",
      "tree_id": "tree2"
    },
    "ot_722@tree1": {
      "git_sha": "3008105691283414a18a6c8a728263b2aa8e7960",
      "study_id": "ot_722",
      "tree_id": "tree1"
    },
    "pg_1428@tree2855": {
      "git_sha": "3008105691283414a18a6c8a728263b2aa8e7960",
      "study_id": "pg_1428",
      "tree_id": "tree2855"
    },
    "pg_2647@tree6169": {
      "git_sha": "3008105691283414a18a6c8a728263b2aa8e7960",
      "study_id": "pg_2647",
      "tree_id": "tree6169"
    },
    "pg_2741@tree6645": {
      "git_sha": "3008105691283414a18a6c8a728263b2aa8e7960",
      "study_id": "pg_2741",
      "tree_id": "tree6645"
    },
    "pg_2812@tree6545": {
      "git_sha": "3008105691283414a18a6c8a728263b2aa8e7960",
      "study_id": "pg_2812",
      "tree_id": "tree6545"
    },
    "pg_2822@tree6569": {
      "git_sha": "3008105691283414a18a6c8a728263b2aa8e7960",
      "study_id": "pg_2822",
      "tree_id": "tree6569"
    }
  },
  "synth_id": "opentree12.3"
  }


Synth subtree
~~~~~~~~~~~~~

To get the full subtree descending from a node in the the synthetic tree::

    python examples/synth_subtree.py --ott-id 913932 --outfile tmp.txt

By default this will write the tree to screen as an ascii plot, and write the newick to the file location
listed in outfile::


    python examples/synth_subtree.py --ott-id 913932 --outfile tmp.txt

You can specify the label format out the output tree using `--label-format` with options [id, name, name_and_id]::

    python examples/synth_subtree.py --ott-id 913932 --label-format name --outfile tmp.txt


Synth induced subtree
~~~~~~~~~~~~~~~~~~~~~


To get the relationships among cows (Bos taurus ott490099), camels (Camelus dromedarius ott510752), and whales (Orcinus orca ott124215)
By default this will write the tree to screen as an ascii plot, and write the newick to the file location
listed in outfile::
   
   python examples/synth_induced_subtree.py --ott-ids ott490099,ott510752,ott124215 --outfile tmp.nwk

Synth node info
~~~~~~~~~~~~~~~

All nodes in the syntehtic tree are supported by published studies, taxonomy, or both.

To get more information the studies that are resolving a node in the syntehtic tree, 
you can get node information::

    python examples/synth_node_info.py --node-id mrcaott354607ott374748


Response::
    {
  "node_id": "mrcaott354607ott374748",
  "num_tips": 21,
  "query": "mrcaott354607ott374748",
  "resolves": {
    "pg_2812@tree6545": "node1135857"
  },
  "source_id_map": {
    "ot_1344@Tr105486": {
      "git_sha": "3008105691283414a18a6c8a728263b2aa8e7960",
      "study_id": "ot_1344",
      "tree_id": "Tr105486"
    },
    "pg_1217@tree2455": {
      "git_sha": "3008105691283414a18a6c8a728263b2aa8e7960",
      "study_id": "pg_1217",
      "tree_id": "tree2455"
    },
    "pg_1428@tree2855": {
      "git_sha": "3008105691283414a18a6c8a728263b2aa8e7960",
      "study_id": "pg_1428",
      "tree_id": "tree2855"
    },
    "pg_2647@tree6169": {
      "git_sha": "3008105691283414a18a6c8a728263b2aa8e7960",
      "study_id": "pg_2647",
      "tree_id": "tree6169"
    },
    "pg_2812@tree6545": {
      "git_sha": "3008105691283414a18a6c8a728263b2aa8e7960",
      "study_id": "pg_2812",
      "tree_id": "tree6545"
    }
  },
  "supported_by": {
    "ot_1344@Tr105486": "Tn16531763"
  },
  "synth_id": "opentree12.3",
  "terminal": {
    "pg_1217@tree2455": "node566205",
    "pg_1428@tree2855": "node610191",
    "pg_2647@tree6169": "node1053583"
  }
  }


Diagnosing subproblem solutions
-------------------------------

To dig deeper into how different trees included in synthesis support or conflict with nodes in the inferred synthetic tree, 
you can examine what trees support and conflict with a given node's resolution, and experiment with alternate tree rankings.


For example, Drosophila (ott34907) is not found in the synthetic tree. Why not:??

    python examples/diagnose_solution_for --ott-id 34907

You can then interactively view the subproblems. The subproblem synthesis algorithm described in depth in Redelings and Holder 2017 (https://peerj.com/articles/3058/).