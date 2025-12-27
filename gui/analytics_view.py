import customtkinter as ctk

class AnalyticsView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.label = ctk.CTkLabel(self, text="Sales & Analytics", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=20)
        
        self.info_label = ctk.CTkLabel(self, text="View sales history and inventory predictions.")
        self.info_label.pack(pady=10)
