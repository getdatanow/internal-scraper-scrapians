import uuid
import re
from urllib.parse import urlparse

def generate_file_name(url: str) -> str:
    """Generate a unique, readable filename from a product URL."""
    try:
        parsed_url = urlparse(url)
        domain_parts = parsed_url.netloc.split(':')[0].split('.')
        
        domain = domain_parts[-2] if len(domain_parts) > 2 else domain_parts[0]
        domain = re.sub(r'[^a-zA-Z0-9]', '_', domain)

        unique_id = uuid.uuid4().hex[:12]
        
        return f"{domain}_{unique_id}.txt"
    
    except Exception as e:
        return f"Error in generating filename: {e}"

url = "https://www.example.com/some/path"
print(generate_file_name(url))