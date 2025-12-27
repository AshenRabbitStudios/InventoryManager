from database import initialize_database
from models import db
from gui.main_window import MainWindow
import customtkinter as ctk

def main():
    # Initialize database on first run
    initialize_database()

    # Set up GUI
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = MainWindow()
    app.mainloop()

    # Close database connection when done
    db.close()


if __name__ == '__main__':
    main()
