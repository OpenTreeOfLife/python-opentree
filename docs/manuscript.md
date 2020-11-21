---
title: 'OpenTree: A Python package for accessing and analyzing data from the Open Tree of Life'
tags:
  - Python
  - phylogenetics
  - taxonomy
  - evolution
authors:
  - name: Emily Jane McTavish ^[Custom footnotes for e.g. denoting who the corresspoinding author is can be included like this.]
    orcid: 0000-0001-9766-5727
    affiliation: 1 # (Multiple affiliations must be quoted)
  - name: Luna Luisa Sanchez Reyes
    orcid: 0000-0001-7668-2528
    affiliation: 1
  - name: Mark T. Holder
    orcid: 0000-0001-5575-0536
    affiliation: 2
affiliations:
 - name: University of California, Merced
   index: 1
 - name: University of Kansas
   index: 2
date: 13 August 2017
bibliography: paper.bib


---

# Summary

The Open Tree of Life project constructs a comprehensive, dynamic and digitally-available tree of life by synthesizing published phylogenetic trees along with taxonomic data.
We Open Tree of Life provides web-service APIs to make the tree estimates, unified taxonomy, and input phylogenetic data available to anyone.
`OpenTree` provides a python wrapper for theses APIs and downstream data analysis functionality.


# Statement of need

`OpenTree` is a Python package for accessing and analyzing data from the OpenTree of Life project.
Open Tree of Life stores a wealth of taxonomic and phylogenetic data gathered together in an open-access interoperable framework.
The current synthetic tree [@opentreeoflife_open_2019] comprises 2.4 million tips (largely species).
The framework of this tree is provided by a unified taxonomy [@opentreeoflife_open_2019-1; @rees_automated_2017].
This taxonomy links unique identifiers across many online taxonomic resources, including NCBI [CITE], GBIF [CITE], as well as user contributed taxonomic amendments contained in [https://github.com/OpenTreeOfLife/amendments-1].
These taxonomic relationships are refined by evolutionary estimates from 	1,216 published papers including 87,000 tips taxa [@opentreeoflife_open_2019; @redelings_supertree_2017].
The Open Tree data store, `Phylesystem` [@mctavish_phylesystem:_2015] contains all of those publishes studies, including the mappings between the tips in these published studies, and unique taxonomic identifiers.

All of there data are freely accessible via API calls [https://github.com/OpenTreeOfLife/germinator/wiki/Open-Tree-of-Life-Web-APIs].
`OpenTree` provides an user-friendly wrapper for calling these APIs.
In addition, in converts these between commonly used file formats and data types.
This package allows allows users to generate to data objects in DendroPy, a phylogenetic computing library [@sukumaran_dendropy_2010].


`OpenTree` incorporates in python the functionality available in rotl: an {R} package to interact with the Open Tree of Life data [@michonneau_rotl:_2016], as well as additional downstream analysis and interoperability tools.
`rotl` has been cited 113 times in the 4 years since its publication, demonstrating a demand for accessible user access to these data.
By providing a python package to interact with these data, we make it straightforward for python users to access and analyze these data.
A python wrapper for Open Tree of Life also makes linking these data with the stable of other Python biodiversity informatics tools such as ETC ETC, much easier.



# Figures



Fenced code blocks are rendered with syntax highlighting:
```python
for n in range(10):
    yield f(n)
```

# Acknowledgements

Research was supported by the grant "Sustaining the Open Tree of Life", National Science Foundation ABI No. 1759838, and ABI No. 1759846.
Compute time was provided by the Multi-Environment Research Computer for Exploration and Discovery (MERCED) cluster from the University of California, Merced (UCM), supported by the NSF Grant No. ACI-1429783.


# References



# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.


For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"
