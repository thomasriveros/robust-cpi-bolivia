import requests
import os
import re
from datetime import datetime

# Configuration
KETAL_GITHUB_API_URL = "https://api.github.com/repos/mauforonda/precios/contents/data/ketal"
KETAL_RAW_DATA_DIR = "data/raw"

FIDALGA_GITHUB_API_URL = "https://api.github.com/repos/mauforonda/precios/contents/data/fidalga/precios"
FIDALGA_RAW_DATA_DIR = "data/fidalga"

HIPERMAXI_GITHUB_API_URL = "https://api.github.com/repos/mauforonda/precios/contents/data/hipermaxi/la_paz"
HIPERMAXI_RAW_DATA_DIR = "data/hipermaxi"

def fetch_latest_file(repo_url=KETAL_GITHUB_API_URL, output_dir=KETAL_RAW_DATA_DIR):
    """
    Fetches the list of files from the GitHub repository, identifies the latest CSV,
    and downloads it if it's not already present.
    """
    try:
        response = requests.get(repo_url)
        response.raise_for_status()
        files = response.json()
        
        # Filter for CSV files
        # Files are named like YYYY_MM.csv (e.g., 2021_11.csv)
        # We also want to exclude non-dated files like 'productos.csv'
        csv_files = [f for f in files if f['name'].endswith('.csv') and f['name'][0].isdigit()]
        
        if not csv_files:
            print(f"No CSV files found in the repository {repo_url}.")
            return None

        # Sort by name (assuming name contains date like ketal_YYYY-MM-DD.csv) or just trust alphabetical for ISO dates
        # Ketal filenames seem to be dates or contain dates? 
        # User prompt said: https://github.com/mauforonda/precios/tree/master/data/ketal
        # Let's inspect the naming convention. Usually ISO 8601 sorts alphabetically correctly.
        csv_files.sort(key=lambda x: x['name'], reverse=True)
        
        latest_file = csv_files[0]
        download_url = latest_file['download_url']
        filename = latest_file['name']
        local_path = os.path.join(output_dir, filename)

        if os.path.exists(local_path):
            print(f"Latest file {filename} already exists locally.")
            return local_path

        print(f"Downloading {filename}...")
        file_content = requests.get(download_url).content
        
        os.makedirs(output_dir, exist_ok=True)
        with open(local_path, 'wb') as f:
            f.write(file_content)
            
        print(f"Successfully downloaded to {local_path}")
        return local_path

    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def fetch_all_files(repo_url=KETAL_GITHUB_API_URL, output_dir=KETAL_RAW_DATA_DIR):
    """
    Fetches ALL CSV files from the GitHub repository and downloads them if not present.
    Returns a list of local file paths sorted chronologically (ascending).
    """
    try:
        response = requests.get(repo_url)
        response.raise_for_status()
        files = response.json()
        
        # Filter for CSV files (YYYY_MM.csv)
        csv_files = [f for f in files if f['name'].endswith('.csv') and f['name'][0].isdigit()]
        
        if not csv_files:
            print(f"No CSV files found in {repo_url}.")
            return []

        # Sort ASCENDING for historical playback
        csv_files.sort(key=lambda x: x['name']) 
        
        local_paths = []
        os.makedirs(output_dir, exist_ok=True)
        
        for i, file_info in enumerate(csv_files):
            download_url = file_info['download_url']
            filename = file_info['name']
            local_path = os.path.join(output_dir, filename)

            is_last_file = (i == len(csv_files) - 1)

            if is_last_file or not os.path.exists(local_path):
                print(f"Downloading {filename}...")
                content = requests.get(download_url).content
                with open(local_path, 'wb') as f:
                    f.write(content)
            
            local_paths.append(local_path)
            
        return local_paths

    except Exception as e:
        print(f"Error fetching all data: {e}")
        # Fallback to local files if API fails
        if os.path.exists(output_dir):
            local_files = [f for f in os.listdir(output_dir) if f.endswith('.csv') and f[0].isdigit()]
            local_files.sort()
            if local_files:
                print(f"Falling back to {len(local_files)} local files in {output_dir}")
                return [os.path.join(output_dir, f) for f in local_files]
        return []

if __name__ == "__main__":
    fetch_all_files()
