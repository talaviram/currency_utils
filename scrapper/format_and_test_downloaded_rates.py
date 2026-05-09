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
# Workaround: docs specify response.date as ISO 8601 UTC ("2024-03-15T14:30:00Z"),
# but the live API now returns date-only ("2026-05-09"). Revert if the API restores
# the full timestamp.
formatted["success"] = True
formatted["timestamp"] = int(time.time())
formatted["date"] = datetime.datetime.strptime(rates["response"]["date"], "%Y-%m-%d").strftime("%Y-%m-%d")
formatted["base"] = rates["response"]["base"]
formatted["rates"] = rates["response"]["rates"]
current_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
assert formatted["date"] == current_date, f"server date {formatted['date']} != today UTC {current_date}"
for currency in supported["symbols"]:
    print(f"{currency} {formatted['rates'][currency]}")
as_json = json.dumps(formatted, separators=(",", ":"))
with open("latest_rates.json", "w") as file:
    file.write(as_json)
print("Finished formatting rates!")
