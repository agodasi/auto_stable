import flet as ft
from core.config_manager import ConfigManager
from core.api_client import SDForgeAPIClient
from gui.main_view import MainView

async def main(page: ft.Page):
    config_manager = ConfigManager()
    
    # Base page settings
    page.title = "Stable Diffusion Forge Queue Manager"
    page.window.width = 1100
    page.window.height = 700
    page.window.min_width = 900
    page.window.min_height = 600
    
    # Initialize API Client
    api_url = config_manager.config.get("api_url", "http://127.0.0.1:7860")
    api_client = SDForgeAPIClient(api_url)
    
    # Default Theme applying
    theme_val = config_manager.config.get("theme", "Dark")
    if theme_val == "Light":
        page.theme_mode = ft.ThemeMode.LIGHT
    elif theme_val == "Dark":
        page.theme_mode = ft.ThemeMode.DARK
    else:
        page.theme_mode = ft.ThemeMode.SYSTEM
        
    # Main View rendering
    main_view = MainView(page, config_manager, api_client)
    page.add(main_view.build())

if __name__ == "__main__":
    ft.run(main)
