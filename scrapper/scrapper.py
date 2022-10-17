import json
import requests
from bs4 import BeautifulSoup

local_sales_tax = requests.get("https://www.tax-rates.org/taxtables/local-sales-taxes")
node_sales_tax = requests.get(
    "https://raw.githubusercontent.com/valeriansaliou/node-sales-tax/master/res/sales_tax_rates.json"
)

grabbed_tax = {}

states_to_code = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "District Of Columbia": "DC",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Puerto Rico": "PR",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}


def clean_percent(value):
    percentile_pos = value.find("%")
    if percentile_pos >= 0:
        return float(value[0:percentile_pos])
    else:
        return 0.0


def grab_table(table_id, web_content):
    soup = BeautifulSoup(web_content, "html.parser")
    table_box = soup.find("div", id=table_id)
    return table_box.find("table").find_all("tr")


def grab_state_web(state_url, state_tax):
    print(f"Grabbing state: {state_url}")
    state_page = requests.get(state_url)
    counties = {}
    for row in grab_table("taxBox", state_page.content):
        for row_el in row.find_all("td"):
            county = row_el.find("a")
            tax = row_el.find("div")
            if county and tax:
                counties[county.text] = {
                    "rate": float("%.2f" % (clean_percent(tax.text) - state_tax)),
                    "type": "vat",
                }
    return counties


def grab_us_tax_to_dict():
    grabbed_tax = {}
    for row in grab_table("taxBox", local_sales_tax.content):
        row_content = row.find_all("td")
        for row_el in row_content:
            state = row_el.find("a")
            tax = row_el.find("div")
            if state and tax:
                tax_value = clean_percent(tax.text)
                counties = {
                    "rate": tax_value,
                    "type": "vat",
                    "counties": grab_state_web(state["href"], tax_value),
                }
                grabbed_tax.update({states_to_code[state.text]: counties})
    return grabbed_tax


def grab_node_sales_tax():
    return json.loads(node_sales_tax.content)


def main():
    us_tax_dict = grab_us_tax_to_dict()
    global_tax = grab_node_sales_tax()
    global_tax["US"]["states"] = us_tax_dict
    with open("world_sales_tax.json", "w") as outfile:
        json.dump(global_tax, outfile)
        outfile.close()


if __name__ == "__main__":
    main()
