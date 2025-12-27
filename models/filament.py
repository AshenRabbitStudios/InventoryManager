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
    rolls_in_stock = IntegerField(default=0)

    class Meta:
        indexes = (
            (('brand', 'material', 'color'), True),
        )

    def __str__(self):
        return f"{self.color} {self.material}"

    def adjust_inventory(self, grams):
        """
        Adjusts the grams remaining. If it goes below zero, 
        decrements rolls_in_stock and resets grams_remaining.
        grams: Decimal to subtract (positive to subtract, negative to add back)
        """
        from decimal import Decimal
        self.grams_remaining -= Decimal(str(grams))
        
        # Handle depletion: move to next roll
        while self.grams_remaining < 0 and self.rolls_in_stock > 0:
            self.rolls_in_stock -= 1
            self.grams_remaining += self.grams_per_roll
            
        # Handle reversal: if grams_remaining exceeds roll capacity, move back to rolls_in_stock
        while self.grams_remaining >= self.grams_per_roll:
            # Only move to rolls_in_stock if we are adding back (reversing a sale)
            # or if we somehow overfilled it.
            self.rolls_in_stock += 1
            self.grams_remaining -= self.grams_per_roll
            
        self.save()


class FilamentPurchase(BaseModel):
    """
    Represents a purchase of a filament roll.
    """
    filament = ForeignKeyField(Filament, backref='purchases', on_delete='CASCADE')
    date = DateTimeField(default=datetime.now)
    rolls_bought = IntegerField()
    grams_added = DecimalField(decimal_places=2)