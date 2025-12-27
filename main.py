from config.logging_config import setup_logging
import logging
from database import initialize_database, seed_example_data
from models import db
from gui.main_window import MainWindow
import customtkinter as ctk

def main():
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting InventoryManager...")

    # Initialize database on first run
    try:
        initialize_database()
        
        # Open connection for the app session
        db.connect()

        # Seed example data if needed
        seed_example_data()

        # Set up GUI
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        app = MainWindow()
        app.mainloop()

    except Exception as e:
        logger.error(f"Application crashed: {e}", exc_info=True)
    finally:
        # Close database connection when done
        if not db.is_closed():
            db.close()
        logger.info("InventoryManager closed.")


if __name__ == '__main__':
    main()
