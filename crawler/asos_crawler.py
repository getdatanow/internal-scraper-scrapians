import hrequests
import json
import logging
from parsel import Selector
import re
import html

def clean_text(text):
    if not text:
        return ""
    
    # If input is a list, clean each item and return the cleaned list
    if isinstance(text, list):
        return [clean_text(item) for item in text]

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
    
    return response.text 

def parse_html(response_text):
    try:
        selector = Selector(response_text)
    except Exception as e:
        print("Failed to create selector:", e)
        return {"error": "Failed to create selector"}

    def safe_xpath(xpath_expr, all_results=False, default=None):
        """Safely extract data using XPath with error handling."""
        try:
            if all_results:
                return selector.xpath(xpath_expr).getall() or default
            return selector.xpath(xpath_expr).get() or default
        except Exception as e:
            print(f"Error parsing XPath '{xpath_expr}':", e)
            return default

    # Extract data with safe parsing
    price = safe_xpath("(//span[@data-testid ='price-screenreader-only-text']//text())[1]", default="N/A")
    product_details = safe_xpath('//div[@class="F_yfF"]//li//text()', all_results=True, default=[])
    brand_details = safe_xpath("//div[@id='productDescriptionBrand']//text()", default="N/A")
    size_fit = safe_xpath("//div[@id='productDescriptionSizeAndFit']//text()", all_results=True, default=[])
    look_after_me = safe_xpath("//div[@id='productDescriptionCareInfo']//text()", default="N/A")
    about_me = safe_xpath("//div[@id='productDescriptionAboutMe']//text()", all_results=True, default=[])
    json_data = safe_xpath("//script[@id ='split-structured-data']//text()", default="{}")

    # Parse JSON data
    try:
        parsed_data = json.loads(json_data)
    except json.JSONDecodeError as e:
        print("Failed to parse JSON:", e)
        parsed_data = {}

    # Safely extract values from parsed JSON
    def safe_json_extract(key, default=None):
        """Safely extract a value from JSON with a fallback."""
        try:
            return parsed_data.get(key, default)
        except Exception as e:
            print(f"Error extracting JSON key '{key}':", e)
            return default

    # Extract product details from JSON
    all_details = {
        'url': safe_json_extract('url', 'N/A'),
        'type': safe_json_extract('@type', 'N/A'),
        'name': safe_json_extract('name', 'N/A'),
        'price': price,
        'product_details': product_details,
        'brand_details': brand_details,
        'size': size_fit,
        'look_after_me': look_after_me,
        'about_me': about_me,
        'sku': safe_json_extract('sku', 'N/A'),
        'color': safe_json_extract('color', 'N/A'),
        'image': safe_json_extract('image', 'N/A'),
        'brand': safe_json_extract('brand', {}).get('name', 'N/A'),
        'description': safe_json_extract('description', 'N/A'),
        'productID': safe_json_extract('productID', 'N/A')
    }

    return all_details


def runCrawler(url):
    response_data =fetch_page(url)

    html_details =parse_html(response_data)

    return html_details
 

# def save_to_file(data, filename):
#     with open(filename, 'w') as f:
#         json.dump(data, f, ensure_ascii=False, indent=4)

# def main():
#     urls = [
#         'https://www.asos.com/mango/mango-zip-through-knitted-jacket-in-white/prd/207101781#colourWayId-207101783',
#         'https://www.asos.com/topshop/topshop-knitted-fluffy-boucle-zip-through-cardigan-in-oat/prd/205987132#ctaref-we%20recommend%20carousel_4&featureref1-we%20recommend%20pers',
#         'https://www.asos.com/topshop/topshop-knitted-textured-crew-cardi-in-ivory/prd/206356511#ctaref-complementary%20items_0&featureref1-complementary%20items',
#         'https://www.asos.com/topshop/topshop-knitted-exposed-seam-crew-cardi-with-pockets-in-cream/prd/205986516#ctaref-we%20recommend%20carousel_13&featureref1-we%20recommend%20pers',
#         'https://www.asos.com/topshop/topshop-knitted-stitch-detail-tank-in-stone/prd/205759072#ctaref-complementary+items_3&featureref1-complementary+items'
#         # Add more URLs as needed
#     ]

#     all_details_list = []

#     for url in urls:
#         print(f"Fetching data for URL: {url}")
#         response_data = fetch_page(url)

#         html_details = parse_html(response_data)
#         all_details_list.append(html_details)

#     save_to_file(all_details_list, "productdetails1.json")
#     print("Data saved to 'productdetails1.json'")

# if __name__ == "__main__":
#     main()