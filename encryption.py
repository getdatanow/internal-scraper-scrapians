import hashlib
import base64
import json
import os

# File to store the mappings
MAPPING_FILE = 'url_to_filename_mapping.json'

# Load the mappings from the file if it exists
def load_mappings():
    if os.path.exists(MAPPING_FILE):
        with open(MAPPING_FILE, 'r') as f:
            # Ensure that we load the data as a dictionary, not as a string
            data = json.load(f)
            return data.get('url_to_filename', {}), data.get('filename_to_url', {})
    return {}, {}

# Save the mappings to the file
def save_mappings(url_to_filename, filename_to_url):
    with open(MAPPING_FILE, 'w') as f:
        json.dump({
            'url_to_filename': url_to_filename,
            'filename_to_url': filename_to_url
        }, f)

# Generate the filename from the URL using SHA-256 and Base64 encoding
def generate_filename_from_url(url: str) -> str:
    """Generate a unique filename based on the URL."""
    hash_object = hashlib.sha256(url.encode())
    hash_bytes = hash_object.digest()

    # Encode the hash using Base64 to get a filename-friendly format
    filename = base64.urlsafe_b64encode(hash_bytes).decode('utf-8').rstrip("=")  # Remove trailing "="
    return filename

# Store URL and filename mappings
def store_mapping(url: str, filename: str, url_to_filename, filename_to_url):
    url_to_filename[url] = filename
    filename_to_url[filename] = url

# Retrieve the original URL from the filename
def get_url_from_filename(filename: str, filename_to_url):
    return filename_to_url.get(filename, None)

def main():
    print("Welcome to the URL to Filename system")

    # Load existing mappings if they exist
    url_to_filename, filename_to_url = load_mappings()

    while True:
        action = input("Would you like to (A)dd a URL or (R)etrieve a URL? ").strip().upper()

        if action == 'A':
            url = input("Enter the URL to store: ")
            filename = generate_filename_from_url(url)
            store_mapping(url, filename, url_to_filename, filename_to_url)
            save_mappings(url_to_filename, filename_to_url)
            print(f"Generated Filename: {filename}")

        elif action == 'R':
            filename = input("Enter the filename to retrieve the URL: ")
            url = get_url_from_filename(filename, filename_to_url)
            if url:
                print(f"The original URL is: {url}")
            else:
                print("Filename not found.")
        
        else:
            print("Invalid option. Please select (A) to add a URL or (R) to retrieve a URL.")

if __name__ == "__main__":
    main()
