import json
import requests
import iso4217_currency_codes
from bs4 import BeautifulSoup

state_sales_tax = requests.get("https://www.tax-rates.org/taxtables/sales-tax-by-state")
local_sales_tax = requests.get("https://www.tax-rates.org/taxtables/local-sales-taxes")
node_sales_tax = requests.get(
    "https://raw.githubusercontent.com/valeriansaliou/node-sales-tax/master/res/sales_tax_rates.json"
)

grabbed_tax = {}

states_to_code = {
    "ALABAMA": "AL",
    "ALASKA": "AK",
    "ARIZONA": "AZ",
    "ARKANSAS": "AR",
    "CALIFORNIA": "CA",
    "COLORADO": "CO",
    "CONNECTICUT": "CT",
    "DISTRICT OF COLUMBIA": "DC",
    "DELAWARE": "DE",
    "FLORIDA": "FL",
    "GEORGIA": "GA",
    "HAWAII": "HI",
    "IDAHO": "ID",
    "ILLINOIS": "IL",
    "INDIANA": "IN",
    "IOWA": "IA",
    "KANSAS": "KS",
    "KENTUCKY": "KY",
    "LOUISIANA": "LA",
    "MAINE": "ME",
    "MARYLAND": "MD",
    "MASSACHUSETTS": "MA",
    "MICHIGAN": "MI",
    "MINNESOTA": "MN",
    "MISSISSIPPI": "MS",
    "MISSOURI": "MO",
    "MONTANA": "MT",
    "NEBRASKA": "NE",
    "NEVADA": "NV",
    "NEW HAMPSHIRE": "NH",
    "NEW JERSEY": "NJ",
    "NEW MEXICO": "NM",
    "NEW YORK": "NY",
    "NORTH CAROLINA": "NC",
    "NORTH DAKOTA": "ND",
    "OHIO": "OH",
    "OKLAHOMA": "OK",
    "OREGON": "OR",
    "PENNSYLVANIA": "PA",
    "PUERTO RICO": "PR",
    "RHODE ISLAND": "RI",
    "SOUTH CAROLINA": "SC",
    "SOUTH DAKOTA": "SD",
    "TENNESSEE": "TN",
    "TEXAS": "TX",
    "UTAH": "UT",
    "VERMONT": "VT",
    "VIRGINIA": "VA",
    "WASHINGTON": "WA",
    "WEST VIRGINIA": "WV",
    "WISCONSIN": "WI",
    "WYOMING": "WY",
}


def clean_percent(value):
    percentile_pos = value.find("%")
    if percentile_pos >= 0:
        return float(value[0:percentile_pos]) * 0.01
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
                    "rate": float("%.4f" % (clean_percent(tax.text) - state_tax)),
                    "type": "vat",
                }
    return counties


def grab_us_states_tax():
    states_tax = {}
    for row in grab_table("taxBox", state_sales_tax.content):
        row_content = row.find_all("td")
        for row in row_content:
            state = states_to_code[row.find("a").text.upper()]
            rate = row.find("div").text
            states_tax[state] = clean_percent(rate)
    return states_tax


def grab_us_tax_to_dict():
    grabbed_tax = {}
    states_tax = grab_us_states_tax()
    for row in grab_table("taxBox", local_sales_tax.content):
        row_content = row.find_all("td")
        for row_el in row_content:
            state = row_el.find("a")
            tax = row_el.find("div")
            if state and tax:
                state_code = states_to_code[state.text.upper()]
                tax_value = clean_percent(tax.text)
                counties = {
                    "rate": max(tax_value, states_tax[state_code]),
                    "type": "vat",
                    "counties": grab_state_web(state["href"], tax_value),
                }
                grabbed_tax.update({state_code: counties})
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
    iso4217_currency_codes.generate_iso4217()


if __name__ == "__main__":
    main()
