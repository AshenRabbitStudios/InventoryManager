from peewee import CharField, DecimalField, IntegerField, ForeignKeyField, DateTimeField
from datetime import datetime
from .base import BaseModel


class Filament(BaseModel):
    brand = CharField(null=True)
    material = CharField()
    color = CharField()
    cost_per_roll = DecimalField(decimal_places=2)
    grams_per_roll = DecimalField(decimal_places=2, default=1000.0)
    grams_remaining = DecimalField(decimal_places=2, default=1000.0)

    class Meta:
        indexes = (
            (('brand', 'material', 'color'), True),
        )

    def __str__(self):
        return f"{self.color} {self.material}"


class FilamentPurchase(BaseModel):
    """
    Represents a purchase of a filament roll.
    """
    filament = ForeignKeyField(Filament, backref='purchases', on_delete='CASCADE')
    date = DateTimeField(default=datetime.now)
    rolls_bought = IntegerField()
    grams_added = DecimalField(decimal_places=2)