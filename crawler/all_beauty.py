import hrequests
import json
from parsel import Selector
import re
import html
import os
import base64
import hashlib


def clean_text(text):
    if not text:
        return ""
    
    # If input is a list, clean each item and filter out empty strings
    if isinstance(text, list):
        return [clean_text(item) for item in text if clean_text(item)]

    # Remove inline CSS or unwanted lines at the start (if applicable)
    text = re.sub(r'^[^a-zA-Z0-9]*', '', text)

    # Remove carriage return and newline characters
    text = text.replace('\r', '').replace('\n', ' ').strip()

    # Decode HTML entities like &nbsp;
    text = html.unescape(text)

    # Remove extra spaces
    text = ' '.join(text.split())

    return text



def fetch_page(url):
    print('inside  fetch page')
    response = hrequests.get(url, verify=False)
    
    if not (200 <= response.status_code < 300):
        raise Exception(f"HTTP Error: {response.status_code} for URL: {url}")
    
    print(response.status_code)
    # breakpoint()
    
    with open('response.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    return response.text 
# breakpoint()

def parse_html(response_text):
    print('inside parse_html')
    selector = Selector(response_text)
    description = selector.xpath('(//div[@id="product-description-content-lg-2"]//p//text())').getall()
    rating = selector.xpath("//main[@id='mainContent']/@data-product-star-rating").get()
    # breakpoint()
    clean_description = clean_text(description)

    # breakpoint()
    json_data = selector.xpath("//script[contains(., 'dataLayer')]//text()").get()
    
    match = re.search(r"dataLayer\s*=\s*(\[.*?\]);", json_data, re.DOTALL)
    if match:
        json_like_data = match.group(1)
    else:
        raise ValueError("dataLayer definition not found!")

    # Step 2: Clean up the single quotes and whitespace to make it valid JSON
    json_like_data = json_like_data.replace("'", "\"")

    # Step 3: Convert to JSON object
    try:
        parsed_data = json.loads(json_like_data)
        print("Clean JSON Data")
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
    # breakpoint()
    

    # with open('json_data.json', 'w') as p:
    #     json.dump(parsed_data, p, ensure_ascii=False, indent=4)
    # breakpoint()
    print('hello 1')
    name = parsed_data[0]['pageTitle']
    pageCategory = parsed_data[0]['pageCategory']
    price = parsed_data[0]['productDetails'][0]['productPrice']
    sku = parsed_data[0]['productDetails'][0]['productSKU']
    productStatus = parsed_data[0]['productDetails'][0]['productStatus']
    print('hello 2')
    review_Data=selector.xpath('//script[@id="productSchema"]').get()
    json_string = re.search(r'\{.*\}', review_Data, re.DOTALL).group()
    json_data1 = json.loads(json_string)
    # with open('reviews.json','w')as f:
    #     json.dump(json_data1, f , ensure_ascii=False, indent=4)
    print('hello 3')
    productGroupId = json_data1['productGroupID']
    brand = json_data1['brand']['name']
    mpn = json_data1['hasVariant'][0]['mpn']
    priceCurrency = json_data1['hasVariant'][0]['offers']['priceCurrency']
    itemconditon = json_data1['hasVariant'][0]['offers']['itemCondition']
    availability = json_data1['hasVariant'][0]['offers']['availability']
    image = json_data1['hasVariant'][0]['image']
    print('hello 4')
    reviews = json_data1['review']
    reviews_data = []
    for review in reviews:
        # breakpoint()
        reviewBy =review['author']['name']
        description = review['description']
        datePublished = review['datePublished']
        itemReviewed = review['itemReviewed']['name']
        reviewRating = review['reviewRating']


        review = {
            'reviewby' :reviewBy,
            'description': description,
            'datePublished':datePublished,
            'itemReviewed':itemReviewed,
            'reviewRating':reviewRating,


        }
        reviews_data.append(review)
    print('hello 5')
    all_details ={
        'name':name,
        'brand':brand,
        'pageCategory':pageCategory,
        "productStatus":productStatus,
        ' price' :price ,
        'priceCurrency':priceCurrency,
        ' sku ' :  sku  ,
        'mpn':mpn,
        'itemconditon':itemconditon,
        'availability':availability,
        'image':image,
        "rating":rating,
        'cleaned_description':clean_description,
        'product_reviews ' : reviews_data  ,
        'productGroupId':productGroupId,

        }

    print(f'scraped data:{all_details}')

    return all_details

def generate_filename_from_url(url, extension="json"):
    # Create a hash for a shorter, unique filename
    hash_object = hashlib.md5(url.encode('utf-8'))
    unique_hash = hash_object.hexdigest()
    
    # Optional: Base64 encode for human readability (if needed)
    base64_encoded = base64.urlsafe_b64encode(url.encode('utf-8')).decode('utf-8').rstrip("=")
    
    # Combine base64 and hash for uniqueness and readability
    filename = f"{base64_encoded[:10]}_{unique_hash[:8]}.{extension}"
    
    return filename


def save_to_file(data, url):
    try:
        # Ensure output folder exists
        output_folder = "output"
        os.makedirs(output_folder, exist_ok=True)
        
        # Generate filename
        filename = generate_filename_from_url(url)

        file_path = os.path.join(output_folder, filename)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print(f"File saved at: {file_path}")
    except Exception as e:
        print(f"failed to save: {e}")


def runCrawler(url):
    print('inside main')
    response_data =fetch_page(url)

    html_details =parse_html(response_data)
    print(f'data:{html_details}')
    
    save_to_file(html_details, url)
    return html_details


if __name__ == "__main__":
    print('started process')
    url = 'https://www.allbeauty.com/roberto-cavalli-nero-assoluto-eau-de-parfum/11210313.html?rctxt=default'
    runCrawler(url)