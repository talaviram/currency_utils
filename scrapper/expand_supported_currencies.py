import json
import datetime

supported_file = open("supported_currencies.json")
supported = json.load(supported_file)

expanded = supported

for currency in supported["symbols"]:
    expanded["symbols"][currency] = {"code": currency, "description": supported["symbols"][currency]}

with open("symbols.json", "w") as f:
    json.dump(expanded, f, indent=4, ensure_ascii=False)
