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
        self.items_done_in_session = 0
        
        # UI Components
        self.queue_pos_text = ft.Text("", size=14, color="grey500", weight=ft.FontWeight.W_500)
        self.preview_image = ft.Image(
            src="", 
            fit=ft.ImageFit.CONTAIN if hasattr(ft, 'ImageFit') else "contain", 
            expand=True, 
            visible=False
        )
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
        
        self.queue_list = ft.ReorderableListView(
            expand=True, 
            spacing=10, 
            on_reorder=self.on_reorder,
            show_default_drag_handles=False
        )
        
        self.setup_ui()
        self.load_queue_from_state()

    def on_reorder(self, e):
        # Move in self.queue_cards
        item = self.queue_cards.pop(e.old_index)
        self.queue_cards.insert(e.new_index, item)
        # Update UI Controls to match new order
        self.queue_list.controls = [c["container"] for c in self.queue_cards]
        self.save_current_queue_state()
        self.page.update()

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
            text_size=12,
            content_padding=ft.padding.all(8),
            on_blur=lambda e: self.save_current_queue_state()
        )
        
        def remove_card(e):
            def confirm_remove(e):
                self.queue_list.controls.remove(card_container)
                self.queue_cards = [c for c in self.queue_cards if c["id"] != card_id]
                self.save_current_queue_state()
                dlg.open = False
                self.page.update()

            dlg = ft.AlertDialog(
                title=ft.Text(t("title_confirm")),
                content=ft.Text(t("msg_confirm_delete")),
                actions=[
                    ft.TextButton(t("btn_yes"), on_click=confirm_remove),
                    ft.TextButton(t("btn_no"), on_click=lambda e: setattr(dlg, "open", False) or self.page.update()),
                ],
            )
            self.page.overlay.append(dlg)
            dlg.open = True
            self.page.update()
            
        header = ft.Row([
            ft.Row([
                ft.ReorderableDragHandle(
                    content=ft.Icon(ft.Icons.DRAG_HANDLE, color="grey400"),
                    mouse_cursor=ft.MouseCursor.GRAB if hasattr(ft, "MouseCursor") else None
                ),
                ft.Text(t("lbl_queue_item"), weight=ft.FontWeight.BOLD)
            ], spacing=10),
            ft.IconButton(icon=ft.Icons.DELETE, icon_color="red500", on_click=remove_card)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        card_container = ft.Container(
            content=ft.Column([header, tf]),
            padding=10,
            border_radius=8,
            bgcolor="grey900" if self.page.theme_mode == ft.ThemeMode.DARK else "blue50"
        )
        
        self.queue_cards.append({"id": card_id, "textfield": tf, "container": card_container})
        self.queue_list.controls.append(card_container)
        
        if save:
            self.save_current_queue_state()
        self.page.update()

    async def toggle_generation(self, e):
        if not hasattr(self, "queue_manager") or not self.queue_manager.is_running:
            await self.start_generation()
        else:
            await self.stop_generation()

    async def start_generation(self):
        # 0. Check Directory
        import os
        save_dir = self.config_manager.config.get("save_dir", "")
        if not save_dir or not os.path.exists(save_dir):
            snack = ft.SnackBar(ft.Text(f"Error: Save directory not found: {save_dir}"), bgcolor="red700")
            self.page.overlay.append(snack)
            snack.open = True
            self.page.update()
            return

        self.btn_generate.text = t("btn_cancel")
        self.btn_generate.bgcolor = "red700"
        self.btn_generate.content = None
        self.btn_generate.update()
        self.items_done_in_session = 0
        
        # 1. Lock first queue item if exists
        if self.queue_cards:
            self.queue_cards[0]["textfield"].read_only = True
            
        self.page.update()
        
        self.save_current_queue_state()
        self.save_global_params()
        
        callbacks = {
            "on_start": self.on_gen_start,
            "on_progress": self.on_gen_progress,
            "on_finish": self.on_gen_finish,
            "on_error": self.on_gen_error,
            "on_queue_empty": self.on_gen_complete
        }
        
        self.queue_manager = QueueManager(self.config_manager, self.api_client, callbacks)
        
        # Start the queue loop as an async task
        import asyncio
        asyncio.create_task(self.queue_manager.run_queue())

    async def stop_generation(self):
        if hasattr(self, "queue_manager"):
            await self.queue_manager.cancel()

    # Callbacks
    async def on_gen_start(self, item, index=1, total=1):
        if total > 1:
            self.status_text.value = f"{t('status_generating')} ({index}/{total})"
        else:
            self.status_text.value = t("status_generating")
        
        # Update Progress Display: [Item X/Y] (Index-1) / BatchTotal
        q_current = self.items_done_in_session + 1
        q_total = self.items_done_in_session + len(self.queue_cards)
        self.queue_pos_text.value = f"[{q_current}/{q_total}] {index-1} / {total}"

        self.progress_bar.visible = True
        self.progress_bar.value = 0
        
        # Color processing item
        if self.queue_cards:
            self.queue_cards[0]["container"].bgcolor = "grey800" if self.page.theme_mode == ft.ThemeMode.DARK else "blue100"
            
        self.page.update()

    async def on_gen_progress(self, info):
        progress = info.get("progress", 0)
        self.progress_bar.value = progress
        self.status_text.value = t("status_generating_pct", pct=int(progress*100))
        self.page.update()

    async def on_gen_finish(self, image, filepath, is_last=True, index=1, total=1):
        import base64
        import io
        
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        img_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        self.preview_image.src = img_b64
        self.preview_image.visible = True
        self.preview_placeholder.visible = False
        
        # Update Progress Display: [Item X/Y] Index / BatchTotal
        q_current = self.items_done_in_session + 1
        q_total = self.items_done_in_session + len(self.queue_cards)
        self.queue_pos_text.value = f"[{q_current}/{q_total}] {index} / {total}"

        if is_last and self.queue_list.controls:
            first_card = self.queue_list.controls[0]
            self.queue_list.controls.remove(first_card)
            if self.queue_cards:
                self.queue_cards.pop(0)
                self.items_done_in_session += 1
                
        self.page.update()

    async def on_gen_error(self, err_msg):
        dlg = ft.AlertDialog(title=ft.Text(t("msg_error")), content=ft.Text(err_msg))
        self.page.overlay.append(dlg)
        dlg.open = True
        await self.on_gen_complete()
        self.page.update()

    async def on_gen_complete(self):
        self.btn_generate.text = t("btn_generate")
        self.btn_generate.bgcolor = "green700"
        self.btn_generate.content = None
        self.btn_generate.update()
        self.status_text.value = t("lbl_status_idle")
        self.progress_bar.visible = False
        self.queue_pos_text.value = ""
        
        # Unlock and Reset colors if items are remaining
        for card in self.queue_cards:
            card["textfield"].read_only = False
            card["container"].bgcolor = "grey900" if self.page.theme_mode == ft.ThemeMode.DARK else "blue50"
            
        self.page.update()

    def setup_ui(self):
        # Header
        header = ft.Row([
            ft.Text(t("title_main"), size=24, weight=ft.FontWeight.BOLD),
            ft.IconButton(icon=ft.Icons.SETTINGS, tooltip=t("btn_settings"), on_click=self.open_settings)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        # Global Settings
        gp = self.config_manager.config.get("global_params", {})
        
        # Helper to create Label + Small TextField (No Slider)
        def create_param_row(label_text, val, key):
            tf = ft.TextField(value=str(val), width=60, height=30, content_padding=5, text_size=12, text_align=ft.TextAlign.RIGHT)
            return ft.Row([
                ft.Text(label_text, size=13, weight=ft.FontWeight.W_500, width=80),
                tf
            ], spacing=5)

        self.batch_count_tf = ft.TextField(value=str(gp.get("batch_count", 1)), width=50, height=30, content_padding=5, text_size=12)
        self.freeu_enable_cb = ft.Checkbox(label="FreeU Integrated (SD 1.x, SD 2.x, SDXL)", value=gp.get("freeu_enable", False))
        
        # Parameters
        self.freeu_controls = {
            "b1": create_param_row("B1", gp.get("b1", 1.01), "b1"),
            "b2": create_param_row("B2", gp.get("b2", 1.02), "b2"),
            "s1": create_param_row("S1", gp.get("s1", 0.99), "s1"),
            "s2": create_param_row("S2", gp.get("s2", 0.95), "s2"),
            "start": create_param_row(t("lbl_freeu_start"), gp.get("freeu_start", 0), "start"),
            "end": create_param_row(t("lbl_freeu_end"), gp.get("freeu_end", 1), "end")
        }

        self.freeu_b1_tf = self.freeu_controls["b1"].controls[1]
        self.freeu_b2_tf = self.freeu_controls["b2"].controls[1]
        self.freeu_s1_tf = self.freeu_controls["s1"].controls[1]
        self.freeu_s2_tf = self.freeu_controls["s2"].controls[1]
        self.freeu_start_tf = self.freeu_controls["start"].controls[1]
        self.freeu_end_tf = self.freeu_controls["end"].controls[1]

        # ADetailer Controls
        self.adetailer_enable_cb = ft.Checkbox(label=t("lbl_ad_enable"), value=gp.get("adetailer_enable", False))
        self.adetailer_model_dd = ft.Dropdown(
            label=t("lbl_ad_model"),
            value=gp.get("adetailer_model", "face_yolov8n.pt"),
            options=[
                ft.dropdown.Option("face_yolov8n.pt"),
                ft.dropdown.Option("hand_yolov8n.pt"),
                ft.dropdown.Option("person_yolov8n.pt"),
                ft.dropdown.Option("mediapipe_face_full"),
            ],
            width=200,
            text_size=12,
            height=45,
        )
        self.adetailer_prompt_tf = ft.TextField(
            label=t("lbl_ad_prompt"),
            value=gp.get("adetailer_prompt", ""),
            multiline=True,
            min_lines=2,
            max_lines=3,
            text_size=12,
        )
        self.adetailer_denoising_tf = ft.TextField(
            value=str(gp.get("adetailer_denoising", 0.4)),
            width=60,
            height=30,
            content_padding=5,
            text_size=12,
            text_align=ft.TextAlign.RIGHT
        )

        def adjust_denoising(delta):
            try:
                val = float(self.adetailer_denoising_tf.value)
                new_val = round(max(0.0, min(1.0, val + delta)), 2)
                self.adetailer_denoising_tf.value = str(new_val)
                self.page.update()
            except: pass

        adetailer_denoising_row = ft.Row([
            ft.Text(t("lbl_ad_denoising"), size=13, weight=ft.FontWeight.W_500),
            ft.Row([
                ft.IconButton(icon=ft.Icons.REMOVE, icon_size=16, on_click=lambda _: adjust_denoising(-0.05)),
                self.adetailer_denoising_tf,
                ft.IconButton(icon=ft.Icons.ADD, icon_size=16, on_click=lambda _: adjust_denoising(0.05)),
            ], spacing=0)
        ], spacing=5, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        adetailer_panel = ft.Container(
            content=ft.Column([
                ft.Text(t("lbl_adetailer"), weight=ft.FontWeight.BOLD, size=14),
                self.adetailer_enable_cb,
                self.adetailer_model_dd,
                adetailer_denoising_row,
                self.adetailer_prompt_tf,
            ], spacing=8, tight=True, scroll=ft.ScrollMode.AUTO),
            width=250,
            padding=10,
            bgcolor="grey900" if self.page.theme_mode == ft.ThemeMode.DARK else "blue50",
            border_radius=8,
        )

        # FreeU preset list
        self.freeu_preset_column = ft.Column([], spacing=4, scroll=ft.ScrollMode.AUTO)
        self._refresh_freeu_preset_list()

        freeu_params_panel = ft.Column([
            self.freeu_enable_cb,
            ft.Column([
                ft.Row([self.freeu_controls["b1"], self.freeu_controls["b2"]], spacing=20),
                ft.Row([self.freeu_controls["s1"], self.freeu_controls["s2"]], spacing=20),
                ft.Row([self.freeu_controls["start"], self.freeu_controls["end"]], spacing=20),
            ], spacing=5)
        ], spacing=5)

        freeu_preset_panel = ft.Container(
            content=ft.Column([
                ft.Text(t("lbl_freeu_presets"), size=14, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton(
                    t("btn_save_freeu_preset"),
                    icon=ft.Icons.SAVE,
                    on_click=self.save_freeu_preset_dialog,
                    height=32,
                    expand=True,
                ),
                ft.Container(
                    content=self.freeu_preset_column,
                    height=110,
                    border=ft.border.all(1, "grey600"),
                    border_radius=6,
                    padding=4,
                    expand=True,
                )
            ], spacing=6, expand=True),
            expand=True,
        )

        global_settings = ft.Container(
            content=ft.Column([
                ft.Text(t("lbl_global_settings"), weight=ft.FontWeight.BOLD, size=16),
                ft.Row([
                    ft.Text(t("lbl_batch_count"), size=14),
                    self.batch_count_tf,
                    ft.Container(width=10),
                    self.queue_pos_text,
                ], alignment=ft.MainAxisAlignment.START, spacing=10),
                ft.Divider(height=1, thickness=1, color="grey700"),
                ft.Row([
                    freeu_params_panel,
                    ft.VerticalDivider(width=1, color="grey700"),
                    freeu_preset_panel,
                ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START, expand=True),
            ], spacing=10),
            padding=15,
            border_radius=10
        )
        
        # Left Panel (Queue)
        left_panel = ft.Container(
            content=ft.Column([
                header,
                ft.Text(t("lbl_queue"), size=16, weight=ft.FontWeight.BOLD),
                ft.Container(content=self.queue_list, expand=True, border=ft.border.all(1, "grey400"), border_radius=8),
                ft.Row([
                    ft.ElevatedButton(t("btn_add_queue_wizard"), on_click=self.open_wizard, expand=True),
                    ft.ElevatedButton(t("btn_add_empty_queue"), on_click=lambda e: self.add_queue_card(""), expand=True)
                ])
            ], expand=True),
            expand=1,
            padding=10
        )
        
        # Right Panel (Preview & Global Settings)
        right_panel = ft.Container(
            content=ft.Column([
                ft.Row([
                    adetailer_panel,
                    ft.Container(
                        content=ft.Stack([
                            self.preview_placeholder,
                            ft.Container(
                                content=self.preview_image,
                                on_click=self.show_full_image,
                                ink=True,
                                expand=True,
                            )
                        ], expand=True),
                        height=300,
                        padding=5,
                        expand=True,
                    )
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.START),
                global_settings,
                ft.Column([
                    self.progress_bar,
                    self.status_text
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
                ft.Row([
                    ft.ElevatedButton(t("btn_save_preset"), on_click=self.open_save_preset, expand=True),
                    ft.ElevatedButton(t("btn_requeue"), on_click=self.requeue_prompt, expand=True)
                ]),
                ft.Row([self.btn_generate])
            ], expand=True, spacing=10),
            expand=1,
            padding=10
        )
        
        self.main_layout = ft.Row([left_panel, right_panel], expand=True)

    # ---- FreeU preset methods ----
    def _refresh_freeu_preset_list(self):
        """プリセットリストのUIを最新状態で再構築する。"""
        self.freeu_preset_column.controls.clear()
        presets = self.config_manager.freeu_presets.get("presets", [])
        for i, p in enumerate(presets):
            idx = i  # closure capture
            row = ft.Row([
                ft.TextButton(
                    p["name"],
                    on_click=lambda e, idx=idx: self._load_freeu_preset(idx),
                    style=ft.ButtonStyle(padding=ft.padding.symmetric(horizontal=4)),
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_size=16,
                    icon_color="red400",
                    tooltip=t("btn_delete"),
                    on_click=lambda e, idx=idx: self._delete_freeu_preset(idx),
                )
            ], spacing=0, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            self.freeu_preset_column.controls.append(row)

    def save_freeu_preset_dialog(self, e):
        """プリセット名を入力して保存するダイアログを表示する。"""
        name_tf = ft.TextField(label=t("lbl_preset_name"), autofocus=True, width=240)

        def do_save(e):
            name = name_tf.value.strip()
            if not name:
                return
            params = {
                "b1": self._float_or(self.freeu_b1_tf.value, 1.01),
                "b2": self._float_or(self.freeu_b2_tf.value, 1.02),
                "s1": self._float_or(self.freeu_s1_tf.value, 0.99),
                "s2": self._float_or(self.freeu_s2_tf.value, 0.95),
                "freeu_start": self._float_or(self.freeu_start_tf.value, 0.0),
                "freeu_end": self._float_or(self.freeu_end_tf.value, 1.0),
                "freeu_enable": self.freeu_enable_cb.value,
            }
            self.config_manager.add_freeu_preset(name, params)
            self._refresh_freeu_preset_list()
            dlg.open = False
            self.page.update()

        dlg = ft.AlertDialog(
            title=ft.Text(t("title_save_freeu_preset")),
            content=name_tf,
            actions=[
                ft.TextButton(t("btn_save"), on_click=do_save),
                ft.TextButton(t("btn_close"), on_click=lambda e: setattr(dlg, "open", False) or self.page.update()),
            ]
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    def _load_freeu_preset(self, index):
        """プリセットをFreeUコントロールに反映する。"""
        presets = self.config_manager.freeu_presets.get("presets", [])
        if index >= len(presets):
            return
        params = presets[index]["params"]
        self.freeu_b1_tf.value = str(params.get("b1", 1.01))
        self.freeu_b2_tf.value = str(params.get("b2", 1.02))
        self.freeu_s1_tf.value = str(params.get("s1", 0.99))
        self.freeu_s2_tf.value = str(params.get("s2", 0.95))
        self.freeu_start_tf.value = str(params.get("freeu_start", 0.0))
        self.freeu_end_tf.value = str(params.get("freeu_end", 1.0))
        self.freeu_enable_cb.value = params.get("freeu_enable", False)
        self.page.update()

    def _delete_freeu_preset(self, index):
        """確認なしでプリセットを削除する。"""
        self.config_manager.delete_freeu_preset(index)
        self._refresh_freeu_preset_list()
        self.page.update()

    @staticmethod
    def _float_or(val, default):
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    def show_full_image(self, e):
        """画像を拡大してダイアログで表示する。"""
        if not self.preview_image.src:
            return
            
        full_img = ft.Image(
            src=self.preview_image.src,
            fit=ft.ImageFit.CONTAIN if hasattr(ft, "ImageFit") else "contain",
        )
        
        dlg = ft.AlertDialog(
            content=ft.Container(
                content=full_img,
                padding=10,
                width=800,
                height=800,
            ),
            actions=[
                ft.TextButton(t("btn_close"), on_click=lambda e: setattr(dlg, "open", False) or self.page.update()),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.overlay.append(dlg)
        dlg.open = True
        self.page.update()

    # ---- end FreeU preset methods ----

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
        psv = PresetSaveView(self.page, self.config_manager, self.last_generated_prompt)
        psv.show()

    async def requeue_prompt(self, e):
        if self.last_generated_prompt:
            self.add_queue_card(self.last_generated_prompt)

    def save_global_params(self):
        gp = self.config_manager.config["global_params"]
        try: gp["batch_count"] = int(self.batch_count_tf.value)
        except: pass
        gp["freeu_enable"] = self.freeu_enable_cb.value
        try: gp["freeu_b1"] = float(self.freeu_b1_tf.value)
        except: pass
        try: gp["freeu_b2"] = float(self.freeu_b2_tf.value)
        except: pass
        try: gp["freeu_s1"] = float(self.freeu_s1_tf.value)
        except: pass
        try: gp["freeu_s2"] = float(self.freeu_s2_tf.value)
        except: pass
        try: gp["freeu_start"] = float(self.freeu_start_tf.value)
        except: pass
        try: gp["freeu_end"] = float(self.freeu_end_tf.value)
        except: pass
        
        # ADetailer
        gp["adetailer_enable"] = self.adetailer_enable_cb.value
        gp["adetailer_model"] = self.adetailer_model_dd.value
        try: gp["adetailer_denoising"] = float(self.adetailer_denoising_tf.value)
        except: pass
        gp["adetailer_prompt"] = self.adetailer_prompt_tf.value
        
        self.config_manager.save_config()

    def build(self):
        return self.main_layout
