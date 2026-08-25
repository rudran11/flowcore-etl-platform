# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""
FlowCore SDK Client.

Provides the foundational client object for HTTP interactions with the Server.
"""

class FlowCoreClient:
    """
    Main SDK Client for interacting with the FlowCore API.
    
    Attributes:
        base_url (str): The root URL of the FlowCore Server.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the FlowCore SDK client.
        
        Args:
            base_url (str): The server URL.
        """
        self.base_url = base_url

    def get_health(self) -> dict:
        """
        Stub method to check platform health.
        
        Returns:
            dict: Health status payload.
        """
        import requests
        resp = requests.get(f"{self.base_url}/health")
        return resp.json()

    def cancel_run(self, run_id: str, token: str) -> dict:
        """
        Cancels an execution run.
        """
        import requests
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.post(f"{self.base_url}/api/v1/runs/{run_id}/cancel", headers=headers)
        resp.raise_for_status()
        return resp.json()

    def trigger_webhook(self, webhook_id: str, secret_key: str, payload: dict) -> dict:
        """
        Triggers a webhook pipeline execution with HMAC validation.
        """
        import requests
        import time
        import hmac
        import hashlib
        import json

        timestamp = str(int(time.time()))
        body_str = json.dumps(payload)
        payload_to_sign = f"{timestamp}:{body_str}".encode('utf-8')
        
        signature = hmac.new(
            key=secret_key.encode('utf-8'),
            msg=payload_to_sign,
            digestmod=hashlib.sha256
        ).hexdigest()

        headers = {
            "X-FlowCore-Timestamp": timestamp,
            "X-FlowCore-Signature": signature,
            "Content-Type": "application/json"
        }
        resp = requests.post(
            f"{self.base_url}/api/v1/webhooks/{webhook_id}",
            headers=headers,
            data=body_str
        )
        resp.raise_for_status()
        return resp.json()
