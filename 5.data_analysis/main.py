import pandas
import json
from datetime import date

data = pandas.read_csv("PESSOA_2018.TXT", delimiter=";", nrows=100)
df = pandas.DataFrame(data)

# Load label configuration from json
with open("label.json", encoding="utf-8") as file:
    config = json.load(file)

    # Converts age delimiter to year delimiters based on current year
    year = date.today().year
    config["age_groups"]["delimiters"] = [
        year - age
        for age in config["age_groups"]["delimiters"]
    ][::-1]

    config["age_groups"]["labels"] = config["age_groups"]["labels"][::-1]

    df["DT_NASC_PESSOA"] = pandas.to_datetime(df["DT_NASC_PESSOA"])


