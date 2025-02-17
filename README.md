# ASK API Wrapper

A Python wrapper for the Kosovo Agency of Statistics (ASK) API that provides easy access to statistical data about Kosovo.

## Features

- Interactive navigation through the ASK data hierarchy
- Easy data retrieval with pandas DataFrame output
- Support for multiple languages (Albanian and English)
- Municipality name/code mapping
- Flexible date range queries
- Tree visualization of the API structure

## Project Structure

```
.
├── README.md
├── ask_api.py      # Main API wrapper class
├── main.py         # Example usage and implementation
├── marriages.py      # Interactive visualization of marriages by municipality
├── marriages_monthly_pattern.py  # Analysis of monthly marriage patterns
└── check_data_quality.py   # Data quality validation tools
```

## Installation

### Requirements
- Python 3.6+
- pandas
- requests

Install the required packages: 

```bash
pip install pandas requests
```

## Quick Start

1. Clone the repository:

```bash
git clone [repository-url]
cd ask-api-wrapper
```

2. Run the example script:

```bash
python main.py
```

This will:
- Start an interactive navigation through the ASK data structure
- Allow you to select a dataset
- Show you how to query the data
- Demonstrate basic data analysis

## Usage

### Basic Usage

```python
from ask_api import ASK

# Initialize the client
ask = ASK(lang='sq')  # 'sq' for Albanian, 'en' for English

# Interactive navigation to find your dataset
path = ask.navigate()

# Once you've found your dataset, you can use the path directly
ask.go_down(*path)

# Query data for specific municipalities and time periods
ask.set_query(
    municipalities=["Prishtinë", "Prizren"],
    start_date="2023-01",
    end_date="2023-12"
)

# Get data as a pandas DataFrame
df = ask.get_data_as_df()

# Basic analysis
print("\nMarriages by Municipality:")
print(df.groupby('Municipality')['Marriages'].agg(['count', 'mean', 'sum']))

# Export to CSV
df.to_csv('statistics.csv', index=False)
```

### Navigation Options

1. View the API structure:
```python
ask.print_navigation_tree(max_depth=3)
```

2. Interactive navigation:
```python
path = ask.navigate()  # Returns the path to your selected dataset
```

3. Direct navigation (if you know the path):
```python
ask.go_down('Population', 'Marriages and divorces', 'Marriages')
```

### Query Options

You can query data in multiple ways:

1. By specific months:
```python
ask.set_query(
    municipalities=["Prishtinë", "Prizren"],
    months=["2024M01", "2024M02"]
)
```

2. By entire year:
```python
ask.set_query(
    municipalities="Gjakovë",
    year=2023
)
```

3. By date range:
```python
ask.set_query(
    municipalities=["Prishtinë", "Prizren"],
    start_date="2023-01",
    end_date="2023-12"
)
```

## Available Methods

- `navigate()`: Interactive navigation through the API structure
- `print_navigation_tree(max_depth)`: Visualize the API structure
- `set_query()`: Set query parameters for data retrieval
- `get_data_as_df()`: Get data as pandas DataFrame
- `get_available_municipalities()`: List available municipalities
- `get_available_months()`: List available months for current dataset

## Data Format

The returned DataFrame includes:
- `Date`: Datetime of the observation
- `Municipality_Code`: Municipality code
- `Municipality`: Municipality name
- `Marriages`: Number of marriages (or other metric depending on dataset)

## Error Handling

The wrapper includes error handling for:
- Invalid municipality names
- Failed API requests
- Missing data points
- Navigation errors

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
