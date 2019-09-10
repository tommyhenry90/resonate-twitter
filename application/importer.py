from mongoengine import connect
from model import EnergySource, EnergyReport
from PublicationService.data_objects import EnergyConsumption, EnergyMix, Population, EnergyAccess
import xml.etree.ElementTree as ET


def reset():
    connect(
        db="comp9321ass3",
        username="admin",
        password="admin",
        host="ds117540.mlab.com",
        port=17540
    )
    EnergyConsumption.objects().delete()


def upload_access():

    tree1 = ET.parse('dataset/access.xml')
    root1 = tree1.getroot()

    connect(
        db="comp9321ass3",
        username="admin",
        password="admin",
        host="ds117540.mlab.com",
        port=17540
    )

    for record in root1.find('.//data'):
        country = record.find('.//field[1]').text
        year = record.find('.//field[3]').text
        try:
            amount = float(record.find('.//field[4]').text)
            raw = Population(country, year, amount)
            raw.save()
        except:
            amount = None
        print(country, year, amount)


def upload_population():

    tree1 = ET.parse('dataset/population.xml')
    root1 = tree1.getroot()

    connect(
        db="comp9321ass3",
        username="admin",
        password="admin",
        host="ds117540.mlab.com",
        port=17540
    )

    for record in root1.find('.//data'):
        country = record.find('.//field[1]').text
        year = record.find('.//field[3]').text
        try:
            amount = float(record.find('.//field[4]').text)
            raw = Population(country, year, amount)
            raw.save()
        except:
            amount = None
        print(country, year, amount)


def upload_consumption():

    tree1 = ET.parse('dataset/consumption.xml')
    root1 = tree1.getroot()

    connect(
        db="comp9321ass3",
        username="admin",
        password="admin",
        host="ds117540.mlab.com",
        port=17540
    )

    for record in root1.find('.//data'):
        country = record.find('.//field[1]').text
        year = record.find('.//field[3]').text
        try:
            amount = float(record.find('.//field[5]').text)
            raw = EnergyConsumption(country, year, amount)
            raw.save()
        except:
            amount = None
        print(country, year, amount)


def mix(country, year):
    connect(
        db="comp9321ass3",
        username="admin",
        password="admin",
        host="ds117540.mlab.com",
        port=17540
    )
    EnergyReport.objects(country=country, year=year).delete()
    for base in EnergyMix.objects(country=country, year=year):
        pop = None
        access = None
        consumption = None
        for temp in Population.objects(country=base.country, year=base.year):
            pop = temp.population

        for temp in EnergyAccess.objects(country=base.country, year=base.year):
            access = temp.energy_access

        for temp in EnergyConsumption.objects(country=base.country, year=base.year):
            consumption = temp.energy_consumption

        sources = list()

        source = EnergySource('solar', base.solar)
        sources.append(source)

        source = EnergySource('wind', base.wind)
        sources.append(source)

        source = EnergySource('hydro', base.hydro)
        sources.append(source)

        source = EnergySource('geothermal', base.geothermal)
        sources.append(source)

        source = EnergySource('combustibles', base.combustibles)
        sources.append(source)

        source = EnergySource('other', base.other)
        sources.append(source)

        report = EnergyReport(base.country, base.year, pop, access, base.total_energy, sources, consumption)

        report.save()

if __name__ == '__main__':
    mix('Indonesia',2015)
