import customtkinter as ctk

class ProductView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.label = ctk.CTkLabel(self, text="Product Management", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.pack(pady=20)
        
        self.info_label = ctk.CTkLabel(self, text="Manage your products and their parts here.")
        self.info_label.pack(pady=10)
