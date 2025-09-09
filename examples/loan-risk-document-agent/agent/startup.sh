#!/bin/bash

# Create service account file from environment variable
if [ -n "$GOOGLE_APPLICATION_CREDENTIALS_JSON" ]; then
    echo "$GOOGLE_APPLICATION_CREDENTIALS_JSON" > /tmp/service-account.json
    export GOOGLE_APPLICATION_CREDENTIALS=/tmp/service-account.json
fi

# Start the Flask application
exec python app.py
