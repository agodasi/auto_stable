import customtkinter as ctk

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("900x700")
        self.config_manager = config_manager
        
        # Tabs for different settings
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tabview.add("System Settings")
        self.tabview.add("Base Generation")
        self.tabview.add("Preset Management")
        
        self.setup_system_tab()
        self.setup_generation_tab()
        self.setup_preset_tab()

        # Save button for the whole settings
        self.save_all_btn = ctk.CTkButton(self, text="Save & Close", command=self.save_and_close)
        self.save_all_btn.pack(pady=10)
        
    def setup_system_tab(self):
        tab = self.tabview.tab("System Settings")
        conf = self.config_manager.config
        
        # API URL
        ctk.CTkLabel(tab, text="API URL:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.api_url_entry = ctk.CTkEntry(tab, width=300)
        self.api_url_entry.insert(0, conf.get("api_url", ""))
        self.api_url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Save Directory
        ctk.CTkLabel(tab, text="Save Directory:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.save_dir_entry = ctk.CTkEntry(tab, width=300)
        self.save_dir_entry.insert(0, conf.get("save_dir", ""))
        self.save_dir_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Theme
        ctk.CTkLabel(tab, text="Theme:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.theme_option = ctk.CTkOptionMenu(tab, values=["System", "Light", "Dark"])
        self.theme_option.set(conf.get("theme", "Dark"))
        self.theme_option.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
    def setup_generation_tab(self):
        tab = self.tabview.tab("Base Generation")
        bp = self.config_manager.config.get("base_params", {})
        
        # Checkpoint
        ctk.CTkLabel(tab, text="Checkpoint:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.checkpoint_option = ctk.CTkOptionMenu(tab, values=[bp.get("checkpoint", "None")], width=250)
        self.checkpoint_option.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Negative Prompt
        ctk.CTkLabel(tab, text="Negative Prompt:").grid(row=1, column=0, padx=10, pady=10, sticky="nw")
        self.neg_prompt_entry = ctk.CTkTextbox(tab, width=400, height=80)
        self.neg_prompt_entry.insert("1.0", bp.get("negative_prompt", ""))
        self.neg_prompt_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="w")
        
        # Steps & CFG
        ctk.CTkLabel(tab, text="Steps:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.steps_entry = ctk.CTkEntry(tab, width=80)
        self.steps_entry.insert(0, str(bp.get("steps", 20)))
        self.steps_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(tab, text="CFG Scale:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.cfg_entry = ctk.CTkEntry(tab, width=80)
        self.cfg_entry.insert(0, str(bp.get("cfg_scale", 7.0)))
        self.cfg_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        # Width & Height
        size_frame = ctk.CTkFrame(tab, fg_color="transparent")
        size_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(size_frame, text="Width:").pack(side="left")
        self.width_entry = ctk.CTkEntry(size_frame, width=80)
        self.width_entry.insert(0, str(bp.get("width", 512)))
        self.width_entry.pack(side="left", padx=(5, 20))
        
        ctk.CTkLabel(size_frame, text="Height:").pack(side="left")
        self.height_entry = ctk.CTkEntry(size_frame, width=80)
        self.height_entry.insert(0, str(bp.get("height", 512)))
        self.height_entry.pack(side="left", padx=5)

    def setup_preset_tab(self):
        tab = self.tabview.tab("Preset Management")
        tab.grid_columnconfigure((0, 1), weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Situations Column
        sit_frame = ctk.CTkFrame(tab)
        sit_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(sit_frame, text="Situations", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.sit_scroll = ctk.CTkScrollableFrame(sit_frame)
        self.sit_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkButton(sit_frame, text="+ Add Situation", command=lambda: self.add_preset_prompt("situations")).pack(pady=5)
        
        # Characters Column
        char_frame = ctk.CTkFrame(tab)
        char_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        ctk.CTkLabel(char_frame, text="Characters", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        
        self.char_scroll = ctk.CTkScrollableFrame(char_frame)
        self.char_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkButton(char_frame, text="+ Add Character", command=lambda: self.add_preset_prompt("characters")).pack(pady=5)
        
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
        dialog.title("Edit Preset" if item else "Add Preset")
        dialog.geometry("400x350")
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text="Name:").pack(pady=(10, 0), padx=20, anchor="w")
        name_entry = ctk.CTkEntry(dialog, width=350)
        name_entry.pack(pady=5, padx=20)
        if item: name_entry.insert(0, item["name"])
        
        ctk.CTkLabel(dialog, text="Text:").pack(pady=(10, 0), padx=20, anchor="w")
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
            
        ctk.CTkButton(dialog, text="Save", command=save).pack(pady=10)

    def delete_preset_prompt(self, category, index):
        self.config_manager.presets[category].pop(index)
        self.config_manager.save_presets()
        self.refresh_presets_display()

    def save_and_close(self):
        # Update config object from UI
        self.config_manager.config["api_url"] = self.api_url_entry.get()
        self.config_manager.config["save_dir"] = self.save_dir_entry.get()
        self.config_manager.config["theme"] = self.theme_option.get()
        
        bp = self.config_manager.config["base_params"]
        bp["negative_prompt"] = self.neg_prompt_entry.get("1.0", "end-1c").strip()
        bp["steps"] = int(self.steps_entry.get())
        bp["cfg_scale"] = float(self.cfg_entry.get())
        bp["width"] = int(self.width_entry.get())
        bp["height"] = int(self.height_entry.get())
        
        self.config_manager.save_config()
        self.destroy()

