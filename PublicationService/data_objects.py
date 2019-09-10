from mongoengine import StringField, IntField, FloatField, Document, \
    EmbeddedDocument, ListField, EmbeddedDocumentField, connect
import pandas as pd
import json

ENERGY_CATEGORIES = {
    "Electricity - Gross production": "total_energy",
    "From combustible fuels – Main activity": "combustibles",
    "Geothermal – Main activity": "geothermal",
    "Hydro – Main activity": "hydro",
    "Nuclear – Main activity": "nuclear",
    "From other sources – Main activity": "other",
    "Solar – Main activity": "solar",
    "Wind – Main activity": "wind",
    "From combustible fuels – Autoproducer": "combustibles",
    "Geothermal – Autoproducer": "geothermal",
    "Hydro – Autoproducer": "hydro",
    "Nuclear - Autoproducer": "nuclear",
    "From other sources – Autoproducer": "other",
    "Solar – Autoproducer": "solar",
    "Wind – Autoproducer": "wind",
}


class EnergyMix(Document):
    country = StringField(required=True)
    year = IntField(required=True)
    total_energy = FloatField(required=True)
    combustibles = FloatField(required=False)
    geothermal = FloatField(required=False)
    hydro = FloatField(required=False)
    nuclear = FloatField(required=False)
    solar = FloatField(required=False)
    wind = FloatField(required=False)
    other = FloatField(required=False)

    def __init__(self, country=None, year=None, total_energy=0, combustibles=0, geothermal=0, hydro=0,
                 nuclear=0, solar=0, wind=0, other=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.country = country
        self.year = year
        self.total_energy = total_energy
        self.combustibles = combustibles
        self.geothermal = geothermal
        self.hydro = hydro
        self.nuclear = nuclear
        self.solar = solar
        self.wind = wind
        self.other = other
        self.keywords = ["total_energy", "combustibles", "geothermal", "hydro", "nuclear", "solar", "wind", "other"]

    def add_value(self, keyword, argument):
        if keyword in self.keywords:
            setattr(self, keyword, argument)
            self.keywords.remove(keyword)
            return
        eval_string = "self." + keyword
        new_value = eval(eval_string) + argument
        setattr(self, keyword, new_value)

    def verify_total(self):
        total = self.combustibles + self.geothermal + self.hydro + self.nuclear + self.solar + self.wind + self.other
        if self.total_energy == total:
            return True
        else:
            return self.total_energy - total


class EnergyAccess(Document):
    country = StringField(required=True)
    year = IntField(required=True)
    energy_access = FloatField()

    def __init__(self, country, year, energy_access=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.country = country
        self.year = year
        self.energy_access = energy_access


class EnergyConsumption(Document):
    country = StringField(required=True)
    year = IntField(required=True)
    energy_consumption = FloatField()

    def __init__(self, country, year, energy_consumption=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.country = country
        self.year = year
        self.energy_consumption = energy_consumption


class ConsumptionPercapita(Document):
    country = StringField(required=True)
    year = IntField(required=True)
    consumption_percapita = FloatField()

    def __init__(self, country, year, consumption_percapita=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.country = country
        self.year = year
        self.consumption_percapita = consumption_percapita

class Population(Document):
    country = StringField(required=True)
    year = IntField(required=True)
    population = IntField()

    def __int__(self, country, year, population=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.country = country
        self.year = year
        self.population = population


def csv_to_json(file_path):
    data_csv = pd.read_csv(file_path)
    data_json = json.loads(data_csv.to_json(orient='records'))
    return data_json


def process_energy_mix_csv(data_input):
    database = []
    for entry in data_input:
        energy_type = entry["Commodity - Transaction"]
        if energy_type in ENERGY_CATEGORIES:
            energy_category = ENERGY_CATEGORIES[energy_type]
            country = entry["Country or Area"]
            year = entry["Year"]
            amount = entry["Quantity"]
            exists = False
            for mix in database:
                if mix.country == country and mix.year == year:
                    mix.add_value(energy_category, amount)
                    exists = True
                    break
            if not exists:
                mix = EnergyMix()
                mix.country = country
                mix.year = year
                mix.add_value(energy_category, amount)
                database.append(mix)
    return database


def process_access_to_electricity_csv(data_input):
    database = []
    for entry in data_input:
        country = entry["Country Name"]
        for year in range(1990, 2017):
            percentage = entry[str(year)]
            access = EnergyAccess(country, year, percentage)
            database.append(access)
    return database


def process_population_csv(data_input):
    database = []
    for entry in data_input:
        country = entry["Country Name"]
        for year in range(1990, 2017):
            population = entry[str(year)]
            population_entry = Population(country, year, population)
            database.append(population_entry)
    return database


if __name__ == '__main__':
    data = csv_to_json("../DataSources/population.csv")
    db = process_population_csv(data)
    connect(
        db="comp9321ass3",
        username="admin",
        password="admin",
        host="ds117540.mlab.com",
        port=17540
    )
    Population.objects.insert(db)
