# Component Stock Management System

A Django-based web application for managing electronic component stock with features for tracking component descriptions, values, manufacturers, and supplier part numbers.

## Features

- **Component Management**: Add, edit, view, and delete electronic components
- **Stock Tracking**: Monitor stock levels with low stock warnings
- **Search & Filter**: Find components quickly using search functionality
- **Dashboard**: Overview of total components, low stock, and out-of-stock items
- **Admin Interface**: Django admin interface for advanced management
- **Responsive UI**: Bootstrap-based responsive web interface

## Component Fields

- **Description**: Component description (e.g., "Resistor", "Capacitor")
- **Value**: Component value if applicable (e.g., "10kΩ", "100μF", "74HC00")
- **Manufacturer**: Component manufacturer
- **Supplier Part Number**: Supplier's part number
- **Quantity in Stock**: Current stock quantity
- **Minimum Stock Level**: Minimum level before reordering alert
- **Location**: Storage location (e.g., "Drawer A1", "Shelf B2")
- **Notes**: Additional notes about the component

## Installation

1. **Clone the repository** (if using version control):
   ```bash
   git clone <repository-url>
   cd Components
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On macOS/Linux
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser** (for admin access):
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

7. **Access the application**:
   - Main application: http://127.0.0.1:8000/
   - Admin interface: http://127.0.0.1:8000/admin/

## Usage

### Web Interface
- **Dashboard**: View stock overview and recent components
- **Components List**: Browse all components with search and pagination
- **Add Component**: Add new components to the inventory
- **Edit/Delete**: Manage existing components

### Admin Interface
- Access via `/admin/` for advanced component management
- Bulk operations and advanced filtering
- Export functionality

## Project Structure

```
Components/
├── component_stock/          # Django project settings
│   ├── __init__.py
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── components/              # Django app for component management
│   ├── __init__.py
│   ├── models.py           # Component data model
│   ├── views.py            # View functions
│   ├── forms.py            # Django forms
│   ├── admin.py            # Admin interface configuration
│   ├── apps.py             # App configuration
│   └── urls.py             # App URL patterns
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   └── components/         # Component-specific templates
├── static/                 # Static files (CSS, JS, images)
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

## Development

### Adding New Features
1. Modify models in `components/models.py`
2. Create and run migrations: `python manage.py makemigrations && python manage.py migrate`
3. Update views in `components/views.py`
4. Create/update templates in `templates/components/`
5. Update forms in `components/forms.py` if needed

### Database
- Uses SQLite by default for development
- Database file: `db.sqlite3`
- For production, update `DATABASES` setting in `component_stock/settings.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests for new functionality
5. Submit a pull request

## License

This project is open source and available under the MIT License.