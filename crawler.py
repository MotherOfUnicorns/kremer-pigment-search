import requests
import lxml.html
import webbrowser
from tqdm import tqdm

from constants import BASE_URL, CACHE_EXPIRE_AFTER

import requests_cache

requests_cache.install_cache(expire_after=CACHE_EXPIRE_AFTER)


def get_all_pigments(base_url=BASE_URL):

    base_html = requests.get(base_url)
    doc = lxml.html.fromstring(base_html.content)
    pigment_list = doc.xpath('//div[@class="artbox"]/div[@class="inner"]/a')

    all_pigments = []
    for p in tqdm(pigment_list):
        pigment_url = p.get("href")
        pigment_title = p.get("title")
        pigment_order_number = (
            p.text_content().strip().split("\n")[1].split(":")[1].strip()
        )

        pigment_info = {
            "url": pigment_url,
            "title": pigment_title,
            "order_number": pigment_order_number,
        }

        pigment_html = requests.get(pigment_url)
        pigment_info.update(parse_pigment_html(pigment_html))

        all_pigments.append(pigment_info)

    return all_pigments


def parse_pigment_html(pigment_html):
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
    pigment_html = pigment_html.decode("utf-8")

    special_shipping = "Regular shipping, no restrictions." not in pigment_html
    prof_only = "Sold only to professional users" in pigment_html
    danger = "Signal word:" in pigment_html

    return {
        "price": price,
        "mass": mass,
        "html": pigment_html,
        "special_shipping": special_shipping,
        "prof_only": prof_only,
        "danger": danger,
    }


def search_pigment_with_keyword(
    all_pigments,
    keyword,
    open_in_browser=False,
    include_special_shipping=True,
    include_prof_only=False,
    include_danger_warning=False,
    max_price=20,
):
    results = [
        x
        for x in all_pigments
        if keyword.casefold() in x["html"].casefold()
        and (include_special_shipping or not x["special_shipping"])
        and (include_prof_only or not x["prof_only"])
        and (include_danger_warning or not x["danger"])
        and (x["price"] is not None)
        and (x["price"] <= max_price)
    ]

    if open_in_browser:
        for p in results:
            webbrowser.open(p["url"])

    return [(p["title"], p["order_number"], p["price"], p["mass"]) for p in results]
