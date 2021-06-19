python -m venv mhcflurry_env
source ./mhcflurry_env/bin/activate
python setup.py install --user
pip install tensorflow==2.3.0
pip install tensorflow-gpu==2.3.0
mhcflurry-downloads fetch
mhcflurry-downloads fetch allele_sequences
mhcflurry-downloads fetch random_peptide_predictions
