import json
import datetime
import time

supported_file = open("supported_currencies.json")
rates_file = open("downloaded_rates.json")

supported = json.load(supported_file)
rates = json.load(rates_file)

formatted = {}

code = rates["meta"]["code"]
assert code == 200, f"api code failed with {code}"
epoch = int(time.mktime(time.strptime(rates["response"]["date"], "%Y-%m-%dT%H:%M:%SZ")))
formatted["success"] = True
formatted["timestamp"] = epoch
formatted["date"] = datetime.date.fromtimestamp(epoch).strftime("%Y-%m-%d")
formatted["base"] = rates["response"]["base"]
formatted["rates"] = rates["response"]["rates"]
current_date = datetime.date.today().strftime("%Y-%m-%d")
assert formatted["date"] == current_date
for currency in supported["symbols"]:
    print(f"{currency} {formatted['rates'][currency]}")
as_json = json.dumps(formatted, separators=(",", ":"))
with open("latest_rates.json", "w") as file:
    file.write(as_json)
print("Finished formatting rates!")
