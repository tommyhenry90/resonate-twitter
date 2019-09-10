import pendulum
from application import app
from flask import Flask, jsonify, render_template
from PublicationService.data_objects import EnergyMix, EnergyAccess, Population, EnergyConsumption, ConsumptionPercapita
from mongoengine import connect
from importer import mix
from flask_cors import CORS
from model import EnergyReport

pendulum.set_formatter('alternative')

@app.route('/')
def hello_world():
    return render_template('index.html')

app = Flask(__name__)
CORS(app)

@app.route("/energymix/<country>/<year>", methods=["GET"])
def energy_mix(country, year=2015):
    connect(
        db="comp9321ass3",
        username="admin",
        password="admin",
        host="ds117540.mlab.com",
        port=17540
    )

    mix = None
    for e in EnergyMix.objects(country__iexact=country, year=year):
        mix = e
    if not mix:
        response = jsonify(country__iexact=country, year=year)
        response.headers._list.append(('Access-Control-Allow-Origin', '*'))
        return response, 404
    energy_mix = {
        "country": country,
        "year": year,
        "total_energy": mix.total_energy,
        "combustibles": mix.combustibles,
        "geothermal": mix.geothermal,
        "hydro": mix.hydro,
        "nuclear": mix.nuclear,
        "solar": mix.solar,
        "wind": mix.wind,
        "other": mix.other
    }

    response = jsonify(energy_mix)
    response.headers._list.append(('Access-Control-Allow-Origin', '*'))
    return response, 200


@app.route("/energyaccess/<country>/<year>", methods=["GET"])
def energy_access(country, year):
    connect(
        db="comp9321ass3",
        username="admin",
        password="admin",
        host="ds117540.mlab.com",
        port=17540
    )

    access = None
    for e in EnergyAccess.objects(country__iexact=country, year=year):
        access = e
    if not access:
        response = jsonify(country__iexact=country, year=year)
        response.headers._list.append(('Access-Control-Allow-Origin', '*'))
        return response, 404

    energy_access = {
        "country": country,
        "year": year,
        "energy_access": access.energy_access
    }
    response = jsonify(energy_access)
    response.headers._list.append(('Access-Control-Allow-Origin', '*'))
    return response, 200


@app.route("/population/<country>/<year>", methods=["GET"])
def population(country, year):
    connect(
        db="comp9321ass3",
        username="admin",
        password="admin",
        host="ds117540.mlab.com",
        port=17540
    )

    pop = None
    for p in Population.objects(country__iexact=country, year=year):
        pop = p
    if not pop:
        response = jsonify(country__iexact=country, year=year)
        response.headers._list.append(('Access-Control-Allow-Origin', '*'))
        return response, 404

    population_response = {
        "country": country,
        "year": year,
        "population": pop.population
    }
    response = jsonify(population_response)
    response.headers._list.append(('Access-Control-Allow-Origin', '*'))
    return response, 200


@app.route("/consumption/<country>/<year>", methods=["GET"])
def consumption(country, year):
    connect(
        db="comp9321ass3",
        username="admin",
        password="admin",
        host="ds117540.mlab.com",
        port=17540
    )

    if ConsumptionPercapita.objects(country__iexact=country, year=year).count():
        for r in ConsumptionPercapita.objects(country__iexact=country, year=year):
            result = {
                "country": country,
                "year": year,
                "consumption_percapita": {
                    "amount": r.consumption_percapita,
                    "unit": "kWh"
                }
            }
            response = jsonify(result)
            response.headers._list.append(('Access-Control-Allow-Origin', '*'))
            return response, 200
    else:
        cons = EnergyConsumption.objects(country__iexact=country, year=year).count()
        pop = Population.objects(country__iexact=country, year=year).count()
        access = EnergyAccess.objects(country__iexact=country, year=year).count()

        if not cons or not pop or not access:
            response = jsonify(country__iexact=country, year=year)
            response.headers._list.append(('Access-Control-Allow-Origin', '*'))
            return response, 404

        for r in EnergyConsumption.objects(country__iexact=country, year=year):
            cons = r.energy_consumption
        for r in Population.objects(country__iexact=country, year=year):
            pop = r.population
        for r in EnergyAccess.objects(country__iexact=country, year=year):
            access = r.energy_access

        if not cons or not pop or not access:
            response = jsonify(country__iexact=country, year=year)
            response.headers._list.append(('Access-Control-Allow-Origin', '*'))
            return response, 404

        per_capita = cons * 1000000 / (pop * access / 100)

        t = ConsumptionPercapita(country,year,per_capita)
        t.save()

        result = {
            "country": country,
            "year": year,
            "consumption_percapita": {
                "amount": per_capita,
                "unit": "kWh"
            }
        }
        response = jsonify(result)
        response.headers._list.append(('Access-Control-Allow-Origin', '*'))
        return response, 200


@app.route("/greens/<year>", methods=["GET"])
def greens(year):
    connect(
        db="comp9321ass3",
        username="admin",
        password="admin",
        host="ds117540.mlab.com",
        port=17540
    )
    result = list()
    result.append(['Country', 'Green Index'])
    for data in EnergyMix.objects(year=year):
        green_point = round(100 * (data.geothermal + data.hydro + data.solar + data.wind) / data.total_energy)
        result.append([data.country, green_point])
    if not result:
        response = jsonify(year=year)
        response.headers._list.append(('Access-Control-Allow-Origin', '*'))
        return response, 404
    response = jsonify(result)
    response.headers._list.append(('Access-Control-Allow-Origin', '*'))
    return response, 200


@app.route("/recaps/<country>/<year>", methods=["GET"])
def recaps(country, year):
    connect(
        db="comp9321ass3",
        username="admin",
        password="admin",
        host="ds117540.mlab.com",
        port=17540
    )

    if not EnergyReport.objects(country__iexact=country, year=year):
        mix(country, year)
    result = None
    for base in EnergyReport.objects(country__iexact=country, year=year):
        sources = list()

        for source in base.production_source:
            percent = round(source.amount / base.production_amount * 100, 2)
            sources.append({
                'type': source.energy_type,
                'amount': source.amount,
                'percent': percent
            })

        cons_per = base.consumption_amount * 1000000 / (base.population * base.energy_access / 100)

        year_next = int(year) + 1
        year_prev = int(year) - 1

        next_report = None
        prev_report = None

        if EnergyMix.objects(country__iexact=country, year=year_next):
            next_report = "/".join(('/recaps', base.country, str(year_next)))

        if EnergyMix.objects(country__iexact=country, year=year_prev):
            prev_report = "/".join(('/recaps', base.country, str(year_prev)))

        delta = base.production_amount - base.consumption_amount
        result = {
            "country": base.country,
            "year": base.year,
            "population": base.population,
            "energy_access": base.energy_access,
            "consumption": {
                "amount": base.consumption_amount,
                "unit": "Gwh",
            },
            "consumption_percapita": {
                "amount": cons_per,
                "unit": "Kwh",
            },
            "production": {
                "amount": base.production_amount,
                "unit": "Gwh",
            },
            "sources": sources,
            "delta_energy": delta,
            "link": {
                "prev": prev_report,
                "next": next_report
            }
        }
    if result is not None:
        response = jsonify(result)
        response.headers._list.append(('Access-Control-Allow-Origin', '*'))
        return response, 200
    else:
        result = {
            "country": country,
            "year": year
        }
        response = jsonify(result)
        return response, 404


@app.route("/testconnection/", methods=["GET"])
def test_connection():
    print("hello")
    return "hello", 200

@app.route("/countries/<parameter>", methods=["GET"])
def countries_list(parameter):
    connect(
        db="comp9321ass3",
        username="admin",
        password="admin",
        host="ds117540.mlab.com",
        port=17540
    )
    ls = Population.objects(country__icontains=parameter).distinct(field="country")
    response = jsonify(ls)
    response.headers._list.append(('Access-Control-Allow-Origin', '*'))
    return response, 200


@app.route("/growths/<country>", methods=["GET"])
def growths(country):
    connect(
        db="comp9321ass3",
        username="admin",
        password="admin",
        host="ds117540.mlab.com",
        port=17540
    )
    result = []
    for annual in EnergyMix.objects(country__iexact=country).order_by('year'):
        result.append([
            str(annual.year),
            round(annual.combustibles / annual.total_energy * 100, 2),
            round(annual.geothermal / annual.total_energy * 100, 2),
            round(annual.hydro / annual.total_energy * 100, 2),
            round(annual.nuclear / annual.total_energy * 100, 2),
            round(annual.solar / annual.total_energy * 100, 2),
            round(annual.wind / annual.total_energy * 100, 2),
            round(annual.other / annual.total_energy * 100, 2)
        ])
    if not result:
        response = jsonify(country=country)
        response.headers._list.append(('Access-Control-Allow-Origin', '*'))
        return response, 404
    response = jsonify(result)
    response.headers._list.append(('Access-Control-Allow-Origin', '*'))
    return response, 200


@app.route("/consumption_growths/<country>", methods=["GET"])
def consumption_growths(country):
    connect(
        db="comp9321ass3",
        username="admin",
        password="admin",
        host="ds117540.mlab.com",
        port=17540
    )
    result = list()

    for rec_1 in EnergyConsumption.objects(country__iexact=country):
        consumption = rec_1.energy_consumption
        access = 0
        for rec_2 in EnergyAccess.objects(country__iexact=country, year=rec_1.year):
            access = rec_2.energy_access
        population = 0
        for rec_2 in Population.objects(country__iexact=country, year=rec_1.year):
            population = rec_2.population
        if access and population:
            per_capita = consumption * 1000000 / (population * access / 100)
        else:
            per_capita = 0
        cons = ConsumptionPercapita(rec_1.country, rec_1.year, per_capita)
        cons.save()
        result.append([
            rec_1.year,
            round(per_capita, 2)
        ])
    if not result:
        response = jsonify(country=country)
        response.headers._list.append(('Access-Control-Allow-Origin', '*'))
        return response, 404
    response = jsonify(result)
    response.headers._list.append(('Access-Control-Allow-Origin', '*'))
    return response, 200


@app.route("/consumption/<year>", methods=["GET"])
def global_consumption(year):
    connect(
        db="comp9321ass3",
        username="admin",
        password="admin",
        host="ds117540.mlab.com",
        port=17540
    )
    result = list()

    for rec_1 in EnergyConsumption.objects(year=year):
        print(rec_1.country)

        if ConsumptionPercapita.objects(year=year, country=rec_1.country).count():
            for rec_2 in ConsumptionPercapita.objects(country=rec_1.country, year=year):
                per_capita = rec_2.consumption_percapita
        else:
            consumption = rec_1.energy_consumption
            access = 0
            for rec_2 in EnergyAccess.objects(country=rec_1.country, year=year):
                access = rec_2.energy_access
            population = 0
            for rec_2 in Population.objects(country=rec_1.country, year=year):
                population = rec_2.population
            if (access and population):
                per_capita = consumption * 1000000 / (population * access / 100)
            else:
                per_capita = 0
            cons = ConsumptionPercapita(rec_1.country, year, per_capita)
            cons.save()
        result.append([
            rec_1.country,
            round(per_capita, 2)
        ])
    if not result:
        response = jsonify(year=year)
        response.headers._list.append(('Access-Control-Allow-Origin', '*'))
        return response, 404
    response = jsonify(result)
    response.headers._list.append(('Access-Control-Allow-Origin', '*'))
    return response, 200


@app.route("/globalfuel/<fueltype>/<year>")
def fuel_summary(fueltype, year):
    connect(
        db="comp9321ass3",
        username="admin",
        password="admin",
        host="ds117540.mlab.com",
        port=17540
    )
    result = list()
    result.append(['Country', fueltype])
    for data in EnergyMix.objects(year=year):
        fuel_percentage = 100 * eval("data." + fueltype.lower()) / data.total_energy
        result.append([data.country, fuel_percentage])
    if not result:
        response = jsonify(fueltype=fueltype, year=year)
        response.headers._list.append(('Access-Control-Allow-Origin', '*'))
        return response, 404
    response = jsonify(result)
    response.headers._list.append(('Access-Control-Allow-Origin', '*'))
    return response, 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
