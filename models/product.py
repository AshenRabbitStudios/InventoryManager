from peewee import CharField, DecimalField, IntegerField, ForeignKeyField
from decimal import Decimal
from .base import BaseModel
from .filament import Filament


class Product(BaseModel):
    """
    Represents a 3D printed product that can be sold.
    A product can be composed of multiple Parts.
    """
    product_type = CharField()
    size = CharField()
    color_variant = CharField()
    print_time_hours = DecimalField(decimal_places=2, default=Decimal('0.00'))
    inventory_count = IntegerField(default=0)

    class Meta:
        indexes = (
            (('product_type', 'size', 'color_variant'), True),
        )

    def __str__(self):
        return f"{self.product_type} - {self.size} - {self.color_variant}"

    def add_part(self, name, print_time_hours=0):
        """
        Creates and adds a part to this product.
        Updates the database immediately.
        """
        return Part.create(
            product=self,
            name=name,
            print_time_hours=Decimal(str(print_time_hours))
        )

    def add_filament_usage(self, filament, grams_needed):
        """
        Adds or updates filament usage for this product.
        Updates the database immediately.
        """
        pf, created = ProductFilament.get_or_create(
            product=self,
            filament=filament,
            defaults={'grams_needed': Decimal(str(grams_needed))}
        )
        if not created:
            pf.grams_needed = Decimal(str(grams_needed))
            pf.save()
        return pf

    def adjust_inventory(self, amount):
        """
        Adjusts the inventory count by the given amount (positive or negative).
        Updates the database immediately.
        """
        self.inventory_count += amount
        self.save()

    @property
    def total_print_time(self):
        """Calculates total print time including all parts."""
        total = Decimal(str(self.print_time_hours))
        for part in self.parts:
            total += Decimal(str(part.total_print_time))
        return total

    @property
    def total_filament_usage(self):
        """
        Calculates total filament usage including all parts.
        Returns a dictionary mapping Filament objects to total grams needed.
        """
        usage = {}
        # Current product usage
        for pf in self.filament_usage:
            usage[pf.filament] = usage.get(pf.filament, Decimal('0')) + Decimal(str(pf.grams_needed))
        
        # Parts usage
        for part in self.parts:
            part_usage = part.total_filament_usage
            for filament, grams in part_usage.items():
                usage[filament] = usage.get(filament, Decimal('0')) + Decimal(str(grams))
        return usage

    @property
    def total_cost(self):
        """
        Calculates the total cost of materials for this product.
        """
        total = Decimal('0.00')
        usage = self.total_filament_usage
        for filament, grams in usage.items():
            cost = (grams / filament.grams_per_roll) * filament.cost_per_roll
            total += cost
        return total.quantize(Decimal('0.01'))


class Part(BaseModel):
    """
    Represents a component part of a Product.
    Parts have their own print time and filament usage.
    """
    product = ForeignKeyField(Product, backref='parts', on_delete='CASCADE')
    name = CharField()
    print_time_hours = DecimalField(decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.name} (Part of {self.product})"

    def add_filament_usage(self, filament, grams_needed):
        """
        Adds or updates filament usage for this part.
        Updates the database immediately.
        """
        pf, created = PartFilament.get_or_create(
            part=self,
            filament=filament,
            defaults={'grams_needed': Decimal(str(grams_needed))}
        )
        if not created:
            pf.grams_needed = Decimal(str(grams_needed))
            pf.save()
        return pf

    @property
    def total_print_time(self):
        """Returns the print time for this part."""
        return Decimal(str(self.print_time_hours))

    @property
    def total_filament_usage(self):
        """
        Returns a dictionary mapping Filament objects to grams needed for this part.
        """
        usage = {}
        for pf in self.filament_usage:
            usage[pf.filament] = usage.get(pf.filament, Decimal('0')) + Decimal(str(pf.grams_needed))
        return usage

    @property
    def total_cost(self):
        """
        Calculates the total cost of materials for this part.
        """
        total = Decimal('0.00')
        usage = self.total_filament_usage
        for filament, grams in usage.items():
            cost = (grams / filament.grams_per_roll) * filament.cost_per_roll
            total += cost
        return total.quantize(Decimal('0.01'))


class ProductFilament(BaseModel):
    """
    Junction table - tracks which filaments a product uses directly.
    """
    product = ForeignKeyField(Product, backref='filament_usage', on_delete='CASCADE')
    filament = ForeignKeyField(Filament, backref='used_in_products', on_delete='CASCADE')
    grams_needed = DecimalField(decimal_places=2)


class PartFilament(BaseModel):
    """
    Junction table - tracks which filaments a part uses.
    """
    part = ForeignKeyField(Part, backref='filament_usage', on_delete='CASCADE')
    filament = ForeignKeyField(Filament, backref='used_in_parts', on_delete='CASCADE')
    grams_needed = DecimalField(decimal_places=2)