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
        
        # --- Top Right: Right Panel (Filaments + To-Do) ---
        self.right_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.right_panel.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")
        self.right_panel.grid_rowconfigure(0, weight=1) # Filament Stock
        self.right_panel.grid_rowconfigure(1, weight=1) # To-Do Section
        self.right_panel.grid_columnconfigure(0, weight=1)

        # Filament Stock Section
        self.filament_list_frame = ctk.CTkFrame(self.right_panel)
        self.filament_list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.fil_label = ctk.CTkLabel(self.filament_list_frame, text="Filament Stock", font=ctk.CTkFont(size=16, weight="bold"))
        self.fil_label.pack(pady=10)
        
        self.fil_scroll = ctk.CTkScrollableFrame(self.filament_list_frame)
        self.fil_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # To-Do Section
        self.todo_frame = ctk.CTkFrame(self.right_panel)
        self.todo_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.todo_label = ctk.CTkLabel(self.todo_frame, text="To-Do List", font=ctk.CTkFont(size=16, weight="bold"))
        self.todo_label.pack(pady=10)

        self.todo_scroll = ctk.CTkScrollableFrame(self.todo_frame)
        self.todo_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
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
        # We'll use a consistent grid for headers and rows
        header.grid_columnconfigure(0, weight=1) # Product/Size
        header.grid_columnconfigure(1, weight=0) # In Stock
        header.grid_columnconfigure(2, weight=0) # Printable
        
        ctk.CTkLabel(header, text="Product / Size", width=200, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="Stock", width=60, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5)
        ctk.CTkLabel(header, text="Printable", width=60, font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5)
        
        current_type = None
        current_color = None
        
        for prod in self.all_products:
            # 1. Type Header
            if prod.product_type != current_type:
                current_type = prod.product_type
                current_color = None # Reset color when type changes
                type_header = ctk.CTkFrame(self.prod_scroll, fg_color=("gray70", "gray20"), corner_radius=4)
                type_header.pack(fill="x", pady=(15, 2), padx=5)
                ctk.CTkLabel(type_header, text=current_type.upper(), font=ctk.CTkFont(size=14, weight="bold")).pack(pady=2)

            # 2. Color Header (Sub-group)
            if prod.color_variant != current_color:
                current_color = prod.color_variant
                color_header = ctk.CTkFrame(self.prod_scroll, fg_color=("gray80", "gray30"), corner_radius=4)
                color_header.pack(fill="x", pady=(5, 2), padx=(15, 5))
                ctk.CTkLabel(color_header, text=current_color, font=ctk.CTkFont(size=12, weight="bold")).pack(pady=1)

            row = ctk.CTkFrame(self.prod_scroll, fg_color="transparent")
            row.pack(fill="x", pady=1, padx=(30, 5))
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=0)
            row.grid_columnconfigure(2, weight=0)
            
            # Show just the size in the row, since Type and Color are in the header
            ctk.CTkLabel(row, text=prod.size, width=200, anchor="w").grid(row=0, column=0, sticky="w", padx=(20, 0))
            
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

        # Update sale dropdown - still use full name for dropdown
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
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)
        header.grid_columnconfigure(2, weight=0)
        
        ctk.CTkLabel(header, text="Filament", width=180, anchor="w", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(header, text="Rolls", width=60, font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5)
        ctk.CTkLabel(header, text="Grams", width=70, font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5)
        
        for fil in self.all_filaments:
            row = ctk.CTkFrame(self.fil_scroll, fg_color="transparent")
            row.pack(fill="x", pady=2, padx=5)
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=0)
            row.grid_columnconfigure(2, weight=0)
            
            ctk.CTkLabel(row, text=f"{fil.brand} {fil.color}", width=180, anchor="w").grid(row=0, column=0, sticky="w")
            
            # Modifiable rolls in stock
            rolls_var = ctk.StringVar(value=str(fil.rolls_in_stock))
            rolls_entry = ctk.CTkEntry(row, textvariable=rolls_var, width=60)
            rolls_entry.grid(row=0, column=1, padx=5)
            
            rolls_entry.bind("<FocusOut>", lambda e, f=fil, v=rolls_var: self.update_filament_rolls(f, v))
            rolls_entry.bind("<Return>", lambda e, f=fil, v=rolls_var: self.update_filament_rolls(f, v))

            # Modifiable grams remaining
            grams_var = ctk.StringVar(value=f"{fil.grams_remaining:.1f}")
            grams_entry = ctk.CTkEntry(row, textvariable=grams_var, width=70)
            grams_entry.grid(row=0, column=2, padx=5)
            
            grams_entry.bind("<FocusOut>", lambda e, f=fil, v=grams_var: self.update_filament_grams(f, v))
            grams_entry.bind("<Return>", lambda e, f=fil, v=grams_var: self.update_filament_grams(f, v))

    def load_todo(self):
        for widget in self.todo_scroll.winfo_children():
            widget.destroy()

        todo_data = InventoryService.get_todo_data()

        # Create a container frame for columns
        container = ctk.CTkFrame(self.todo_scroll, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)

        # Left Column: Things to Print
        print_col = ctk.CTkFrame(container, fg_color="transparent")
        print_col.grid(row=0, column=0, sticky="nsew", padx=5)

        ctk.CTkLabel(print_col, text="NEXT THINGS TO PRINT", font=ctk.CTkFont(size=12, weight="bold"), text_color=("gray40", "gray60")).pack(pady=(10, 5))
        
        if not todo_data['to_print']:
            ctk.CTkLabel(print_col, text="Everything is stocked!").pack()
        else:
            for prod in todo_data['to_print']:
                needed = 3 - prod.inventory_count
                row = ctk.CTkFrame(print_col, fg_color="transparent")
                row.pack(fill="x", padx=5, pady=2)
                ctk.CTkLabel(row, text=str(prod), anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=f"Print {needed}", font=ctk.CTkFont(weight="bold"), text_color="orange").pack(side="right")

        # Right Column: Filaments to Order
        order_col = ctk.CTkFrame(container, fg_color="transparent")
        order_col.grid(row=0, column=1, sticky="nsew", padx=5)

        ctk.CTkLabel(order_col, text="FILAMENTS TO ORDER", font=ctk.CTkFont(size=12, weight="bold"), text_color=("gray40", "gray60")).pack(pady=(10, 5))

        if not todo_data['to_order']:
            ctk.CTkLabel(order_col, text="Stock levels sufficient.").pack()
        else:
            for item in todo_data['to_order']:
                fil = item['filament']
                row = ctk.CTkFrame(order_col, fg_color="transparent")
                row.pack(fill="x", padx=5, pady=2)
                ctk.CTkLabel(row, text=f"{fil.brand} {fil.color}", anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=f"Order {item['rolls']} rolls", font=ctk.CTkFont(weight="bold"), text_color="red").pack(side="right")

    def update_product_inventory(self, product, var):
        try:
            new_val = int(var.get())
            if product.inventory_count != new_val:
                product.inventory_count = new_val
                product.save()
                self.status_label.configure(text=f"Updated {product} inventory to {new_val}", text_color="green")
                self.load_todo() # Refresh todo list
        except ValueError:
            var.set(str(product.inventory_count))

    def update_filament_rolls(self, filament, var):
        try:
            new_val = int(var.get())
            if filament.rolls_in_stock != new_val:
                filament.rolls_in_stock = new_val
                filament.save()
                self.status_label.configure(text=f"Updated {filament} rolls to {new_val}", text_color="green")
                # Reload products to update printable count and todo
                self.load_products()
                self.load_todo()
        except ValueError:
            var.set(str(filament.rolls_in_stock))

    def update_filament_grams(self, filament, var):
        try:
            new_val = Decimal(var.get())
            if filament.grams_remaining != new_val:
                filament.grams_remaining = new_val
                filament.save()
                self.status_label.configure(text=f"Updated {filament} grams to {new_val}", text_color="green")
                # Reload products to update printable count and todo
                self.load_products()
                self.load_todo()
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
        self.load_todo()
