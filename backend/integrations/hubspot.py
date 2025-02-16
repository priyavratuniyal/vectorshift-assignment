import json
import time
from datetime import datetime
from typing import List, Dict, Any
import httpx
from fastapi import Request
from logger import log_error, log_integration_event

from config import HUBSPOT_API_BASE
from integrations.base_integration import BaseIntegration
from integrations.integration_item import IntegrationItem

class HubSpotIntegration(BaseIntegration):
    def __init__(self):
        super().__init__("hubspot")

    async def authorize_hubspot(self, user_id: str, org_id: str) -> str:
        """Generate HubSpot authorization URL."""
        return await self.authorize(user_id, org_id)

    async def oauth2callback_hubspot(self, request: Request):
        """Handle HubSpot OAuth callback."""
        return await self.oauth2callback(request)

    async def get_hubspot_credentials(self, user_id: str, org_id: str):
        """Retrieve HubSpot credentials."""
        return await self.get_credentials(user_id, org_id)

    async def get_items(self, credentials: str) -> List[IntegrationItem]:
        """
        Retrieve and format HubSpot items.
        We'll fetch contacts, companies, and deals from HubSpot's CRM.
        """
        start_time = time.time()
        try:
            credentials_dict = json.loads(credentials)
            access_token = credentials_dict.get("access_token")
            
            if not access_token:
                raise ValueError("No access token found in credentials")

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            }

            self.logger.info("Starting HubSpot API calls for data retrieval")
            async with httpx.AsyncClient() as client:
                # Fetch contacts, companies, and deals in parallel
                api_start_time = time.time()
                responses = await client.get(
                    f"{HUBSPOT_API_BASE}/objects/contacts",
                    headers=headers,
                    params={"limit": 100}
                ), await client.get(
                    f"{HUBSPOT_API_BASE}/objects/companies",
                    headers=headers,
                    params={"limit": 100}
                ), await client.get(
                    f"{HUBSPOT_API_BASE}/objects/deals",
                    headers=headers,
                    params={"limit": 100}
                )
                api_duration = time.time() - api_start_time
                self.logger.info(f"HubSpot API calls completed in {api_duration * 1000:.2f}ms")

            items: List[IntegrationItem] = []
            stats = {
                "contacts": 0,
                "companies": 0,
                "deals": 0,
                "errors": 0
            }

            # Process contacts
            contacts_response = responses[0]
            if contacts_response.status_code == 200:
                contacts_data = contacts_response.json()
                for contact in contacts_data.get("results", []):
                    try:
                        items.append(self._create_contact_item(contact))
                        stats["contacts"] += 1
                    except Exception as e:
                        stats["errors"] += 1
                        log_error(
                            self.logger,
                            e,
                            {
                                "operation": "process_contact",
                                "contact_id": contact.get("id")
                            }
                        )

            # Process companies
            companies_response = responses[1]
            if companies_response.status_code == 200:
                companies_data = companies_response.json()
                for company in companies_data.get("results", []):
                    try:
                        items.append(self._create_company_item(company))
                        stats["companies"] += 1
                    except Exception as e:
                        stats["errors"] += 1
                        log_error(
                            self.logger,
                            e,
                            {
                                "operation": "process_company",
                                "company_id": company.get("id")
                            }
                        )

            # Process deals
            deals_response = responses[2]
            if deals_response.status_code == 200:
                deals_data = deals_response.json()
                for deal in deals_data.get("results", []):
                    try:
                        items.append(self._create_deal_item(deal))
                        stats["deals"] += 1
                    except Exception as e:
                        stats["errors"] += 1
                        log_error(
                            self.logger,
                            e,
                            {
                                "operation": "process_deal",
                                "deal_id": deal.get("id")
                            }
                        )

            duration = time.time() - start_time
            log_integration_event(
                self.logger,
                "GET_ITEMS_COMPLETE",
                self.integration_name,
                "system",  # No user context in this method
                "system",  # No org context in this method
                {
                    "duration_ms": duration * 1000,
                    "api_duration_ms": api_duration * 1000,
                    "total_items": len(items),
                    "stats": stats
                }
            )

            return items

        except Exception as e:
            log_error(
                self.logger,
                e,
                {
                    "operation": "get_items",
                    "integration": self.integration_name
                }
            )
            raise

    def _create_contact_item(self, contact: Dict[str, Any]) -> IntegrationItem:
        """Create IntegrationItem for HubSpot contact."""
        properties = contact.get("properties", {})
        return self.create_integration_item(
            id=contact.get("id"),
            type="contact",
            name=f"{properties.get('firstname', '')} {properties.get('lastname', '')}".strip() or "Unnamed Contact",
            creation_time=datetime.fromisoformat(properties.get("createdate", "").replace("Z", "+00:00"))
            if properties.get("createdate")
            else None,
            last_modified_time=datetime.fromisoformat(properties.get("lastmodifieddate", "").replace("Z", "+00:00"))
            if properties.get("lastmodifieddate")
            else None,
            url=f"https://app.hubspot.com/contacts/{properties.get('hubspot_owner_id')}/contact/{contact.get('id')}"
            if properties.get("hubspot_owner_id")
            else None
        )

    def _create_company_item(self, company: Dict[str, Any]) -> IntegrationItem:
        """Create IntegrationItem for HubSpot company."""
        properties = company.get("properties", {})
        return self.create_integration_item(
            id=company.get("id"),
            type="company",
            name=properties.get("name", "Unnamed Company"),
            creation_time=datetime.fromisoformat(properties.get("createdate", "").replace("Z", "+00:00"))
            if properties.get("createdate")
            else None,
            last_modified_time=datetime.fromisoformat(properties.get("lastmodifieddate", "").replace("Z", "+00:00"))
            if properties.get("lastmodifieddate")
            else None,
            url=f"https://app.hubspot.com/contacts/{properties.get('hubspot_owner_id')}/company/{company.get('id')}"
            if properties.get("hubspot_owner_id")
            else None
        )

    def _create_deal_item(self, deal: Dict[str, Any]) -> IntegrationItem:
        """Create IntegrationItem for HubSpot deal."""
        properties = deal.get("properties", {})
        return self.create_integration_item(
            id=deal.get("id"),
            type="deal",
            name=properties.get("dealname", "Unnamed Deal"),
            creation_time=datetime.fromisoformat(properties.get("createdate", "").replace("Z", "+00:00"))
            if properties.get("createdate")
            else None,
            last_modified_time=datetime.fromisoformat(properties.get("lastmodifieddate", "").replace("Z", "+00:00"))
            if properties.get("lastmodifieddate")
            else None,
            url=f"https://app.hubspot.com/contacts/{properties.get('hubspot_owner_id')}/deal/{deal.get('id')}"
            if properties.get("hubspot_owner_id")
            else None
        )

# Create a singleton instance
hubspot_integration = HubSpotIntegration()

# Export the instance methods
authorize_hubspot = hubspot_integration.authorize_hubspot
oauth2callback_hubspot = hubspot_integration.oauth2callback_hubspot
get_hubspot_credentials = hubspot_integration.get_hubspot_credentials
get_items_hubspot = hubspot_integration.get_items
