import flet as ft
from core.i18n import t

class SettingsView:
    def __init__(self, page: ft.Page, config_manager, api_client, on_close_callback):
        self.page = page
        self.config_manager = config_manager
        self.api_client = api_client
        self.on_close_callback = on_close_callback
        self.conf = self.config_manager.config
        
        # Build UI Components
        self.api_url_tf = ft.TextField(label=t("lbl_api_url"), value=self.conf.get("api_url", "http://127.0.0.1:7860"), expand=True)
        self.test_btn = ft.ElevatedButton(t("btn_test_connection"), on_click=self.test_connection)
        self.conn_status = ft.Text(t("status_disconnected"), color="red")
        
        self.save_dir_tf = ft.TextField(label=t("lbl_save_dir"), value=self.conf.get("save_dir", ""), expand=True)
        self.browse_btn = ft.ElevatedButton(t("btn_browse"), on_click=self.browse_folder)
        
        self.theme_dd = ft.Dropdown(
            label=t("lbl_theme"),
            options=[ft.dropdown.Option("Light"), ft.dropdown.Option("Dark"), ft.dropdown.Option("System")],
            value=self.conf.get("theme", "Dark")
        )
        
        self.lang_dd = ft.Dropdown(
            label=t("lbl_language"),
            options=[ft.dropdown.Option("ja"), ft.dropdown.Option("en"), ft.dropdown.Option("zh")],
            value=self.conf.get("language", "ja"),
            expand=True
        )
        self.restart_txt = ft.Text(t("msg_restart"), color="red", visible=False)
        
        bp = self.conf.get("base_params", {})
        self.ckpt_dd = ft.Dropdown(label=t("lbl_checkpoint"), options=[ft.dropdown.Option(bp.get("checkpoint", "None"))], value=bp.get("checkpoint", "None"), expand=True)
        self.refresh_btn = ft.ElevatedButton(t("btn_refresh"), on_click=self.refresh_models)
        
        self.neg_prompt_tf = ft.TextField(
            label=t("lbl_negative_prompt"), 
            value=bp.get("negative_prompt", ""), 
            multiline=True, 
            min_lines=10, 
            max_lines=12,
            expand=True
        )
        self.steps_tf = ft.TextField(label=t("lbl_steps"), value=str(bp.get("steps", 20)), width=100)
        self.cfg_tf = ft.TextField(label=t("lbl_cfg_scale"), value=str(bp.get("cfg_scale", 7.0)), width=100)
        self.width_tf = ft.TextField(label=t("lbl_width"), value=str(bp.get("width", 512)), width=100)
        self.height_tf = ft.TextField(label=t("lbl_height"), value=str(bp.get("height", 512)), width=100)
        
        self.dialog = ft.AlertDialog(
            title=ft.Text(t("title_settings")),
            content=self.build_content(),
            actions=[
                ft.TextButton(t("btn_apply"), on_click=self.apply_settings),
                ft.TextButton(t("btn_save"), on_click=self.save_and_close),
                ft.TextButton(t("btn_close"), on_click=self.close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        # FilePicker for directory selection
        # FilePicker for directory selection (on_result is removed in v0.8+)
        self.file_picker = ft.FilePicker()

    def build_content(self):
        system_tab = ft.Column([
            ft.Container(height=10), # Spacer
            ft.Row([self.api_url_tf, self.test_btn, self.conn_status]),
            ft.Row([self.save_dir_tf, self.browse_btn]),
            self.theme_dd,
            ft.Row([self.lang_dd, self.restart_txt])
        ], scroll=ft.ScrollMode.AUTO, expand=True)
        
        gen_tab = ft.Column([
            ft.Container(height=10), # Spacer
            ft.Row([self.ckpt_dd, self.refresh_btn]),
            self.neg_prompt_tf,
            ft.Row([self.steps_tf, self.cfg_tf]),
            ft.Row([self.width_tf, self.height_tf])
        ], scroll=ft.ScrollMode.AUTO, expand=True)
        
        preset_tab = ft.Column([
            ft.Text("Presets management will be implemented here.") # Placeholder for simplicity
        ], scroll=ft.ScrollMode.AUTO, expand=True)
        
        tab_bar = ft.TabBar(
            tabs=[
                ft.Tab(label=t("tab_system")),
                ft.Tab(label=t("tab_base")),
                ft.Tab(label=t("tab_preset")),
            ]
        )
        
        tab_view = ft.TabBarView(
            controls=[
                ft.Container(content=system_tab, padding=ft.padding.only(top=20, left=15, right=15)),
                ft.Container(content=gen_tab, padding=ft.padding.only(top=20, left=15, right=15)),
                ft.Container(content=preset_tab, padding=ft.padding.only(top=20, left=15, right=15))
            ],
            expand=True
        )
        
        tabs_controller = ft.Tabs(
            content=ft.Column([tab_bar, tab_view], expand=True),
            length=3,
            selected_index=0,
            expand=True
        )
        
        return ft.Container(content=tabs_controller, width=800, height=600, padding=10)

    def show(self):
        if self.dialog not in self.page.overlay:
            self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()
        
        # Auto test connection on open
        self.page.run_task(self.test_connection, None)

    def close_dialog(self, e=None):
        self.dialog.open = False
        self.page.update()
        if self.on_close_callback:
            self.on_close_callback()

    async def test_connection(self, e):
        import asyncio
        from core.api_client import SDForgeAPIClient
        
        url = self.api_url_tf.value
        temp_client = SDForgeAPIClient(url)
        self.conn_status.value = "..."
        self.conn_status.color = "grey"
        self.page.update()
        
        try:
            # We don't need threading, just await since this is an async-compatible handler
            await temp_client.get_progress()
            
            self.conn_status.value = t("status_connected")
            self.conn_status.color = "green"
            self.api_client.base_url = url.rstrip('/')
        except Exception:
            self.conn_status.value = t("status_disconnected")
            self.conn_status.color = "red"
        self.page.update()

    async def browse_folder(self, e):
        # In v0.8.0+, get_directory_path is async and returns the path directly
        path = await self.file_picker.get_directory_path()
        if path:
            self.save_dir_tf.value = path
            self.page.update()

    def apply_settings(self, e=None):
        old_theme = self.conf.get("theme")
        new_theme = self.theme_dd.value
        theme_changed = old_theme != new_theme
        
        old_lang = self.conf.get("language")
        new_lang = self.lang_dd.value
        lang_changed = old_lang != new_lang
        
        self.conf["api_url"] = self.api_url_tf.value
        self.conf["save_dir"] = self.save_dir_tf.value
        self.conf["theme"] = new_theme
        self.conf["language"] = new_lang
        
        bp = self.conf["base_params"]
        bp["checkpoint"] = self.ckpt_dd.value
        bp["negative_prompt"] = self.neg_prompt_tf.value
        try: bp["steps"] = int(self.steps_tf.value)
        except: pass
        try: bp["cfg_scale"] = float(self.cfg_tf.value)
        except: pass
        try: bp["width"] = int(self.width_tf.value)
        except: pass
        try: bp["height"] = int(self.height_tf.value)
        except: pass
        
        self.config_manager.save_config()
        
        if theme_changed:
            if new_theme == "Light": self.page.theme_mode = ft.ThemeMode.LIGHT
            elif new_theme == "Dark": self.page.theme_mode = ft.ThemeMode.DARK
            else: self.page.theme_mode = ft.ThemeMode.SYSTEM
            self.page.update()
            
        if lang_changed:
            from core.i18n import set_language
            set_language(new_lang)
            # Notifying user to restart inline
            self.restart_txt.visible = True
            self.page.update()

    def save_and_close(self, e):
        self.apply_settings()
        self.close_dialog()

    async def refresh_models(self, e):
        import asyncio
        
        self.refresh_btn.disabled = True
        self.page.update()
        
        try:
            models = await self.api_client.get_models()
            titles = [m.get("title") for m in models]
            if not titles: titles = ["None"]
            
            self.ckpt_dd.options = [ft.dropdown.Option(t) for t in titles]
            if self.ckpt_dd.value not in titles:
                self.ckpt_dd.value = titles[0]
        except Exception as ex:
            print(f"Error fetching models: {ex}")
        finally:
            self.refresh_btn.disabled = False
            self.page.update()
