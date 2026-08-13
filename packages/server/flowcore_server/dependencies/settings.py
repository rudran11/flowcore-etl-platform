from fastapi import Depends
from flowcore_server.services.settings import SettingsService

def get_settings_service() -> SettingsService:
    return SettingsService()
