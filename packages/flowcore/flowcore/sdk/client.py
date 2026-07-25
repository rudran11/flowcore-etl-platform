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
        return {"status": "ok", "service": "flowcore-sdk"}
