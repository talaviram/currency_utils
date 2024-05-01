# obtain top currencies from https://en.wikipedia.org/wiki/Template:Most_traded_currencies
import datetime
import json
import requests as rq
from bs4 import BeautifulSoup


def get_currency_data():
    url = "https://en.wikipedia.org/wiki/Template:Most_traded_currencies"
    response = rq.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    tbody = soup.find("tbody")
    rows = tbody.find_all("tr")
    currency_dict = {}
    for row in range(2, len(rows) - 2):
        cells = rows[row].find_all("td")
        rank = int(cells[0].text)
        iso = cells[2].text
        currency_dict[iso] = rank
    return currency_dict


def get_top_currency_codes_as_json():
    currency_data = get_currency_data()
    with open(f"top_currencies.json", "w") as f:
        json.dump(currency_data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    get_top_currency_codes_as_json()
