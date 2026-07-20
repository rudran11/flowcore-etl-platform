# Copyright (c) 2026 Rudran
# Licensed under the MIT License.
# See LICENSE file in the project root for full license information.

"""
Main Entrypoint for FlowCore Server.

Provides the foundational FastAPI application and health check endpoint.
No business logic is implemented yet.
"""

from fastapi import FastAPI

app = FastAPI(
    title="FlowCore API",
    description="Enterprise Metadata-Driven ETL Platform Control Plane",
    version="1.0.0",
)

@app.get("/health")
def health_check():
    """
    Basic health check endpoint.
    """
    return {"status": "ok", "service": "flowcore-server"}
