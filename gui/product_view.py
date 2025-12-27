import customtkinter as ctk
from services.inventory_service import InventoryService
from decimal import Decimal

class ProductView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.selected_product_id = None
        self.parts_widgets = []
        
        # Grid layout: Left (List) and Right (Details)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Left Side: List ---
        self.list_frame = ctk.CTkFrame(self)
        self.list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.list_label = ctk.CTkLabel(self.list_frame, text="Product List", font=ctk.CTkFont(size=16, weight="bold"))
        self.list_label.pack(pady=10)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self.list_frame, label_text="Available Products")
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.add_btn = ctk.CTkButton(self.list_frame, text="Add New Product", command=self.prepare_new_product)
        self.add_btn.pack(pady=10)
        
        # --- Right Side: Details ---
        self.details_scroll = ctk.CTkScrollableFrame(self)
        self.details_scroll.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.details_label = ctk.CTkLabel(self.details_scroll, text="Product Details", font=ctk.CTkFont(size=16, weight="bold"))
        self.details_label.pack(pady=10)
        
        # Product Basic Info Frame
        self.basic_info_frame = ctk.CTkFrame(self.details_scroll)
        self.basic_info_frame.pack(fill="x", padx=10, pady=5)
        
        self.type_var = ctk.StringVar()
        self.size_var = ctk.StringVar()
        self.color_var = ctk.StringVar()
        self.inventory_var = ctk.StringVar(value="0")
        
        fields = [
            ("Type:", self.type_var),
            ("Size:", self.size_var),
            ("Color Variant:", self.color_var),
            ("Inventory Count:", self.inventory_var),
        ]
        
        for i, (label_text, var) in enumerate(fields):
            lbl = ctk.CTkLabel(self.basic_info_frame, text=label_text)
            lbl.grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ctk.CTkEntry(self.basic_info_frame, textvariable=var)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="w")
            
        # Parts Section
        self.parts_label = ctk.CTkLabel(self.details_scroll, text="Parts", font=ctk.CTkFont(size=14, weight="bold"))
        self.parts_label.pack(pady=(20, 10))
        
        self.parts_container = ctk.CTkFrame(self.details_scroll)
        self.parts_container.pack(fill="x", padx=10, pady=5)
        
        self.add_part_btn = ctk.CTkButton(self.details_scroll, text="+ Add Part", command=self.add_part_entry)
        self.add_part_btn.pack(pady=10)
        
        self.save_btn = ctk.CTkButton(self.details_scroll, text="Save Product", command=self.save_product)
        self.save_btn.pack(pady=10)
        
        self.delete_btn = ctk.CTkButton(self.details_scroll, text="Delete Product", fg_color="red", hover_color="darkred", command=self.delete_product)
        self.delete_btn.pack(pady=10)
        
        self.status_label = ctk.CTkLabel(self.details_scroll, text="")
        self.status_label.pack()
        
        self.all_filaments = []
        self.load_filaments_list()
        self.load_products()

    def load_filaments_list(self):
        try:
            self.all_filaments = list(InventoryService.get_all_filaments())
        except Exception as e:
            print(f"Error loading filaments for product parts: {e}")

    def load_products(self):
        # Clear current list
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        try:
            products = InventoryService.get_all_products()
            for prod in products:
                btn = ctk.CTkButton(
                    self.scrollable_frame, 
                    text=str(prod),
                    fg_color="transparent",
                    text_color=("gray10", "gray90"),
                    hover_color=("gray70", "gray30"),
                    anchor="w",
                    command=lambda p=prod: self.select_product(p)
                )
                btn.pack(fill="x", padx=5, pady=2)
        except Exception as e:
            print(f"Error loading products: {e}")

    def select_product(self, product):
        self.selected_product_id = product.id
        self.type_var.set(product.product_type)
        self.size_var.set(product.size)
        self.color_var.set(product.color_variant)
        self.inventory_var.set(str(product.inventory_count))
        
        # Load Parts
        for widget_data in self.parts_widgets:
            widget_data['frame'].destroy()
        self.parts_widgets = []
        
        for part in product.parts:
            self.add_part_entry(part)
            
        self.status_label.configure(text=f"Editing: {product}", text_color=("gray10", "gray90"))

    def prepare_new_product(self):
        self.selected_product_id = None
        self.type_var.set("")
        self.size_var.set("")
        self.color_var.set("")
        self.inventory_var.set("0")
        
        for widget_data in self.parts_widgets:
            widget_data['frame'].destroy()
        self.parts_widgets = []
        
        # Start with 1 empty part as requested
        self.add_part_entry()
        
        self.status_label.configure(text="Adding New Product", text_color=("gray10", "gray90"))

    def add_part_entry(self, part=None):
        frame = ctk.CTkFrame(self.parts_container)
        frame.pack(fill="x", pady=5)
        
        name_var = ctk.StringVar(value=part.name if part else "")
        time_var = ctk.StringVar(value=str(part.print_time_hours) if part else "0.00")
        
        # Part header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(header, text="Part Name:").grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkEntry(header, textvariable=name_var, width=150).grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkLabel(header, text="Print Time (h):").grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkEntry(header, textvariable=time_var, width=60).grid(row=0, column=3, padx=5, pady=5)
        
        remove_btn = ctk.CTkButton(header, text="Remove Part", width=100, fg_color="red", hover_color="darkred", 
                                   command=lambda f=frame: self.remove_part_entry(f))
        remove_btn.grid(row=0, column=4, padx=20, pady=5)
        
        # Filament Usage Section for this part
        fil_container = ctk.CTkFrame(frame)
        fil_container.pack(fill="x", padx=20, pady=5)
        
        fil_widgets = []
        
        add_fil_btn = ctk.CTkButton(frame, text="+ Add Filament to Part", width=150, height=24,
                                    command=lambda c=fil_container, w=fil_widgets: self.add_filament_usage_entry(c, w))
        add_fil_btn.pack(pady=5)

        if part:
            for pf in part.filament_usage:
                self.add_filament_usage_entry(fil_container, fil_widgets, pf)
        else:
            # Add one empty filament entry by default
            self.add_filament_usage_entry(fil_container, fil_widgets)
        
        self.parts_widgets.append({
            'frame': frame,
            'id': part.id if part else None,
            'name_var': name_var,
            'time_var': time_var,
            'filament_widgets': fil_widgets
        })

    def add_filament_usage_entry(self, container, widgets_list, pf=None):
        row_frame = ctk.CTkFrame(container, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)
        
        fil_var = ctk.StringVar()
        grams_var = ctk.StringVar(value=str(pf.grams_needed) if pf else "0.00")
        
        filament_options = [f"{f.brand} {f.color} {f.material}" for f in self.all_filaments]
        fil_menu = ctk.CTkOptionMenu(row_frame, values=filament_options, variable=fil_var, width=200)
        fil_menu.grid(row=0, column=0, padx=5, pady=2)
        
        if pf:
            fil_var.set(f"{pf.filament.brand} {pf.filament.color} {pf.filament.material}")
        elif filament_options:
            fil_var.set(filament_options[0])
            
        ctk.CTkLabel(row_frame, text="grams:").grid(row=0, column=1, padx=5, pady=2)
        ctk.CTkEntry(row_frame, textvariable=grams_var, width=80).grid(row=0, column=2, padx=5, pady=2)
        
        del_btn = ctk.CTkButton(row_frame, text="X", width=30, fg_color="gray", hover_color="red",
                                command=lambda f=row_frame, w=widgets_list: self.remove_filament_usage_entry(f, w))
        del_btn.grid(row=0, column=3, padx=5, pady=2)
        
        widgets_list.append({
            'frame': row_frame,
            'filament_var': fil_var,
            'grams_var': grams_var,
            'menu': fil_menu
        })

    def remove_filament_usage_entry(self, frame, widgets_list):
        for i, data in enumerate(widgets_list):
            if data['frame'] == frame:
                data['frame'].destroy()
                widgets_list.pop(i)
                break

    def remove_part_entry(self, frame):
        for i, data in enumerate(self.parts_widgets):
            if data['frame'] == frame:
                data['frame'].destroy()
                self.parts_widgets.pop(i)
                break

    def save_product(self):
        try:
            product_data = {
                'product_type': self.type_var.get(),
                'size': self.size_var.get(),
                'color_variant': self.color_var.get(),
                'print_time_hours': Decimal('0.00'), # Reset base time to 0 as we use parts now
                'inventory_count': int(self.inventory_var.get() or "0")
            }
            
            parts_data = []
            for pw in self.parts_widgets:
                filament_usage = {}
                for fw in pw['filament_widgets']:
                    selected_fil_str = fw['filament_var'].get()
                    filament_obj = next((f for f in self.all_filaments if f"{f.brand} {f.color} {f.material}" == selected_fil_str), None)
                    if filament_obj:
                        grams = Decimal(fw['grams_var'].get() or "0")
                        # Aggregate if same filament added twice by mistake
                        filament_usage[filament_obj] = filament_usage.get(filament_obj, Decimal('0')) + grams
                
                parts_data.append({
                    'id': pw['id'],
                    'name': pw['name_var'].get(),
                    'print_time_hours': Decimal(pw['time_var'].get() or "0"),
                    'filament_usage': filament_usage
                })
            
            InventoryService.save_product(self.selected_product_id, product_data, parts_data)
            self.status_label.configure(text="Saved successfully!", text_color="green")
            self.load_products()
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")
            import traceback
            traceback.print_exc()

    def delete_product(self):
        if self.selected_product_id:
            try:
                InventoryService.delete_product(self.selected_product_id)
                self.status_label.configure(text="Deleted successfully!", text_color="green")
                self.prepare_new_product()
                self.load_products()
            except Exception as e:
                self.status_label.configure(text=f"Error: {str(e)}", text_color="red")
        else:
            self.status_label.configure(text="No product selected to delete.", text_color="orange")

    def refresh(self):
        self.load_filaments_list()
        self.load_products()
        
        # Update existing dropdowns with new filament list
        filament_options = [f"{f.brand} {f.color} {f.material}" for f in self.all_filaments]
        for pw in self.parts_widgets:
            for fw in pw['filament_widgets']:
                fw['menu'].configure(values=filament_options)
                
        if self.selected_product_id is None and not self.type_var.get() and not self.parts_widgets:
            self.prepare_new_product()
