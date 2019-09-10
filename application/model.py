from mongoengine import StringField, IntField, FloatField, Document, EmbeddedDocument, EmbeddedDocumentListField


class EnergySource(EmbeddedDocument):
    energy_type = StringField(required=True)
    amount = FloatField(min_value=0.00)

    def __init__(self,energy_type,amount, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.energy_type = energy_type
        self.amount = amount


class EnergyReport(Document):
    country = StringField(required=True)
    year = IntField(required=True, min_value=1990, max_value=2199)

    population = IntField(min_value=0)
    energy_access = FloatField(min_value=0.00, max_value=100.00)

    production_amount = FloatField(min_value=0.00)
    production_source = EmbeddedDocumentListField(EnergySource)
    consumption_amount = FloatField(min_value=0.00)

    def __init__(self, country, year, population=None, energy_access=None, production_amount=None,
                 production_source=[], consumption_amount=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.country = country
        self.year = year

        self.population = population
        self.energy_access = energy_access

        self.production_amount = production_amount
        self.production_source = production_source
        self.consumption_amount = consumption_amount
