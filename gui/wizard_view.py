import flet as ft
from core.i18n import t

class WizardView:
    def __init__(self, page: ft.Page, config_manager, on_complete_callback):
        self.page = page
        self.config_manager = config_manager
        self.on_complete_callback = on_complete_callback
        
        self.presets = self.config_manager.presets
        self.situations = [t("opt_skip")] + [item["name"] for item in self.presets.get("situations", [])]
        self.characters = [t("opt_skip")] + [item["name"] for item in self.presets.get("characters", [])]
        
        self.sit_dd = ft.Dropdown(label=t("step1_sit"), options=[ft.dropdown.Option(s) for s in self.situations], value=self.situations[0], expand=True)
        self.char_dd = ft.Dropdown(label=t("step2_char"), options=[ft.dropdown.Option(c) for c in self.characters], value=self.characters[0], expand=True)

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
            self.sit_dd
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
        prompt_parts = []
        sit_back_text = ""
        
        sit_val = self.sit_dd.value
        char_val = self.char_dd.value
        
        if sit_val != t("opt_skip"):
            # Find actual prompt text
            for item in self.presets.get("situations", []):
                if item["name"] == sit_val:
                    if "text_front" in item or "text_back" in item:
                        front = item.get("text_front", "").strip()
                        back = item.get("text_back", "").strip()
                        if front: prompt_parts.append(front)
                        # We temporarily attach 'back' to a local variable to be appended after the character
                        sit_back_text = back
                    else:
                        # Legacy support
                        prompt_parts.append(item.get("text", "").strip())
                    break
        
        if char_val != t("opt_skip"):
            for item in self.presets.get("characters", []):
                if item["name"] == char_val:
                    prompt_parts.append(item.get("text", "").strip())
                    break
                    
        if sit_back_text:
            prompt_parts.append(sit_back_text)
                    
        final_text = "\n".join(prompt_parts)
        if final_text:
            self.on_complete_callback(final_text)
            
        self.close_dialog()

    def show(self):
        if self.dialog not in self.page.overlay:
            self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()

    def close_dialog(self):
        self.dialog.open = False
        self.page.update()
