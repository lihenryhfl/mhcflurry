#!/bin/bash

#python -m venv mhcflurry_env
#source ./mhcflurry_env/bin/activate
python -m pip install --upgrade pip setuptools cython pandas
python -m pip install -e .
python -m pip install tensorflow==2.2.0
python -m pip install tensorflow-gpu==2.2.0
python -m pip install biopython simplejson joblib
mhcflurry-downloads fetch
mhcflurry-downloads fetch allele_sequences
mhcflurry-downloads fetch random_peptide_predictions
#python -m pip install ipykernel
#python -m ipykernel install --user --name=mhcflurry_env
