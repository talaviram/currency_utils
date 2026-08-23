# Obtain top currencies from https://en.wikipedia.org/wiki/Template:Most_traded_currencies
import json
import re

import requests as rq
from bs4 import BeautifulSoup


URL = "https://en.wikipedia.org/wiki/Template:Most_traded_currencies"
ISO_CODE = re.compile(r"[A-Z]{3}")
HEADERS = {
    "User-Agent": "currency-utils/1.0 (https://github.com/talaviram/currency_utils)"
}


def get_currency_data():
    response = rq.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    table = next(
        (
            candidate
            for candidate in soup.find_all("table")
            if (caption := candidate.find("caption"))
            and "Most traded currencies by value" in caption.get_text(" ", strip=True)
        ),
        None,
    )
    if table is None:
        raise ValueError("Could not find the most-traded-currencies table")

    currency_dict = {}
    for row in table.select("tbody > tr"):
        cells = row.find_all("td", recursive=False)
        if len(cells) < 2:
            continue

        iso = cells[1].get_text(strip=True)
        if not ISO_CODE.fullmatch(iso):
            continue

        currency_dict[iso] = len(currency_dict) + 1

    if not currency_dict:
        raise ValueError("Could not extract any currency codes from the ranking table")

    return currency_dict


def get_top_currency_codes_as_json():
    currency_data = get_currency_data()
    with open(f"top_currencies.json", "w") as f:
        json.dump(currency_data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    get_top_currency_codes_as_json()
