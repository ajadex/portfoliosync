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
export TW_USERNAME=[username]
export TW_PASSWORD=[password]

python3 sync.py
```
