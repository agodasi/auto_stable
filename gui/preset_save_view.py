import flet as ft
from core.i18n import t

class PresetSaveView:
    def __init__(self, page: ft.Page, config_manager, current_prompt: str):
        self.page = page
        self.config_manager = config_manager
        self.current_prompt = current_prompt
        
        # Bottom Prompt Area (Permanent)
        self.prompt_text = ft.TextField(
            value=self.current_prompt,
            multiline=True,
            min_lines=2,
            max_lines=3,
            read_only=True,
            expand=True
        )
        
        self.bottom_panel = ft.Container(
            content=ft.Column([
                ft.Text(t("lbl_current_prompt_guide"), weight=ft.FontWeight.BOLD),
                self.prompt_text
            ]),
            padding=10,
            border_radius=8,
            bgcolor="grey800" if self.page.theme_mode == ft.ThemeMode.DARK else "blue50"
        )
        
        # Top Area container
        self.step_content = ft.Container()
        
        self.sit_name_tf = ft.TextField(label=t("step1_save_sit") + " - " + t("ph_preset_name"), expand=True)
        self.sit_text_tf = ft.TextField(label="Text", multiline=True, min_lines=4, expand=True)
        
        self.char_name_tf = ft.TextField(label=t("step2_save_char") + " - " + t("ph_preset_name"), expand=True)
        self.char_text_tf = ft.TextField(label="Text", multiline=True, min_lines=4, expand=True)
        
        self.dialog = ft.AlertDialog(
            title=ft.Text(t("title_preset_save")),
            content=ft.Column([
                ft.Text(t("lbl_registration_fields"), weight=ft.FontWeight.BOLD),
                self.step_content,
                ft.Divider(),
                self.bottom_panel
            ], expand=True, tight=True),
            actions=[],
            content_padding=20,
        )
        # Dynamic width: 80% of window
        self.dialog.content.width = self.page.window_width * 0.8
        
        self.go_step1()

    def go_step1(self, e=None):
        content = ft.Column([
            ft.Text(t("step1_save_sit"), size=16),
            self.sit_name_tf,
            self.sit_text_tf
        ], expand=True)
        
        self.step_content.content = content
        self.dialog.actions = [
            ft.TextButton(t("btn_skip"), on_click=self.go_step2),
            ft.TextButton(t("btn_next"), on_click=self.go_step2)
        ]
        self.page.update()

    def go_step2(self, e=None):
        content = ft.Column([
            ft.Text(t("step2_save_char"), size=16),
            self.char_name_tf,
            self.char_text_tf
        ], expand=True)
        
        self.step_content.content = content
        self.dialog.actions = [
            ft.TextButton(t("btn_back"), on_click=self.go_step1),
            ft.TextButton(t("btn_save"), on_click=self.save_and_close)
        ]
        self.page.update()

    def save_and_close(self, e):
        sit_data = {"name": self.sit_name_tf.value, "text": self.sit_text_tf.value.strip()}
        char_data = {"name": self.char_name_tf.value, "text": self.char_text_tf.value.strip()}
        
        if sit_data.get("name") and sit_data.get("text"):
            self.config_manager.add_preset("situations", sit_data)
        if char_data.get("name") and char_data.get("text"):
            self.config_manager.add_preset("characters", char_data)
            
        self.close_dialog()

    def show(self):
        if self.dialog not in self.page.overlay:
            self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    def close_dialog(self):
        self.dialog.open = False
        self.page.update()
