# python-adform
Very simple AdForm Wrapper for Python

### Project description:
Self-built wrapper for the AdForm API using *requests* to send get and post requests and *json* for parsing response.
Included base class with authorization methods, as well as a few classes to get different types of data back.

### Usage:
- Either use adform.py as a base class to build up your own methods
- Or try in terminal: `$ python3 example_lineitemreport.py` 
**If ran from terminal, you need to enter your credentials in the example_lineitemreport.py before!!!**

### Features:
- Client authorization with client credentials method (needs client ID and client Secret from AdForm)
- Get all campaigns of the account and return a formatted data structure of the results
- Get all campaigns filtered by status or a given string
- Get all orders of a campaign and return a formatted data structure of the results
- Get budgets for each lineitem

