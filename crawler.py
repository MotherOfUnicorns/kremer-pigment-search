import requests
import lxml.html
import webbrowser
from tqdm import tqdm

import requests_cache

requests_cache.install_cache()


base_url = "https://www.kremer-pigmente.com/en/pigments/?f=19&sPage=1&sPerPage=2400"
base_html = requests.get(base_url)
doc = lxml.html.fromstring(base_html.content)

pigment_list = doc.xpath('//div[@class="artbox"]/div[@class="inner"]/a')

all_pigments = []
for p in tqdm(pigment_list):
    pigment_url = p.get("href")
    pigment_title = p.get("title")
    pigment_order_number = p.text_content().strip().split("\n")[1].split(":")[1].strip()

    pigment_html = requests.get(pigment_url)
    pigment_doc = lxml.html.fromstring(pigment_html.content)
    try:
        price = pigment_doc.xpath("//span/strong")[0].text_content().strip()
        price = float(price[1:-2])
    except IndexError:
        price = None
    try:
        mass = (
            pigment_doc.xpath('//div[@class="article_details_price_unit"]/span')[0]
            .text_content()
            .strip()
            .split("\n")[0]
        )
    except IndexError:
        mass = ""

    pigment_html = lxml.html.tostring(pigment_doc.xpath('//div[@id="detail"]')[0])

    regular_shipping = b"Regular shipping, no restrictions." in pigment_html
    danger = (b"Sold only to professional users" in pigment_html) or (
        b"Signal word:" in pigment_html
    )

    all_pigments.append(
        {
            "title": pigment_title,
            "order_number": pigment_order_number,
            "url": pigment_url,
            "html": pigment_html,
            "regular_shipping": regular_shipping,
            "danger": danger,
            "price": price,
            "mass": mass,
        }
    )


def get_pigment_with_keyword(keyword, open_in_browser=False, max_price=20):
    results = [
        (x["title"], x["order_number"], x["price"], x["mass"])
        for x in all_pigments
        if keyword in x["html"] and x["regular_shipping"] and not x["danger"]
        and (x["price"] is not None) and (x["price"] < max_price)
    ]

    if open_in_browser:
        urls = [
            x["url"]
            for x in all_pigments
            if keyword in x["html"] and x["regular_shipping"] and not x["danger"]
        ]
        for url in urls:
            webbrowser.open(url)
    return results
