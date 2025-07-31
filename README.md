# Instructions

## Downloads 

Dowload the above files as a zip, making sure to place them all in the same directory. 

Ensure that the model files directory remains intact and is placed in the same directory as the raw python files.

## Install Necessary Packages

In your terminal, create a virtual environment and run...

```bash
pip install pandas python-libsbml gamspy
```

## Running The Model

Set your current directory to the folder where you placed all of the files from the .zip.

Run main.py in your favorite python environment.

The treatment option available when you run the model will set different reaction constraints depending on what additive molecule is simulated as being added to the model. In order to run the model without simulating a treatment, press 0.

# Acknowledgements

The Cowmunity Model was developed by Evan Ingmire in collaboration with Mohammed Reza Zargar, Dr. Karuna Anna Sajeevan, and Dr. Ratul Chowdhury at Iowa State University.

The OptCom model was originally developed by Zomorrodi and Maranas. 

Zomorrodi, A.R. and C.D. Maranas (2012), "[OptCom: A multi-level optimization framework for the metabolic modeling and analysis of microbial communities](https://www.maranasgroup.com/pub/2012/OptCom_2012.pdf)," PLoS Computational Biology, 8(2):e1002363. PMID: [22319433](http://www.ncbi.nlm.nih.gov/pubmed/22319433).

The SBML Models attached to this repository were originally developed by Islam et al.

Islam MM, Fernando SC and Saha R (2019), "Metabolic Modeling Elucidates the Transactions in the Rumen Microbiome and the Shifts Upon Virome Interactions," Front. Microbiol. 10:2412. doi: [10.3389/fmicb.2019.02412](https://doi.org/10.3389/fmicb.2019.02412).
