import flet as ft
from core.i18n import t
from core.queue_manager import QueueManager

class MainView:
    def __init__(self, page: ft.Page, config_manager, api_client):
        self.page = page
        self.config_manager = config_manager
        self.api_client = api_client
        
        self.last_generated_prompt = self.config_manager.queue_state.get("last_finished_prompt", "")
        self.queue_cards = []
        
        # UI Components
        self.preview_image = ft.Image(src=None, fit=ft.ImageFit.CONTAIN if hasattr(ft, 'ImageFit') else "contain", expand=True, visible=False)
        self.preview_placeholder = ft.Container(
            content=ft.Text(t("lbl_image_preview"), color="grey500"),
            alignment=ft.Alignment(0, 0),
            bgcolor="grey900" if self.page.theme_mode == ft.ThemeMode.DARK else "blue50",
            border_radius=10,
            expand=True
        )
        
        self.progress_bar = ft.ProgressBar(value=0, width=400, visible=False)
        self.status_text = ft.Text(t("lbl_status_idle"), size=14)
        
        self.btn_generate = ft.ElevatedButton(
            t("btn_generate"),
            bgcolor="green700",
            color="white",
            on_click=self.toggle_generation,
            height=50,
            expand=True
        )
        
        self.queue_list = ft.ListView(expand=True, spacing=10, auto_scroll=False)
        
        self.setup_ui()
        self.load_queue_from_state()

    def load_queue_from_state(self):
        saved_queue = self.config_manager.queue_state.get("queue", [])
        for item in saved_queue:
            self.add_queue_card(item.get("prompt", ""), save=False)

    def save_current_queue_state(self):
        queue_data = []
        for card_data in self.queue_cards:
            text = card_data["textfield"].value.strip()
            queue_data.append({"prompt": text})
        self.config_manager.queue_state["queue"] = queue_data
        self.config_manager.save_queue_state()

    def add_queue_card(self, initial_text="", save=True):
        card_id = len(self.queue_cards)
        
        tf = ft.TextField(
            value=initial_text,
            multiline=True,
            min_lines=2,
            max_lines=4,
            expand=True,
            on_blur=lambda e: self.save_current_queue_state()
        )
        
        def remove_card(e):
            self.queue_list.controls.remove(card_container)
            self.queue_cards = [c for c in self.queue_cards if c["id"] != card_id]
            self.save_current_queue_state()
            self.page.update()
            
        header = ft.Row([
            ft.Text(t("lbl_queue_item"), weight=ft.FontWeight.BOLD),
            ft.IconButton(icon="delete", icon_color="red500", on_click=remove_card)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        card_container = ft.Container(
            content=ft.Column([header, tf]),
            padding=10,
            border_radius=8,
            bgcolor="grey800" if self.page.theme_mode == ft.ThemeMode.DARK else "blue100"
        )
        
        self.queue_cards.append({"id": card_id, "textfield": tf, "container": card_container})
        self.queue_list.controls.append(card_container)
        
        if save:
            self.save_current_queue_state()
        self.page.update()

    def toggle_generation(self, e):
        if not hasattr(self, "queue_manager") or not self.queue_manager.is_running:
            self.start_generation()
        else:
            self.stop_generation()

    def start_generation(self):
        self.btn_generate.text = t("btn_cancel")
        self.btn_generate.bgcolor = "red700"
        self.page.update()
        
        self.save_current_queue_state()
        
        callbacks = {
            "on_start": self.on_gen_start,
            "on_progress": self.on_gen_progress,
            "on_finish": self.on_gen_finish,
            "on_error": self.on_gen_error,
            "on_queue_empty": self.on_gen_complete
        }
        
        self.queue_manager = QueueManager(self.config_manager, self.api_client, callbacks)
        
        import asyncio
        import threading
        
        def run_asyncio():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.queue_manager.run_queue())
            
        threading.Thread(target=run_asyncio, daemon=True).start()

    def stop_generation(self):
        import asyncio
        if hasattr(self, "queue_manager"):
            async def do_cancel():
                await self.queue_manager.cancel()
            asyncio.run(do_cancel())

    # Callbacks
    def on_gen_start(self, item):
        self.status_text.value = t("status_generating")
        self.progress_bar.visible = True
        self.progress_bar.value = 0
        self.page.update()

    def on_gen_progress(self, info):
        progress = info.get("progress", 0)
        self.progress_bar.value = progress
        self.status_text.value = t("status_generating_pct", pct=int(progress*100))
        self.page.update()

    def on_gen_finish(self, image, filepath):
        import base64
        import io
        
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        self.preview_image.src_base64 = img_b64
        self.preview_image.visible = True
        self.preview_placeholder.visible = False
        
        self.last_generated_prompt = self.config_manager.queue_state.get("last_finished_prompt", "")
        
        if self.queue_list.controls:
            first_card = self.queue_list.controls[0]
            self.queue_list.controls.remove(first_card)
            if self.queue_cards:
                self.queue_cards.pop(0)
                
        self.page.update()

    def on_gen_error(self, err_msg):
        self.page.dialog = ft.AlertDialog(title=ft.Text(t("msg_error")), content=ft.Text(err_msg))
        self.page.dialog.open = True
        self.on_gen_complete()
        self.page.update()

    def on_gen_complete(self):
        self.btn_generate.text = t("btn_generate")
        self.btn_generate.bgcolor = "green700"
        self.status_text.value = t("lbl_status_idle")
        self.progress_bar.visible = False
        self.page.update()

    def setup_ui(self):
        # Header
        header = ft.Row([
            ft.Text(t("title_main"), size=24, weight=ft.FontWeight.BOLD),
            ft.IconButton(icon="settings", tooltip=t("btn_settings"), on_click=self.open_settings)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Global Settings (Mocked for now, will link to ConfigManager later)
        global_settings = ft.Container(
            content=ft.Column([
                ft.Text(t("lbl_global_settings"), weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Text(t("lbl_batch_count")),
                    ft.TextField(value="1", width=60, height=40)
                ])
            ]),
            padding=10,
            border_radius=8,
            bgcolor="grey800" if self.page.theme_mode == ft.ThemeMode.DARK else "blue50"
        )
        
        # Left Panel (Settings & Queue)
        left_panel = ft.Container(
            content=ft.Column([
                header,
                global_settings,
                ft.Text(t("lbl_queue"), size=16, weight=ft.FontWeight.BOLD),
                ft.Container(content=self.queue_list, expand=True, border=ft.border.all(1, "grey400"), border_radius=8),
                ft.Row([
                    ft.ElevatedButton(t("btn_add_queue_wizard"), on_click=self.open_wizard, expand=True),
                    ft.ElevatedButton(t("btn_add_empty_queue"), on_click=lambda e: self.add_queue_card(""), expand=True)
                ])
            ], expand=True),
            expand=4,
            padding=10
        )
        
        # Right Panel (Preview)
        right_panel = ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Stack([
                        self.preview_placeholder,
                        self.preview_image
                    ], expand=True),
                    expand=True,
                    padding=10
                ),
                ft.Column([
                    self.progress_bar,
                    self.status_text
                ], alignment=ft.MainAxisAlignment.CENTER),
                ft.Row([
                    ft.ElevatedButton(t("btn_save_preset"), on_click=self.open_save_preset, expand=True),
                    ft.ElevatedButton(t("btn_requeue"), on_click=self.requeue_prompt, expand=True)
                ]),
                ft.Row([self.btn_generate])
            ], expand=True),
            expand=6,
            padding=10
        )
        
        self.main_layout = ft.Row([left_panel, right_panel], expand=True)

    def open_settings(self, e):
        from gui.settings_view import SettingsView
        sv = SettingsView(self.page, self.config_manager, self.api_client, self.on_settings_closed)
        sv.show()

    def on_settings_closed(self):
        # Refresh API URL or Theme if needed
        pass

    def open_wizard(self, e):
        from gui.wizard_view import WizardView
        wv = WizardView(self.page, self.config_manager, self.on_wizard_complete)
        wv.show()
        
    def on_wizard_complete(self, prompt_text):
        self.add_queue_card(prompt_text)

    def open_save_preset(self, e):
        from gui.preset_save_view import PresetSaveView
        psv = PresetSaveView(self.page, self.config_manager, "1girl, outdoors") # Mock current prompt
        psv.show()

    def requeue_prompt(self, e):
        if self.last_generated_prompt:
            self.add_queue_card(self.last_generated_prompt)

    def build(self):
        return self.main_layout
