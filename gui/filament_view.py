import customtkinter as ctk
from services.inventory_service import InventoryService
from decimal import Decimal

class FilamentView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.selected_filament_id = None
        
        # Grid layout: Left (List) and Right (Details)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Left Side: List ---
        self.list_frame = ctk.CTkFrame(self)
        self.list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.list_label = ctk.CTkLabel(self.list_frame, text="Filament List", font=ctk.CTkFont(size=16, weight="bold"))
        self.list_label.pack(pady=10)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self.list_frame, label_text="Available Filaments")
        self.scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.add_btn = ctk.CTkButton(self.list_frame, text="Add New Filament", command=self.prepare_new_filament)
        self.add_btn.pack(pady=10)
        
        # --- Right Side: Details ---
        self.details_frame = ctk.CTkFrame(self)
        self.details_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.details_label = ctk.CTkLabel(self.details_frame, text="Filament Details", font=ctk.CTkFont(size=16, weight="bold"))
        self.details_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Form fields
        self.brand_var = ctk.StringVar()
        self.material_var = ctk.StringVar()
        self.color_var = ctk.StringVar()
        self.cost_var = ctk.StringVar()
        self.grams_roll_var = ctk.StringVar(value="1000")
        self.grams_rem_var = ctk.StringVar(value="1000")
        self.rolls_stock_var = ctk.StringVar(value="0")
        
        fields = [
            ("Brand:", self.brand_var),
            ("Material:", self.material_var),
            ("Color:", self.color_var),
            ("Cost per Roll ($):", self.cost_var),
            ("Grams per Roll:", self.grams_roll_var),
            ("Grams Remaining:", self.grams_rem_var),
            ("Rolls in Stock:", self.rolls_stock_var),
        ]
        
        for i, (label_text, var) in enumerate(fields):
            lbl = ctk.CTkLabel(self.details_frame, text=label_text)
            lbl.grid(row=i+1, column=0, padx=10, pady=5, sticky="e")
            entry = ctk.CTkEntry(self.details_frame, textvariable=var)
            entry.grid(row=i+1, column=1, padx=10, pady=5, sticky="w")
            
        self.save_btn = ctk.CTkButton(self.details_frame, text="Save Changes", command=self.save_filament)
        self.save_btn.grid(row=len(fields)+1, column=0, pady=20)
        
        self.delete_btn = ctk.CTkButton(self.details_frame, text="Delete Filament", fg_color="red", hover_color="darkred", command=self.delete_filament)
        self.delete_btn.grid(row=len(fields)+1, column=1, pady=20)
        
        self.status_label = ctk.CTkLabel(self.details_frame, text="")
        self.status_label.grid(row=len(fields)+2, column=0, columnspan=2)
        
        self.load_filaments()

    def load_filaments(self):
        # Clear current list
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        try:
            filaments = InventoryService.get_all_filaments()
            for fil in filaments:
                btn = ctk.CTkButton(
                    self.scrollable_frame, 
                    text=f"{fil.brand or 'Generic'} {fil.color} {fil.material}",
                    fg_color="transparent",
                    text_color=("gray10", "gray90"),
                    hover_color=("gray70", "gray30"),
                    anchor="w",
                    command=lambda f=fil: self.select_filament(f)
                )
                btn.pack(fill="x", padx=5, pady=2)
        except Exception as e:
            print(f"Error loading filaments: {e}")

    def select_filament(self, filament):
        self.selected_filament_id = filament.id
        self.brand_var.set(filament.brand or "")
        self.material_var.set(filament.material)
        self.color_var.set(filament.color)
        self.cost_var.set(str(filament.cost_per_roll))
        self.grams_roll_var.set(str(filament.grams_per_roll))
        self.grams_rem_var.set(str(filament.grams_remaining))
        self.rolls_stock_var.set(str(filament.rolls_in_stock))
        self.status_label.configure(text=f"Editing: {filament}", text_color=("gray10", "gray90"))

    def prepare_new_filament(self):
        self.selected_filament_id = None
        self.brand_var.set("")
        self.material_var.set("")
        self.color_var.set("")
        self.cost_var.set("")
        self.grams_roll_var.set("1000")
        self.grams_rem_var.set("1000")
        self.rolls_stock_var.set("0")
        self.status_label.configure(text="Adding New Filament", text_color=("gray10", "gray90"))

    def save_filament(self):
        try:
            data = {
                'brand': self.brand_var.get(),
                'material': self.material_var.get(),
                'color': self.color_var.get(),
                'cost_per_roll': Decimal(self.cost_var.get() or "0"),
                'grams_per_roll': Decimal(self.grams_roll_var.get() or "1000"),
                'grams_remaining': Decimal(self.grams_rem_var.get() or "1000"),
                'rolls_in_stock': int(self.rolls_stock_var.get() or "0")
            }
            
            InventoryService.save_filament(self.selected_filament_id, **data)
            self.status_label.configure(text="Saved successfully!", text_color="green")
            self.load_filaments()
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")

    def delete_filament(self):
        if self.selected_filament_id:
            try:
                InventoryService.delete_filament(self.selected_filament_id)
                self.status_label.configure(text="Deleted successfully!", text_color="green")
                self.prepare_new_filament()
                self.load_filaments()
            except Exception as e:
                self.status_label.configure(text=f"Error: {str(e)}", text_color="red")
        else:
            self.status_label.configure(text="No filament selected to delete.", text_color="orange")

    def refresh(self):
        """Called when database is switched or view is focused."""
        self.load_filaments()
        # Only prepare new if nothing is selected
        if self.selected_filament_id is None:
            self.prepare_new_filament()
