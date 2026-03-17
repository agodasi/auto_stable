import customtkinter as ctk
from core.i18n import t

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.title(t("title_settings"))
        self.geometry("900x700")
        self.config_manager = config_manager
        
        # Tabs for different settings
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tabview.add(t("tab_system"))
        self.tabview.add(t("tab_base"))
        self.tabview.add(t("tab_preset"))
        
        self.setup_system_tab()
        self.setup_generation_tab()
        self.setup_preset_tab()

        # Control Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)
        
        ctk.CTkButton(btn_frame, text=t("btn_apply"), command=self.apply_settings, width=100).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text=t("btn_save"), command=self.save_and_close, width=100).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text=t("btn_close"), command=self.destroy, width=100).pack(side="left", padx=10)
        
    def setup_system_tab(self):
        tab = self.tabview.tab(t("tab_system"))
        conf = self.config_manager.config
        
        # API URL
        ctk.CTkLabel(tab, text=t("lbl_api_url")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.api_url_entry = ctk.CTkEntry(tab, width=300)
        self.api_url_entry.insert(0, conf.get("api_url", ""))
        self.api_url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Save Directory
        ctk.CTkLabel(tab, text=t("lbl_save_dir")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.save_dir_entry = ctk.CTkEntry(tab, width=300)
        self.save_dir_entry.insert(0, conf.get("save_dir", ""))
        self.save_dir_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Theme
        ctk.CTkLabel(tab, text=t("lbl_theme")).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.theme_option = ctk.CTkOptionMenu(tab, values=["System", "Light", "Dark"])
        self.theme_option.set(conf.get("theme", "Dark"))
        self.theme_option.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # Language
        ctk.CTkLabel(tab, text=t("lbl_language")).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.lang_option = ctk.CTkOptionMenu(tab, values=["ja", "en", "zh"])
        self.lang_option.set(conf.get("language", "ja"))
        self.lang_option.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
    def setup_generation_tab(self):
        tab = self.tabview.tab(t("tab_base"))
        bp = self.config_manager.config.get("base_params", {})
        
        # Checkpoint
        ctk.CTkLabel(tab, text=t("lbl_checkpoint")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.checkpoint_option = ctk.CTkOptionMenu(tab, values=[bp.get("checkpoint", "None")], width=250)
        self.checkpoint_option.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Negative Prompt
        ctk.CTkLabel(tab, text=t("lbl_negative_prompt")).grid(row=1, column=0, padx=10, pady=10, sticky="nw")
        self.neg_prompt_entry = ctk.CTkTextbox(tab, width=400, height=80)
        self.neg_prompt_entry.insert("1.0", bp.get("negative_prompt", ""))
        self.neg_prompt_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="w")
        
        # Steps & CFG
        ctk.CTkLabel(tab, text=t("lbl_steps")).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.steps_entry = ctk.CTkEntry(tab, width=80)
        self.steps_entry.insert(0, str(bp.get("steps", 20)))
        self.steps_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(tab, text=t("lbl_cfg_scale")).grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.cfg_entry = ctk.CTkEntry(tab, width=80)
        self.cfg_entry.insert(0, str(bp.get("cfg_scale", 7.0)))
        self.cfg_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        # Width & Height
        size_frame = ctk.CTkFrame(tab, fg_color="transparent")
        size_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(size_frame, text=t("lbl_width")).pack(side="left")
        self.width_entry = ctk.CTkEntry(size_frame, width=80)
        self.width_entry.insert(0, str(bp.get("width", 512)))
        self.width_entry.pack(side="left", padx=(5, 20))
        
        ctk.CTkLabel(size_frame, text=t("lbl_height")).pack(side="left")
        self.height_entry = ctk.CTkEntry(size_frame, width=80)
        self.height_entry.insert(0, str(bp.get("height", 512)))
        self.height_entry.pack(side="left", padx=5)

    def setup_preset_tab(self):
        tab = self.tabview.tab(t("tab_preset"))
        tab.grid_columnconfigure((0, 1), weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Situations Column
        sit_frame = ctk.CTkFrame(tab)
        sit_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(sit_frame, text=t("lbl_situations"), font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.sit_scroll = ctk.CTkScrollableFrame(sit_frame)
        self.sit_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkButton(sit_frame, text=t("btn_add_situation"), command=lambda: self.add_preset_prompt("situations")).pack(pady=5)
        
        # Characters Column
        char_frame = ctk.CTkFrame(tab)
        char_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(char_frame, text=t("lbl_characters"), font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.char_scroll = ctk.CTkScrollableFrame(char_frame)
        self.char_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkButton(char_frame, text=t("btn_add_character"), command=lambda: self.add_preset_prompt("characters")).pack(pady=5)
        
        self.refresh_presets_display()

    def refresh_presets_display(self):
        # Clear existing widgets
        for widget in self.sit_scroll.winfo_children(): widget.destroy()
        for widget in self.char_scroll.winfo_children(): widget.destroy()
        
        # Render Situations
        for i, item in enumerate(self.config_manager.presets["situations"]):
            self.create_preset_item(self.sit_scroll, "situations", i, item)
            
        # Render Characters
        for i, item in enumerate(self.config_manager.presets["characters"]):
            self.create_preset_item(self.char_scroll, "characters", i, item)

    def create_preset_item(self, parent, category, index, item):
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", pady=2, padx=2)
        
        label = ctk.CTkLabel(frame, text=item["name"], anchor="w")
        label.pack(side="left", padx=5, fill="x", expand=True)
        
        edit_btn = ctk.CTkButton(frame, text="✎", width=30, command=lambda: self.edit_preset_prompt(category, index))
        edit_btn.pack(side="left", padx=2)
        
        del_btn = ctk.CTkButton(frame, text="🗑", width=30, fg_color="#C62828", hover_color="#b71c1c", 
                               command=lambda: self.delete_preset_prompt(category, index))
        del_btn.pack(side="left", padx=2)

    def add_preset_prompt(self, category):
        self.open_preset_editor(category, None)

    def edit_preset_prompt(self, category, index):
        item = self.config_manager.presets[category][index]
        self.open_preset_editor(category, index, item)

    def open_preset_editor(self, category, index, item=None):
        dialog = ctk.CTkToplevel(self)
        dialog.title(t("title_edit_preset") if item else t("title_add_preset"))
        dialog.geometry("400x350")
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text=t("lbl_name")).pack(pady=(10, 0), padx=20, anchor="w")
        name_entry = ctk.CTkEntry(dialog, width=350)
        name_entry.pack(pady=5, padx=20)
        if item: name_entry.insert(0, item["name"])
        
        ctk.CTkLabel(dialog, text=t("lbl_text")).pack(pady=(10, 0), padx=20, anchor="w")
        text_box = ctk.CTkTextbox(dialog, width=350, height=150)
        text_box.pack(pady=5, padx=20)
        if item: text_box.insert("1.0", item["text"])
        
        def save():
            new_item = {"name": name_entry.get(), "text": text_box.get("1.0", "end-1c").strip()}
            if index is not None:
                self.config_manager.presets[category][index] = new_item
            else:
                self.config_manager.presets[category].append(new_item)
            self.config_manager.save_presets()
            self.refresh_presets_display()
            dialog.destroy()
            
        ctk.CTkButton(dialog, text=t("btn_save"), command=save).pack(pady=10)

    def delete_preset_prompt(self, category, index):
        self.config_manager.presets[category].pop(index)
        self.config_manager.save_presets()
        self.refresh_presets_display()

    def apply_settings(self):
        # Check if language changed
        old_lang = self.config_manager.config.get("language")
        new_lang = self.lang_option.get()
        lang_changed = old_lang != new_lang
        
        # Update config object from UI
        self.config_manager.config["api_url"] = self.api_url_entry.get()
        self.config_manager.config["save_dir"] = self.save_dir_entry.get()
        self.config_manager.config["theme"] = self.theme_option.get()
        self.config_manager.config["language"] = new_lang
        
        bp = self.config_manager.config["base_params"]
        bp["negative_prompt"] = self.neg_prompt_entry.get("1.0", "end-1c").strip()
        bp["steps"] = int(self.steps_entry.get())
        bp["cfg_scale"] = float(self.cfg_entry.get())
        bp["width"] = int(self.width_entry.get())
        bp["height"] = int(self.height_entry.get())
        
        self.config_manager.save_config()
        
        if lang_changed:
            from tkinter import messagebox
            from core.i18n import set_language
            set_language(new_lang)
            messagebox.showinfo(t("title_msg_restart"), t("msg_restart"))

    def save_and_close(self):
        self.apply_settings()
        self.destroy()

