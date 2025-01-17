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
    response = hrequests.get(url, verify=False)
    
    if not (200 <= response.status_code < 300):
        raise Exception(f"HTTP Error: {response.status_code} for URL: {url}")

    
    with open('response.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    return response.text 

def parse_html(response_text):
    selector = Selector(response_text)
    description = selector.xpath('(//div[@id="product-description-content-lg-2"]//p//text())').getall()
    rating = selector.xpath("//main[@id='mainContent']/@data-product-star-rating").get()

    clean_description = clean_text(description)

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
        print("Clean JSON Data:")
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)

    name = parsed_data[0]['pageTitle']
    pageCategory = parsed_data[0]['pageCategory']
    price = parsed_data[0]['productDetails'][0]['productPrice']
    sku = parsed_data[0]['productDetails'][0]['productSKU']
    productStatus = parsed_data[0]['productDetails'][0]['productStatus']
    match = re.search(r'\/([^\/]+)$', productStatus)

    # If a match is found, extract the group
    if match:
        productStatus = match.group(1)
    else:
        productStatus = productStatus 


    review_Data=selector.xpath('//script[@id="productSchema"]').get()
    json_string = re.search(r'\{.*\}', review_Data, re.DOTALL).group()
    json_data1 = json.loads(json_string)

    productGroupId = json_data1.get('productGroupID',None)
    productname= json_data1['name']
    brand = json_data1['brand']['name']
    mpn = None
    priceCurrency = None
    itemCondition = None
    availability = None
    image = None

    # Check if 'hasVariant' exists and is a non-empty list
    if 'hasVariant' in json_data1 and isinstance(json_data1['hasVariant'], list) and len(json_data1['hasVariant']) > 0:
        variant = json_data1['hasVariant'][0]  # Access the first item in the 'hasVariant' list

        # Extract values if the keys exist
        mpn = variant.get('mpn', None)
        offers = variant.get('offers', {})
        priceCurrency = offers.get('priceCurrency', None)
        itemCondition = offers.get('itemCondition', None)
        match = re.search(r'\/([^\/]+)$',itemCondition)

        # If a match is found, extract the group
        if match:
            itemCondition = match.group(1)
        else:
            itemCondition = itemCondition

        availability = offers.get('availability', None)
        match = re.search(r'\/([^\/]+)$',availability)

        # If a match is found, extract the group
        if match:
            availability = match.group(1)
        else:
            availability = availability
        image = variant.get('image', None)

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

    return {
        'Brand':brand,
        "ProductName":productname,
        "Status":productStatus,
        'Price' :price ,
        'Currency':priceCurrency,
        'SKU' :  sku  ,
        'MPN':mpn,
        'itemconditon':itemCondition,
        'Availability':availability,
        'Image':image,
        "Rating":rating,
        'Description':clean_description,
        'Reviews': reviews_data,
        'productGroupId':productGroupId,
        }


def runCrawler(url):
    response_data =fetch_page(url)

    html_details =parse_html(response_data)

    return html_details


if __name__ == "__main__":
    print('started process')
    url = 'https://www.allbeauty.com/issey-miyake-leau-dissey-pour-homme-intense-eau-de-toilette-spray-75ml/10076091.html'
    runCrawler(url)