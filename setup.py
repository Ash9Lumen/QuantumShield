# setup.py
import os
from PyInstaller.__main__ import run

# Ensure the output directory exists
if not os.path.exists("dist"):
    os.makedirs("dist")

# Create the command for PyInstaller
opts = [
    'gui.py',  # Use gui.py as the main script
    '--onefile',  # create a single executable
    '--add-data', f"{'data/phishing_dataset.csv'};data",  # add data file
    '--add-data', f"{'popup/popup.html'};popup",  # add popup files
    '--add-data', f"{'popup/styles.css'};popup",
    '--add-data', f"{'popup/popup.js'};popup",
    '--add-data', f"{'background.js'};.",  # add other scripts
    '--add-data', f"{'content.js'};.",  
    '--add-data', f"{'Blocked.html'};.",  
    '--add-data', f"{'manifest.json'};.",  
    '--distpath=dist'  # output directory
]

# Run PyInstaller
run(opts)
