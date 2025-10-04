import collections
import json
import re
import xmltodict
import requests
import iso3166

url = "https://www.six-group.com/dam/download/financial-information/data-center/iso-currrency/lists/list-one.xml"


def get_relevant_alpha2_for_country(country):
    country = country.upper()
    non_country_currencies = [
        "ARAB MONETARY FUND"
        "EUROPEAN UNION",
        "INTERNATIONAL MONETARY FUND (IMF)",
        "MEMBER COUNTRIES OF THE AFRICAN DEVELOPMENT BANK GROUP",
        'SISTEMA UNITARIO DE COMPENSACION REGIONAL DE PAGOS "SUCRE"',
        "ZZ01_BOND MARKETS UNIT EUROPEAN_EURCO",
        "ZZ02_BOND MARKETS UNIT EUROPEAN_EMU-6",
        "ZZ03_BOND MARKETS UNIT EUROPEAN_EUA-9",
        "ZZ04_BOND MARKETS UNIT EUROPEAN_EUA-17",
        "ZZ06_TESTING_CODE",
        "ZZ07_NO_CURRENCY",
        "ZZ08_GOLD",
        "ZZ09_PALLADIUM",
        "ZZ10_PLATINUM",
        "ZZ11_SILVER",
    ]
    if any((country in c) for c in non_country_currencies):
        return None

    # (THE) is special case / there are many ugly cases
    # TODO: maybe clean this with regex :)
    stripped = (
        country.replace("THE ", "").replace("(THE)", "").replace("\u2019", "'")
    )  # workaround the suffix in ISO xml
    firstParenthesis = stripped.find("(")
    if firstParenthesis != -1:
        stripped = (
            stripped[: (firstParenthesis - 1)] + ", " + stripped[firstParenthesis + 1 :]
        )
    stripped = stripped.replace(")", "").strip()
    stripped = re.sub(" +", " ", stripped)
    special_cases = {
        "CONGO, DEMOCRATIC REPUBLIC OF": "CONGO",
        "FALKLAND ISLANDS [MALVINAS]": "FALKLAND ISLANDS (MALVINAS)",
        "COCOS, KEELING ISLANDS": "COCOS (KEELING) ISLANDS",
        "SAINT MARTIN, FRENCH PART": "SAINT MARTIN (FRENCH PART)",
        "SAINT VINCENT AND GRENADINES": "SAINT VINCENT AND THE GRENADINES",
        "SINT MAARTEN, DUTCH PART": "SINT MAARTEN (DUTCH PART)",
        "SOUTH GEORGIA AND SOUTH SANDWICH ISLANDS": "SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS",
        "TÜRKİYE": "TÜRKIYE",
    }
    if stripped in special_cases:
        stripped = special_cases[stripped]
    return iso3166.countries_by_name[stripped].alpha2


def clean_xml(currency_list, last_update):
    cleaned_list = {
        "last_update": last_update,
        "countries": {},
        "state_currencies": {},
        "funds": {},
    }
    key_mapping = {
        "CtryNm": "country_name",
        "CcyNm": "currency_name",
        "Ccy": "iso_code",
        "CcyNbr": "iso_number",
        "CcyMnrUnts": "minor_units",
    }
    for item in currency_list:
        new_dict = collections.OrderedDict()
        for key, value in item.items():
            new_key = key_mapping.get(key, key)
            new_dict[new_key] = value
        possible_symbol = get_relevant_alpha2_for_country(new_dict["country_name"])
        if (
            "@IsFund" in new_dict["currency_name"]
            and new_dict["currency_name"]["@IsFund"] == "true"
            and possible_symbol != None
        ):
            # the XML contains also funded forms
            new_dict["currency_name"] = new_dict["currency_name"]["#text"]
            insert_or_append(new_dict["country_name"], cleaned_list["funds"], new_dict)
        elif possible_symbol == None:
            insert_or_append(
                new_dict["country_name"], cleaned_list["state_currencies"], new_dict
            )
        else:
            insert_or_append(possible_symbol, cleaned_list["countries"], new_dict)
    return cleaned_list


def insert_or_append(country_iso, dict, currency_item):
    if country_iso in dict:
        dict[country_iso].append(currency_item)
    else:
        dict[country_iso] = [currency_item]


def generate_iso4217():
    response = requests.get(url)

    if response.status_code == 200:
        xml_data = response.content
        xml = xmltodict.parse(xml_data, encoding="utf-8")
        dict_iso_4217 = clean_xml(
            xml["ISO_4217"]["CcyTbl"]["CcyNtry"], xml["ISO_4217"]["@Pblshd"]
        )

        filename = "iso4217_currency_codes.json"

        with open(filename, "w") as f:
            json.dump(dict_iso_4217, f, indent=4, ensure_ascii=False)
