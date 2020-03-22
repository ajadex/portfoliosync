# Overview

Synchronizes an excel with data from a broker

## Dependencies

Python 3x

```bash
pip3 install beautifulsoup4
pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## Run

```bash
export WORKSHEET_ID=[google worksheet id]
export TW_USERNAME=[username]
export TW_PASSWORD=[password]

python3 sync.py
```
