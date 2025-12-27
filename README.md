# InventoryManager

A professional desktop application for managing 3D printing filament inventory, products, and sales. Built with Python, CustomTkinter, and Peewee ORM.

## Features

- **Filament Management**: Track filament usage, stock levels, and costs.
- **Product Management**: Define products with multi-part components and filament requirements.
- **Sales Tracking**: Record sales and automatically update inventory levels.
- **Analytics**: Visualize sales data and inventory trends.
- **Environment Switching**: Easily switch between Production and Test databases for safe experimentation.

## Tech Stack

- **GUI**: [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- **Database**: [Peewee ORM](http://docs.peewee-orm.com/) with SQLite
- **Visualization**: [Matplotlib](https://matplotlib.org/)
- **Language**: Python 3.10+

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/inventory-manager.git
   cd inventory-manager
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```

## Project Structure

- `config/`: Configuration settings and constants.
- `database/`: Database initialization and seeding scripts.
- `gui/`: View components and main window layout.
- `models/`: Database models and schema definitions.
- `services/`: Business logic and data processing services.
- `tests/`: Automated tests.

## Development

### Running Tests
To run the automated test suite, use the following command from the project root:

```powershell
$env:PYTHONPATH="."; pytest
```

Or using the standard Python module approach:
```bash
python -m pytest
```

### Code Quality
This project uses `pylint` and `flake8` for linting. You can run them to ensure code quality:
```bash
pylint services models
flake8 .
```

### Future Enhancements
- [ ] Prediction service for inventory forecasting.
- [ ] Export functionality for reports (CSV/PDF).
- [ ] Multi-user support or cloud database sync.
