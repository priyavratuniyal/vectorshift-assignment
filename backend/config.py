import os
from typing import Dict

# Base URLs
HUBSPOT_AUTH_URL = "https://app.hubspot.com/oauth/authorize"
HUBSPOT_TOKEN_URL = "https://api.hubspot.com/oauth/v1/token"
HUBSPOT_API_BASE = "https://api.hubspot.com/crm/v3"

# Client configurations
CLIENT_CONFIGS: Dict[str, Dict[str, str]] = {
    "hubspot": {
        "client_id": "c1ad28b1-6bbc-498b-be8f-27365d791b7c",
        "client_secret": "c513e563-69b3-45be-9135-fb251d04f06d",
        "redirect_uri": "http://localhost:8000/integrations/hubspot/oauth2callback",
        "scopes": "crm.objects.contacts.read crm.objects.companies.read crm.objects.deals.read"
    },
    "notion": {
        "client_id": "XXX",
        "client_secret": "XXX",
        "redirect_uri": "http://localhost:8000/integrations/notion/oauth2callback"
    },
    "airtable": {
        "client_id": "XXX",
        "client_secret": "XXX",
        "redirect_uri": "http://localhost:8000/integrations/airtable/oauth2callback"
    }
}

# Redis configuration
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# API configuration
CORS_ORIGINS = [
    "http://localhost:3000",  # React app address
]

# State token expiration (in seconds)
STATE_TOKEN_EXPIRATION = 600  # 10 minutes
