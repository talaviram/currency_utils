import json
import datetime

supported_file = open("supported_currencies.json")
rates_file = open("latest_rates.json")

supported = json.load(supported_file)
rates = json.load(rates_file)

assert(rates["success"] == True)
current_date = datetime.date.today().strftime('%Y-%m-%d')
assert(rates["date"] == current_date)

for currency in supported["symbols"]:
    print(f"{currency} {rates['rates'][currency]}")
