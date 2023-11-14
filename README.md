# Portfolio Investment

The goal of this project is to build a simple Flask application that pulls stock data from Finviz and returns best Value or Growth Stocks for different choice of Sector or Index. The application also allows users to pick the stocks and returns optimal portofio based on their selections.

## Table of Contents

- [Portfolio Investment](#portfolio-investment)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Contributing](#contributing)
  - [License](#license)


## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/tkalden/stock-portfolio.git

2. Navigate to the project directory:
  
   ```bash
   cd stock-portfolio

3. Create and activate a virtual environment (optional but recommended):
  
   ```bash
    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    # On macOS and Linux
    python3 -m venv venv
    source venv/bin/activate

4. Install the dependencies from the requirements.txt file:
  
   ```bash
   pip install -r requirements.txt


5. Set the Flask app name (if not named app.py):
  
   ```bash
   # On Windows
    set FLASK_APP=main.py
   # On macOS and Linux
   export FLASK_APP=main.py

6. Set python path 

   ```bash
   # On macOS and Linux
   export PYTHONPATH=/path/to/project

7. Run the Flask app:
  
   ```bash
   flask run

8. In order to run google api used in this app, you need to set up local credentials using following link.Otherwise you will get errors when clicking on pages.
   https://cloud.google.com/docs/authentication/provide-credentials-adc#local-dev

## Usage
User can choose : Sector , Index and choice of investement (Growth vs. Value).
The application returns the stocks for that particular user inputs in descending order of strength.
User can select stocks returned from the application and build portfolio out of them. The optimization method will take care of returning best portfolio.

### Data Dictionary
``` 
{"P/E": "pe", 
"Fwd P/E" : "fpe",
"P/B": "pb", 
"P/C":"pc", 
"Dividend":"dividend", 
"PEG" : "peg",
"Insider Own" : "insider_own", 
"ROI":"roi",
"ROE":"roe",
"Beta" : "beta",
"Price" :"price"
}
```

### Strength Calculation
#### Value Stock
```
 if pb or pe or pc or fpe or peg  < avg value of sector
   strength =+1
 elif beta < 1
    strength =+1
 elif dividend > avg div
 strength =+1
```
#### Growth Stock

```
 if pb or pe or pc or fpe or peg  > avg value of sector
   strength =+1
 elif beta > 1
    strength =+1
 elif dividend < avg div
 strength =+1
```
### Weight Calculation

```
weight_{i} = strength_value_{i} / sum (strength_value) across all stocks

```
### Expected Return (ER) Calculation
```
ER_{i} = weight_{i} * roi_{i}
```

### Portfolio Total Return (PTR) Calculation 
```
TPR = sum (ER_{i}) for i = 1..n  where n is the total number of stocks in the portoflio
```

### Optimization Method:
Given the user provide desired expected return and threshold.The optimization Method returns the best portfolio by optimizing TPR.
Note: sometimes the expected return can be less than desired expected return. However the algorithm returns the maximum expected return for the different combination of stocks

## Further Analysis
For greater certainty about a stock's prospects, it's important to use a company's EPS Rating in conjunction with its Composite Rating, Relative Strength Rating and Accumulation/Distribution score. 
The expected return is oversimplified. The better approach is to analyze the expected return of each stock over the past 5 years and take statistical average. 
```
ER_{i} = Sum(ER_{j}) / n for j = 1..n  where n is total number of years
```
```
PR_{i} = weight_{i} * ER_{i} 
```
```
TPR = sum(PR_{i})  for i = 1..n  where n = total number of stocks
```

## Dependencies
```
List the dependencies required by your Flask app. You can generate this list from the requirements.txt file:

```bash
pip freeze > requirements.txt

Flask==2.1.0
gunicorn==20.1.0
pandas
numpy
asyncio
flask_toastr
finvizfinance
google-cloud-bigquery
db-dtypes
```

## Contributing

## License


```