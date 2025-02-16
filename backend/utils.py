import json
import secrets
from typing import Any, Dict, Optional
from fastapi import HTTPException
import base64
import httpx

from redis_client import add_key_value_redis, get_value_redis, delete_key_redis
from config import STATE_TOKEN_EXPIRATION, CLIENT_CONFIGS

async def generate_and_store_state(integration: str, user_id: str, org_id: str) -> str:
    """Generate and store state token for OAuth flow."""
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }
    encoded_state = json.dumps(state_data)
    await add_key_value_redis(
        f'{integration}_state:{org_id}:{user_id}',
        encoded_state,
        expire=STATE_TOKEN_EXPIRATION
    )
    return encoded_state

async def validate_state(integration: str, encoded_state: str) -> Dict[str, str]:
    """Validate state token from OAuth callback."""
    try:
        state_data = json.loads(encoded_state)
        original_state = state_data.get('state')
        user_id = state_data.get('user_id')
        org_id = state_data.get('org_id')

        if not all([original_state, user_id, org_id]):
            raise HTTPException(status_code=400, detail='Invalid state data.')

        saved_state = await get_value_redis(f'{integration}_state:{org_id}:{user_id}')
        if not saved_state or original_state != json.loads(saved_state).get('state'):
            raise HTTPException(status_code=400, detail='State does not match.')

        return state_data
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail='Invalid state format.')

def get_basic_auth_header(integration: str) -> str:
    """Generate Basic Auth header for OAuth token requests."""
    client_id = CLIENT_CONFIGS[integration]["client_id"]
    client_secret = CLIENT_CONFIGS[integration]["client_secret"]
    credentials = f"{client_id}:{client_secret}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"

async def exchange_code_for_token(
    integration: str,
    code: str,
    additional_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Exchange authorization code for access token."""
    config = CLIENT_CONFIGS[integration]
    token_url = {
        "hubspot": "https://api.hubspot.com/oauth/v1/token",
        "notion": "https://api.notion.com/v1/oauth/token",
        "airtable": "https://airtable.com/oauth/v1/token"
    }.get(integration)

    if not token_url:
        raise HTTPException(status_code=400, detail=f'Unsupported integration: {integration}')

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": config["redirect_uri"],
        **(additional_params or {})
    }

    headers = {
        "Authorization": get_basic_auth_header(integration),
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, json=data, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Token exchange failed: {response.text}"
            )
        
        return response.json()

def recursive_dict_search(data: Dict[str, Any], target_key: str) -> Optional[Any]:
    """Recursively search for a key in a dictionary of dictionaries."""
    if target_key in data:
        return data[target_key]

    for value in data.values():
        if isinstance(value, dict):
            result = recursive_dict_search(value, target_key)
            if result is not None:
                return result
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    result = recursive_dict_search(item, target_key)
                    if result is not None:
                        return result
    return None

async def store_credentials(integration: str, user_id: str, org_id: str, credentials: Dict[str, Any]) -> None:
    """Store OAuth credentials in Redis."""
    await add_key_value_redis(
        f'{integration}_credentials:{org_id}:{user_id}',
        json.dumps(credentials),
        expire=STATE_TOKEN_EXPIRATION
    )

async def get_credentials(integration: str, user_id: str, org_id: str) -> Dict[str, Any]:
    """Retrieve OAuth credentials from Redis."""
    credentials = await get_value_redis(f'{integration}_credentials:{org_id}:{user_id}')
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    
    credentials_dict = json.loads(credentials)
    if not credentials_dict:
        raise HTTPException(status_code=400, detail='Invalid credentials format.')
    
    await delete_key_redis(f'{integration}_credentials:{org_id}:{user_id}')
    return credentials_dict
