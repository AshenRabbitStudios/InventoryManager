import customtkinter as ctk
from services.inventory_service import InventoryService
from datetime import datetime
from decimal import Decimal

class SalesView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.selected_sale_id = None
        self.all_products = []
        
        # Grid layout: Left (List) and Right (Details)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Left Side: List ---
        self.list_frame = ctk.CTkFrame(self)
        self.list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.list_label = ctk.CTkLabel(self.list_frame, text="Sale History", font=ctk.CTkFont(size=16, weight="bold"))
        self.list_label.pack(pady=10)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self.list_frame, label_text="Recent Sales")
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- Right Side: Details ---
        self.details_frame = ctk.CTkFrame(self)
        self.details_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.details_label = ctk.CTkLabel(self.details_frame, text="Sale Details", font=ctk.CTkFont(size=16, weight="bold"))
        self.details_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Form fields
        self.product_var = ctk.StringVar()
        self.date_var = ctk.StringVar()
        self.value_var = ctk.StringVar()
        
        ctk.CTkLabel(self.details_frame, text="Product:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.product_menu = ctk.CTkOptionMenu(self.details_frame, variable=self.product_var, values=[])
        self.product_menu.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(self.details_frame, text="Date (YYYY-MM-DD HH:MM):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.date_entry = ctk.CTkEntry(self.details_frame, textvariable=self.date_var, width=200)
        self.date_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkLabel(self.details_frame, text="Total Value ($):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.value_entry = ctk.CTkEntry(self.details_frame, textvariable=self.value_var, width=100)
        self.value_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        self.save_btn = ctk.CTkButton(self.details_frame, text="Save Changes", command=self.save_sale)
        self.save_btn.grid(row=4, column=0, pady=20)
        
        self.delete_btn = ctk.CTkButton(self.details_frame, text="Delete Sale", fg_color="red", hover_color="darkred", command=self.delete_sale)
        self.delete_btn.grid(row=4, column=1, pady=20)
        
        self.status_label = ctk.CTkLabel(self.details_frame, text="")
        self.status_label.grid(row=5, column=0, columnspan=2)
        
        self.refresh()

    def load_sales(self):
        # Clear current list
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        try:
            sales = InventoryService.get_active_sales()
            for sale in sales:
                btn = ctk.CTkButton(
                    self.scrollable_frame, 
                    text=str(sale),
                    fg_color="transparent",
                    text_color=("gray10", "gray90"),
                    hover_color=("gray70", "gray30"),
                    anchor="w",
                    command=lambda s=sale: self.select_sale(s)
                )
                btn.pack(fill="x", padx=5, pady=2)
        except Exception as e:
            print(f"Error loading sales: {e}")

    def load_products(self):
        try:
            self.all_products = list(InventoryService.get_all_products())
            product_names = [str(p) for p in self.all_products]
            self.product_menu.configure(values=product_names)
        except Exception as e:
            print(f"Error loading products for sales view: {e}")

    def select_sale(self, sale):
        self.selected_sale_id = sale.id
        self.product_var.set(str(sale.product))
        self.date_var.set(sale.date.strftime('%Y-%m-%d %H:%M'))
        self.value_var.set(str(sale.total_value))
        self.status_label.configure(text=f"Editing sale from {sale.date.strftime('%Y-%m-%d')}", text_color=("gray10", "gray90"))

    def save_sale(self):
        if not self.selected_sale_id:
            self.status_label.configure(text="No sale selected.", text_color="orange")
            return
            
        try:
            prod_str = self.product_var.get()
            selected_prod = next((p for p in self.all_products if str(p) == prod_str), None)
            
            if not selected_prod:
                raise ValueError("Product not found.")
                
            data = {
                'product': selected_prod,
                'date': datetime.strptime(self.date_var.get(), '%Y-%m-%d %H:%M'),
                'total_value': Decimal(self.value_var.get())
            }
            
            InventoryService.update_sale(self.selected_sale_id, **data)
            self.status_label.configure(text="Saved successfully!", text_color="green")
            self.load_sales()
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")

    def delete_sale(self):
        if self.selected_sale_id:
            try:
                InventoryService.delete_sale(self.selected_sale_id)
                self.status_label.configure(text="Deleted successfully!", text_color="green")
                self.selected_sale_id = None
                self.product_var.set("")
                self.date_var.set("")
                self.value_var.set("")
                self.load_sales()
            except Exception as e:
                self.status_label.configure(text=f"Error: {str(e)}", text_color="red")
        else:
            self.status_label.configure(text="No sale selected to delete.", text_color="orange")

    def refresh(self):
        """Called when database is switched or view is focused."""
        self.load_products()
        self.load_sales()
