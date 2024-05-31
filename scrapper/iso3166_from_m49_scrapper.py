# Obtain ISO3166 2/3 iso codes based on UN data.
import json
import requests as rq
from bs4 import BeautifulSoup

def get_countries_data():
    url = "https://unstats.un.org/unsd/methodology/m49/overview/"
    response = rq.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    core_table = soup.find(id="downloadTableEN").find("tbody")
    arTable = soup.find(id="downloadTableAR").find("tbody").find_all("tr")
    esTable = soup.find(id="downloadTableES").find("tbody").find_all("tr")
    frTable = soup.find(id="downloadTableFR").find("tbody").find_all("tr")
    ruTable = soup.find(id="downloadTableRU").find("tbody").find_all("tr")
    zhTable = soup.find(id="downloadTableZH").find("tbody").find_all("tr")
    rows = core_table.find_all("tr")
    country_dict = {}
    for row in range(len(rows)):
        cells = rows[row].find_all("td")
        name = cells[8].text
        iso_alpha2 = cells[10].text
        iso_alpha3 = cells[11].text
        region_code = cells[2].text
        region_sub_code = cells[4].text
        intermediate_region_code = cells[6].text
        country_dict[iso_alpha2] = {
            "name": name.strip(),
            "name_ar": arTable[row].find_all("td", limit=9)[8].text.strip(),
            "name_es": esTable[row].find_all("td", limit=9)[8].text.strip(),
            "name_fr": frTable[row].find_all("td", limit=9)[8].text.strip(),
            "name_ru": ruTable[row].find_all("td", limit=9)[8].text.strip(),
            "name_zh": zhTable[row].find_all("td", limit=9)[8].text.strip(),
            "iso_alpha2": iso_alpha2,
            "iso_alpha3": iso_alpha3,
            "un_m49": int(cells[9].text),
        }
        if region_code != "":
            country_dict[iso_alpha2]["region_code"] = int(region_code)
            country_dict[iso_alpha2]["region"] = cells[3].text
        if intermediate_region_code != "":
            country_dict[iso_alpha2]["intermediate_region_code"] = int(
                intermediate_region_code
            )
            country_dict[iso_alpha2]["intermediate_region"] = cells[7].text
        if region_sub_code != "":
            country_dict[iso_alpha2]["region_sub_code"] = int(region_sub_code)
            country_dict[iso_alpha2]["region_sub"] = cells[5].text
    return country_dict


def get_countries_iso_json():
    country_data = get_countries_data()
    with open(f"countries_iso3166_m49.json", "w") as f:
        json.dump(country_data, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    get_countries_iso_json()
