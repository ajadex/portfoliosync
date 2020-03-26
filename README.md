# Overview

Synchronizes an excel with data from a broker

## Dependencies

Python 3x

```bash
pip3 install beautifulsoup4
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

In order to connect to google we need to enable API access to the google sheets. Go here: https://developers.google.com/sheets/api/quickstart/python
and click "Enable the Google Sheets API".

In resulting dialog click DOWNLOAD CLIENT CONFIGURATION and save the file credentials.json in this directory.

## Run

```bash
export WORKSHEET_ID=[google worksheet id]
export TW_USER=[username]
export TW_PASSWORD=[password]

python3 sync.py
```

if you have RobinHood in addition to Tastyworks, export the vars and run it like this:

```bash
export WORKSHEET_ID=[google worksheet id]
export TW_USER=[username]
export TW_PASSWORD=[password]
export RH_USER=[username]
export RH_PASSWORD=[password]

python3 sync.py
```

if TW_USER or TW_PASSWORD is not defined it won't download data from Tastyworks. Similarly if no RH_USER or RH_PASSWORD is defined no data is retrieved from Robinhood.