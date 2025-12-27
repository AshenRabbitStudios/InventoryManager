import customtkinter as ctk
from services.inventory_service import InventoryService
from decimal import Decimal

class OverviewView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Grid layout: Top (Lists) and Bottom (Sale)
        self.grid_rowconfigure(0, weight=3) # Product/Filament lists
        self.grid_rowconfigure(1, weight=1) # Sale area
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # --- Top Left: Product List ---
        self.product_list_frame = ctk.CTkFrame(self)
        self.product_list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.prod_label = ctk.CTkLabel(self.product_list_frame, text="Product Inventory", font=ctk.CTkFont(size=16, weight="bold"))
        self.prod_label.pack(pady=10)
        
        self.prod_scroll = ctk.CTkScrollableFrame(self.product_list_frame)
        self.prod_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- Top Right: Filament List ---
        self.filament_list_frame = ctk.CTkFrame(self)
        self.filament_list_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.fil_label = ctk.CTkLabel(self.filament_list_frame, text="Filament Stock", font=ctk.CTkFont(size=16, weight="bold"))
        self.fil_label.pack(pady=10)
        
        self.fil_scroll = ctk.CTkScrollableFrame(self.filament_list_frame)
        self.fil_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- Bottom: New Sale Area ---
        self.sale_frame = ctk.CTkFrame(self)
        self.sale_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.sale_label = ctk.CTkLabel(self.sale_frame, text="New Sale", font=ctk.CTkFont(size=16, weight="bold"))
        self.sale_label.grid(row=0, column=0, columnspan=6, pady=5)
        
        ctk.CTkLabel(self.sale_frame, text="Product:").grid(row=1, column=0, padx=5, pady=5)
        self.sale_product_var = ctk.StringVar()
        self.sale_product_menu = ctk.CTkOptionMenu(self.sale_frame, variable=self.sale_product_var, values=[])
        self.sale_product_menu.grid(row=1, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(self.sale_frame, text="Quantity:").grid(row=1, column=2, padx=5, pady=5)
        self.sale_qty_var = ctk.StringVar(value="1")
        self.sale_qty_entry = ctk.CTkEntry(self.sale_frame, textvariable=self.sale_qty_var, width=50)
        self.sale_qty_entry.grid(row=1, column=3, padx=5, pady=5)
        
        ctk.CTkLabel(self.sale_frame, text="Total Value ($):").grid(row=1, column=4, padx=5, pady=5)
        self.sale_value_var = ctk.StringVar()
        self.sale_value_entry = ctk.CTkEntry(self.sale_frame, textvariable=self.sale_value_var, width=80)
        self.sale_value_entry.grid(row=1, column=5, padx=5, pady=5)
        
        self.add_sale_btn = ctk.CTkButton(self.sale_frame, text="Record Sale", command=self.record_sale)
        self.add_sale_btn.grid(row=1, column=6, padx=20, pady=5)
        
        self.status_label = ctk.CTkLabel(self.sale_frame, text="")
        self.status_label.grid(row=2, column=0, columnspan=7)
        
        self.all_products = []
        self.all_filaments = []
        
        self.refresh()

    def load_products(self):
        for widget in self.prod_scroll.winfo_children():
            widget.destroy()
        
        self.all_products = list(InventoryService.get_all_products())
        
        # Header
        header = ctk.CTkFrame(self.prod_scroll, fg_color="transparent")
        header.pack(fill="x", padx=5)
        ctk.CTkLabel(header, text="Product", width=200, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0)
        ctk.CTkLabel(header, text="In Stock", width=70, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1)
        ctk.CTkLabel(header, text="Printable", width=70, font=ctk.CTkFont(weight="bold")).grid(row=0, column=2)
        
        for prod in self.all_products:
            row = ctk.CTkFrame(self.prod_scroll, fg_color="transparent")
            row.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(row, text=str(prod), width=200, anchor="w").grid(row=0, column=0)
            
            # Modifiable inventory count
            inv_var = ctk.StringVar(value=str(prod.inventory_count))
            inv_entry = ctk.CTkEntry(row, textvariable=inv_var, width=60)
            inv_entry.grid(row=0, column=1, padx=5)
            # Binding focus out to save
            inv_entry.bind("<FocusOut>", lambda e, p=prod, v=inv_var: self.update_product_inventory(p, v))
            inv_entry.bind("<Return>", lambda e, p=prod, v=inv_var: self.update_product_inventory(p, v))
            
            # Non-modifiable printable count
            printable = InventoryService.calculate_printable_count(prod)
            ctk.CTkLabel(row, text=str(printable), width=60).grid(row=0, column=2, padx=5)

        # Update sale dropdown
        product_names = [str(p) for p in self.all_products]
        self.sale_product_menu.configure(values=product_names)
        if product_names and not self.sale_product_var.get():
            self.sale_product_var.set(product_names[0])

    def load_filaments(self):
        for widget in self.fil_scroll.winfo_children():
            widget.destroy()
        
        self.all_filaments = list(InventoryService.get_all_filaments())
        
        # Header
        header = ctk.CTkFrame(self.fil_scroll, fg_color="transparent")
        header.pack(fill="x", padx=5)
        ctk.CTkLabel(header, text="Filament", width=180, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0)
        ctk.CTkLabel(header, text="Rolls", width=60, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1)
        ctk.CTkLabel(header, text="Grams", width=70, font=ctk.CTkFont(weight="bold")).grid(row=0, column=2)
        
        for fil in self.all_filaments:
            row = ctk.CTkFrame(self.fil_scroll, fg_color="transparent")
            row.pack(fill="x", pady=2, padx=5)
            
            ctk.CTkLabel(row, text=f"{fil.brand} {fil.color}", width=180, anchor="w").grid(row=0, column=0)
            
            # Modifiable rolls in stock
            rolls_var = ctk.StringVar(value=str(fil.rolls_in_stock))
            rolls_entry = ctk.CTkEntry(row, textvariable=rolls_var, width=50)
            rolls_entry.grid(row=0, column=1, padx=5)
            
            rolls_entry.bind("<FocusOut>", lambda e, f=fil, v=rolls_var: self.update_filament_rolls(f, v))
            rolls_entry.bind("<Return>", lambda e, f=fil, v=rolls_var: self.update_filament_rolls(f, v))

            # Modifiable grams remaining
            grams_var = ctk.StringVar(value=f"{fil.grams_remaining:.1f}")
            grams_entry = ctk.CTkEntry(row, textvariable=grams_var, width=60)
            grams_entry.grid(row=0, column=2, padx=5)
            
            grams_entry.bind("<FocusOut>", lambda e, f=fil, v=grams_var: self.update_filament_grams(f, v))
            grams_entry.bind("<Return>", lambda e, f=fil, v=grams_var: self.update_filament_grams(f, v))

    def update_product_inventory(self, product, var):
        try:
            new_val = int(var.get())
            if product.inventory_count != new_val:
                product.inventory_count = new_val
                product.save()
                self.status_label.configure(text=f"Updated {product} inventory to {new_val}", text_color="green")
        except ValueError:
            var.set(str(product.inventory_count))

    def update_filament_rolls(self, filament, var):
        try:
            new_val = int(var.get())
            if filament.rolls_in_stock != new_val:
                filament.rolls_in_stock = new_val
                filament.save()
                self.status_label.configure(text=f"Updated {filament} rolls to {new_val}", text_color="green")
                # Reload products to update printable count
                self.load_products()
        except ValueError:
            var.set(str(filament.rolls_in_stock))

    def update_filament_grams(self, filament, var):
        try:
            new_val = Decimal(var.get())
            if filament.grams_remaining != new_val:
                filament.grams_remaining = new_val
                filament.save()
                self.status_label.configure(text=f"Updated {filament} grams to {new_val}", text_color="green")
                # Reload products to update printable count
                self.load_products()
        except Exception:
            var.set(f"{filament.grams_remaining:.1f}")

    def record_sale(self):
        try:
            prod_str = self.sale_product_var.get()
            qty = int(self.sale_qty_var.get())
            val = Decimal(self.sale_value_var.get() or "0")
            
            selected_prod = next((p for p in self.all_products if str(p) == prod_str), None)
            
            if selected_prod:
                InventoryService.create_sale(selected_prod, qty, val)
                self.status_label.configure(text=f"Recorded sale of {qty}x {selected_prod}", text_color="green")
                self.refresh() # Full refresh to update inventory and filaments
            else:
                self.status_label.configure(text="Error: Product not found", text_color="red")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")

    def refresh(self):
        self.load_products()
        self.load_filaments()
