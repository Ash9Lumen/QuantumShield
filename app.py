import pandas as pd
import requests
import time
import threading
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Lock
phishing_data_lock = Lock()

# Set up logging
logging.basicConfig(filename='app_logs.log', level=logging.INFO, format='%(asctime)s - %(message)s',force=True)

# Example of logging a message
logging.info("Phishing detection service started.")

app = Flask(__name__)
# Disable Flask's default HTTP request logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
CORS(app)

# Define dataset path and OpenPhish feed URL
DATASET_PATH = 'data/phishing_dataset.csv'
OPENPHISH_FEED_URL = 'https://openphish.com/feed.txt'

# Lock to prevent concurrent access to phishing data
phishing_data_lock = Lock()

# Load the initial phishing dataset
phishing_data = pd.read_csv(DATASET_PATH)

def normalize_url(url):
    """Normalize URL by removing trailing slashes and converting to lowercase."""
    return url.rstrip('/').lower()

def is_phishing_url(url):
    """Check if a URL is in the phishing dataset."""
    normalized_url = normalize_url(url)
    phishing_data['normalized_text'] = phishing_data['text'].apply(normalize_url)
    
    # Filter matching URLs and check if any are labeled as phishing
    matching_rows = phishing_data[phishing_data['normalized_text'] == normalized_url]
    
    if not matching_rows.empty:
        return matching_rows['label'].max()  # If mixed, treat it as phishing (label 1)
    return False

def update_phishing_dataset():
    """Fetch real-time phishing URLs from OpenPhish and update the dataset."""
    global phishing_data
    with phishing_data_lock:
        try:
            response = requests.get(OPENPHISH_FEED_URL)
            if response.status_code == 200:
                new_urls = response.text.splitlines()
                existing_urls = phishing_data['text'].tolist()
                
                # Create new entries with normalized_text
                new_entries = [
                    {'text': url, 'label': 1, 'normalized_text': normalize_url(url)}
                    for url in new_urls if url not in existing_urls
                ]
                
                if new_entries:
                    # Append new entries to phishing_data
                    new_df = pd.DataFrame(new_entries)
                    phishing_data = pd.concat([phishing_data, new_df], ignore_index=True)
                    message = f"Added {len(new_entries)} new phishing URLs from OpenPhish."
                else:
                    message = "No new phishing URLs to add."
                
            else:
                message = f"Failed to fetch OpenPhish data. Status code: {response.status_code}"

            # Ensure all rows in phishing_data have normalized_text
            if 'normalized_text' not in phishing_data.columns:
                phishing_data['normalized_text'] = phishing_data['text'].apply(normalize_url)
            else:
                # Fill any missing normalized_text for existing rows
                phishing_data['normalized_text'] = phishing_data.apply(
                    lambda row: normalize_url(row['text']) if pd.isna(row['normalized_text']) or row['normalized_text'] == '' else row['normalized_text'],
                    axis=1
                )

            # Save updated dataset
            phishing_data.to_csv(DATASET_PATH, index=False)
            
        except Exception as e:
            message = f"Error fetching OpenPhish data: {str(e)}"


    # Log message to the file
    logging.info(message)
    return message

def schedule_dataset_update():
    """Continuously update the dataset every 60 minutes."""
    while True:
        update_phishing_dataset()
        time.sleep(3600)  # Update every hour

# Background thread to update the phishing dataset
threading.Thread(target=schedule_dataset_update, daemon=True).start()

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "active"}), 200

@app.route('/analyze', methods=['POST'])
def analyze_url():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Detect phishing using the real-time dataset
    is_phishing = bool(is_phishing_url(url))  # Convert NumPy bool_ to Python bool

    # Log the URL and phishing detection result in a clear format
    logging.info(f"Analyzed URL: {url} | Phishing: {'Yes' if is_phishing else 'No'}")

    # Return the result to the extension
    return jsonify({"url": url, "is_phishing": is_phishing})

if __name__ == '__main__':
    app.run(debug=False)
