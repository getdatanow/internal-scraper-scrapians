import hrequests
from bs4 import BeautifulSoup
import re


def product_details(url):
    print("inside product details")
    details = {}
    # PROXY_URL = "http://:jyabatech-res-US:B4Cq9fnpiMa1hMx"
    session = hrequests.Session(
        proxy="http://jyabatech-res-US:B4Cq9fnpiMa1hMx@gw.ntnt.io:5959"
    )
    r = session.get(url)
    soup = BeautifulSoup(r.text)
    details["title"] = soup.find("title").text
    if len(soup.find("div", id="twisterContainer")) > 0:
        x = (
            soup.find_all("div", id="twisterContainer")[0]
            .find("div", class_="twisterSlotDiv")
            .find("span")
            .find("span")
            .text
        )
        match = re.search(r"\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)", x)
        amount = match.group(1)
        details["price"] = float(amount)
    else:
        details["price"] = None
    details["image_url"] = (
        soup.find("img", id="landingImage")
        .get("data-a-dynamic-image")
        .split('":')[0]
        .replace('{"', "")
    )
    details["product_url"] = url

    p_details = ""
    for tr in soup.find(
        "div", class_="a-section a-spacing-small a-spacing-top-small"
    ).find_all("tr"):

        p_details = (
            p_details
            + tr.find("span", class_="a-size-base a-text-bold").text
            + " : "
            + tr.find("span", class_="a-size-base po-break-word").text
            + "\n"
        )

    details["additional_info"] = p_details

    return details


if __name__ == "__main__":
    product_details("https://www.amazon.com/dp/B086KJBKDW")
    # product_details('https://www.amazon.com/dp/157330056X')
