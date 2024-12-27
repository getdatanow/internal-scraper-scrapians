import httpx
from parsel import Selector

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "session-id=133-1544796-8183716; i18n-prefs=USD; ubid-main=131-5252462-7065838; session-id-time=2082787201l; AMCV_A7493BC75245ACD20A490D4D%40AdobeOrg=1585540135%7CMCIDTS%7C20081%7CMCMID%7C71871717319850907444158611445829920343%7CMCAAMLH-1735540261%7C3%7CMCAAMB-1735540261%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1734942666s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.4.0; ld=AZUSSOA-sell; lc-main=en_US; session-token=pIom3EezpQLN6thP8XxPGB+j+PqxMje916OV799iqRsEi3ZO6JZsiCxOlMVXlCOGcz+mOEm8mdEhSV/xOKxFeknyZ1wm+qImIvswBqtvpBvzzuiKX3kZOp4R+7RDmwPagoNrsfliJGv74TXen46FNlM4ZxdBnMDeudKdF9nKEgYuSIA4Yl5x9gKGJls95bkTOaGqnW+p6Mf9wH2iUjKKdTQEtvWdz4U99+LtxL0y6X+Rtqqhnb0ejhDocGsoxoXpa9GtKE5KaKxs5SiJtFIpHHOMCk+Xm5/jqEXa4VfUPI2jZ6oE8ypm7d7rRbAaLJWnYdTOxrNx7ZrF67C3YmP0jTlkWyyGkQBd; csm-hit=tb:s-CTT5CX29GSH8ZNZPZ121|1735019896308&t:1735019899459&adb:adblk_no",
    "device-memory": "8",
    "downlink": "10",
    "dpr": "1",
    "ect": "4g",
    "priority": "u=0, i",
    "rtt": "150",
    "sec-ch-device-memory": "8",
    "sec-ch-dpr": "1",
    "sec-ch-ua": '"Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-ch-viewport-width": "1300",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "viewport-width": "1300",
}

PROXY_URL = "http://jyabatech-res-US:B4Cq9fnpiMa1hMx@gw.ntnt.io:5959"
RETRY_TIMES = 5


# Use httpx for the request
def product_details(url):
    details = {}
    for attempt in range(RETRY_TIMES):
        try:
            with httpx.Client(
                proxy=PROXY_URL,
            ) as client:
                # with httpx.Client() as client:
                response = client.get(url=url, headers=headers, timeout=10)

                if response.status_code == 200:
                    selector = Selector(response.text)
                    details["product_url"] = url
                    details["title"] = selector.xpath("//title/text()").get()
                    details["price"] = selector.xpath(
                        '//span[contains(@class,"a-price a-text-price")]/span[contains(@aria-hidden,"true")]/text()'
                    ).get().replace('$'," ")
                    details["image_url"] = (
                        selector.xpath(
                            '//img[contains(@id,"landingImage")]/@data-a-dynamic-image'
                        )
                        .get()
                        .split('":')[0]
                        .replace('{"', "")
                    )

                    p_details = ""
                    for tr in selector.xpath(
                        '//div[contains(@class,"a-section a-spacing-small a-spacing-top-small")]//tr'
                    ):
                        key = tr.xpath(
                            './/span[contains(@class,"a-size-base a-text-bold")]/text()'
                        ).get()
                        value = tr.xpath(
                            './/span[contains(@class,"a-size-base po-break-word")]/text()'
                        ).get()
                        if key and value:
                            p_details += f"{key} : {value}\n"
                    details["product_details"] = p_details
                    return details
                else:
                    print(
                        f"Attempt {attempt + 1} failed with status code {response.status_code}"
                    )

        except httpx.RequestError as e:
            print(f"Attempt {attempt + 1} failed: {e}")


# print(product_details("https://www.amazon.com/dp/157583572X"))