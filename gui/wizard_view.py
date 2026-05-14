import flet as ft
from core.i18n import t

class WizardView:
    def __init__(self, page: ft.Page, config_manager, on_complete_callback):
        self.page = page
        self.config_manager = config_manager
        self.on_complete_callback = on_complete_callback
        
        self.presets = self.config_manager.presets
        self.sit_items = self.presets.get("situations", [])
        self.sit_checkboxes = [ft.Checkbox(label=item["name"], value=False) for item in self.sit_items]
        
        self.characters = [t("opt_skip")] + [item["name"] for item in self.presets.get("characters", [])]
        self.char_dd = ft.Dropdown(label=t("step2_char"), options=[ft.dropdown.Option(c) for c in self.characters], value=self.characters[0] if self.characters else None, expand=True)

        self.step_content = ft.Container()
        
        self.dialog = ft.AlertDialog(
            title=ft.Text(t("title_wizard")),
            content=self.step_content,
            actions=[]
        )
        self.go_step1()

    def go_step1(self, e=None):
        content = ft.Column([
            ft.Text(t("step1_sit"), size=16),
            ft.Container(
                content=ft.Column(self.sit_checkboxes, scroll=ft.ScrollMode.AUTO),
                height=150,
                border=ft.border.all(1, "grey400"),
                border_radius=5,
                padding=5
            )
        ], width=400, height=200)
        
        self.step_content.content = content
        self.dialog.actions = [
            ft.TextButton(t("btn_next"), on_click=self.go_step2)
        ]
        self.page.update()

    def go_step2(self, e=None):
        content = ft.Column([
            ft.Text(t("step2_char"), size=16),
            self.char_dd
        ], width=400, height=200)
        
        self.step_content.content = content
        self.dialog.actions = [
            ft.TextButton(t("btn_back"), on_click=self.go_step1),
            ft.TextButton(t("btn_finish"), on_click=self.finish_wizard)
        ]
        self.page.update()

    def finish_wizard(self, e):
        char_val = self.char_dd.value
        char_text = ""
        
        if char_val != t("opt_skip"):
            for item in self.presets.get("characters", []):
                if item["name"] == char_val:
                    char_text = item.get("text", "").strip()
                    break

        final_texts = []
        selected_situations = [cb for cb in self.sit_checkboxes if cb.value]
        
        if not selected_situations:
            if char_text:
                final_texts.append(char_text)
        else:
            for i, cb in enumerate(self.sit_checkboxes):
                if cb.value:
                    prompt_parts = []
                    item = self.sit_items[i]
                    if "text_front" in item or "text_back" in item:
                        front = item.get("text_front", "").strip()
                        back = item.get("text_back", "").strip()
                        if front: prompt_parts.append(front)
                        if char_text: prompt_parts.append(char_text)
                        if back: prompt_parts.append(back)
                    else:
                        front = item.get("text", "").strip()
                        if front: prompt_parts.append(front)
                        if char_text: prompt_parts.append(char_text)
                    
                    final_text = "\n".join(prompt_parts)
                    if final_text:
                        final_texts.append(final_text)

        if final_texts:
            self.on_complete_callback(final_texts)
            
        self.close_dialog()

    def show(self):
        for cb in self.sit_checkboxes:
            cb.value = False
        if self.characters:
            self.char_dd.value = self.characters[0]
            
        if self.dialog not in self.page.overlay:
            self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.go_step1()
        self.page.update()

    def close_dialog(self):
        self.dialog.open = False
        self.page.update()
