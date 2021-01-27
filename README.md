# Mat.se

## Description
Extracts the following from the Mat.se API:
- number of products per category
- Percentage of Swedish products per category
- Top 5 best selling products per category, full data and in descending order

Results are stored in separate JSON files in "/tmp"
- "/tmp/number_of_products.json"
- "/tmp/percentage_swedish.json"
- "/tmp/top_5_products.json"

## Requirements
- Python 3.9+ (Most likely works with 3.6+)
- Pipenv https://pipenv.readthedocs.io
- Linux (Developed on Ubuntu 20.04)

## Usage
make run

## Install dependencies
make install

## Test
make test

## Coverage
make coverage
