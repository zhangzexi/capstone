
#remove old cleaned2.csv
rm -r ./cleaned2.csv

# run cleaning.py
python cleaning.py

# Remove previous model files
rm -r ./model/

# Trigger the trainer
python trainer.py