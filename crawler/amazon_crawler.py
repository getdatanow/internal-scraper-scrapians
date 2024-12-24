import httpx
from parsel import Selector

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'cookie': 'session-id=133-1544796-8183716; i18n-prefs=USD; ubid-main=131-5252462-7065838; session-id-time=2082787201l; AMCV_A7493BC75245ACD20A490D4D%40AdobeOrg=1585540135%7CMCIDTS%7C20081%7CMCMID%7C71871717319850907444158611445829920343%7CMCAAMLH-1735540261%7C3%7CMCAAMB-1735540261%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1734942666s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C4.4.0; ld=AZUSSOA-sell; lc-main=en_US; session-token=pIom3EezpQLN6thP8XxPGB+j+PqxMje916OV799iqRsEi3ZO6JZsiCxOlMVXlCOGcz+mOEm8mdEhSV/xOKxFeknyZ1wm+qImIvswBqtvpBvzzuiKX3kZOp4R+7RDmwPagoNrsfliJGv74TXen46FNlM4ZxdBnMDeudKdF9nKEgYuSIA4Yl5x9gKGJls95bkTOaGqnW+p6Mf9wH2iUjKKdTQEtvWdz4U99+LtxL0y6X+Rtqqhnb0ejhDocGsoxoXpa9GtKE5KaKxs5SiJtFIpHHOMCk+Xm5/jqEXa4VfUPI2jZ6oE8ypm7d7rRbAaLJWnYdTOxrNx7ZrF67C3YmP0jTlkWyyGkQBd; csm-hit=tb:s-CTT5CX29GSH8ZNZPZ121|1735019896308&t:1735019899459&adb:adblk_no',
    'device-memory': '8',
    'downlink': '10',
    'dpr': '1',
    'ect': '4g',
    'priority': 'u=0, i',
    'rtt': '150',
    'sec-ch-device-memory': '8',
    'sec-ch-dpr': '1',
    'sec-ch-ua': '"Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-ch-viewport-width': '1300',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'viewport-width': '1300',
}

PROXY_URL = "http://jyabatech-res-US:B4Cq9fnpiMa1hMx@gw.ntnt.io:5959"

# Use httpx for the request
def amazon_product_scraper(url):
    with httpx.Client(proxies={"http://": PROXY_URL, "https://": PROXY_URL}) as client:
        details={}
        respons = client.get(url=url,headers=headers)

        # Debugging the response
        response=Selector(respons.text)
        details["url"]=url
        details["title"]=response.xpath('//title/text()').get()
        details["price"]=response.xpath('//span[contains(@class,"a-price a-text-price")]/span[contains(@aria-hidden,"true")]/text()').get()
        details["image"]=response.xpath('//img[contains(@id,"landingImage")]/@data-a-dynamic-image').get().split('":')[0].replace('{"','')
        p_details=''
        for tr in response.xpath('//div[contains(@class,"a-section a-spacing-small a-spacing-top-small")]//tr'):
            p_details=p_details+tr.xpath('.//span[contains(@class,"a-size-base a-text-bold")]/text()').get()+' : '+tr.xpath('.//span[contains(@class,"a-size-base po-break-word")]/text()').get()+'\n'
        return details

det=amazon_product_scraper('https://www.amazon.com/dp/B004EDYQX6/')
print(det)