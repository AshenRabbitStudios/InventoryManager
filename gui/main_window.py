import customtkinter as ctk
from .overview_view import OverviewView
from .filament_view import FilamentView
from .product_view import ProductView
from .sales_view import SalesView
from .analytics_view import AnalyticsView
from models.base import set_database, db
from database import initialize_database, seed_example_data
import os

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("InventoryManager")
        self.geometry("1100x700")

        # set grid layout 1x2
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # create navigation frame
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1)

        self.navigation_frame_label = ctk.CTkLabel(self.navigation_frame, text="InventoryManager",
                                                             compound="left", font=ctk.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        self.overview_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Overview",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.overview_button_event)
        self.overview_button.grid(row=1, column=0, sticky="ew")

        self.filament_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Filaments",
                                                   fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                   anchor="w", command=self.filament_button_event)
        self.filament_button.grid(row=2, column=0, sticky="ew")

        self.product_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Products",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.product_button_event)
        self.product_button.grid(row=3, column=0, sticky="ew")

        self.sales_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Sales",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.sales_button_event)
        self.sales_button.grid(row=4, column=0, sticky="ew")

        self.analytics_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Analytics",
                                                      fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                                      anchor="w", command=self.analytics_button_event)
        self.analytics_button.grid(row=5, column=0, sticky="ew")

        self.appearance_mode_menu = ctk.CTkOptionMenu(self.navigation_frame, values=["Light", "Dark", "System"],
                                                                command=self.change_appearance_mode_event)
        self.appearance_mode_menu.grid(row=7, column=0, padx=20, pady=20, sticky="s")

        # create frames
        self.overview_frame = OverviewView(self, corner_radius=0, fg_color="transparent")
        self.filament_frame = FilamentView(self, corner_radius=0, fg_color="transparent")
        self.product_frame = ProductView(self, corner_radius=0, fg_color="transparent")
        self.sales_frame = SalesView(self, corner_radius=0, fg_color="transparent")
        self.analytics_frame = AnalyticsView(self, corner_radius=0, fg_color="transparent")

        # dataset selection in top right of navigation or main area?
        # User said "upper right". Let's put it in a small frame at the top of the main area or just as a widget.
        # Given current layout 1x2, main area is column 1.
        
        self.top_bar = ctk.CTkFrame(self, height=40, corner_radius=0)
        self.top_bar.grid(row=0, column=1, sticky="new")
        self.top_bar.grid_columnconfigure(0, weight=1)

        initial_dataset = "Production" if os.environ.get('INVENTORYMANAGER_ENV') != 'test' else "Test"
        self.dataset_menu = ctk.CTkOptionMenu(self.top_bar, values=["Production", "Test"],
                                               command=self.change_dataset_event)
        self.dataset_menu.set(initial_dataset)
        self.dataset_menu.grid(row=0, column=1, padx=20, pady=5, sticky="e")

        # Adjust frame grids to be below top bar
        # Actually it's better if the frames themselves are placed starting from row 0 and we just push them down 
        # OR we use another grid row. Let's use row 0 for top bar and row 1 for content in column 1.
        self.grid_rowconfigure(0, weight=0) # for top bar
        self.grid_rowconfigure(1, weight=1) # for content
        
        # Re-grid navigation frame to span both rows
        self.navigation_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")

        # select default frame
        self.select_frame_by_name("overview")

    def select_frame_by_name(self, name):
        # set button color for selected button
        self.overview_button.configure(fg_color=("gray75", "gray25") if name == "overview" else "transparent")
        self.filament_button.configure(fg_color=("gray75", "gray25") if name == "filaments" else "transparent")
        self.product_button.configure(fg_color=("gray75", "gray25") if name == "products" else "transparent")
        self.sales_button.configure(fg_color=("gray75", "gray25") if name == "sales" else "transparent")
        self.analytics_button.configure(fg_color=("gray75", "gray25") if name == "analytics" else "transparent")

        # show selected frame
        if name == "overview":
            self.overview_frame.grid(row=1, column=1, sticky="nsew")
            self.overview_frame.refresh()
        else:
            self.overview_frame.grid_forget()
        if name == "filaments":
            self.filament_frame.grid(row=1, column=1, sticky="nsew")
            self.filament_frame.refresh()
        else:
            self.filament_frame.grid_forget()
        if name == "products":
            self.product_frame.grid(row=1, column=1, sticky="nsew")
            self.product_frame.refresh()
        else:
            self.product_frame.grid_forget()
        if name == "sales":
            self.sales_frame.grid(row=1, column=1, sticky="nsew")
            self.sales_frame.refresh()
        else:
            self.sales_frame.grid_forget()
        if name == "analytics":
            self.analytics_frame.grid(row=1, column=1, sticky="nsew")
            self.analytics_frame.refresh()
        else:
            self.analytics_frame.grid_forget()

    def overview_button_event(self):
        self.select_frame_by_name("overview")

    def filament_button_event(self):
        self.select_frame_by_name("filaments")

    def product_button_event(self):
        self.select_frame_by_name("products")

    def sales_button_event(self):
        self.select_frame_by_name("sales")

    def analytics_button_event(self):
        self.select_frame_by_name("analytics")

    def change_appearance_mode_event(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

    def change_dataset_event(self, new_dataset):
        # Close current connection
        if not db.is_closed():
            db.close()
        
        # Switch database
        env = "test" if new_dataset == "Test" else "prod"
        set_database(env)
        
        # Re-initialize (ensure tables exist)
        initialize_database()
        
        # Re-open connection for the app session
        db.connect()

        # Seed example data if needed
        seed_example_data()
        
        # Refresh current view
        self.overview_frame.refresh()
        self.filament_frame.refresh()
        self.product_frame.refresh()
        self.sales_frame.refresh()
        self.analytics_frame.refresh()
        
        print(f"Switched to {new_dataset} database.")
