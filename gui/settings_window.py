import customtkinter as ctk

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("800x600")
        
        # Tabs for different settings
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tabview.add("System Settings")
        self.tabview.add("Base Generation")
        self.tabview.add("Preset Management")
        
        self.setup_system_tab()
        self.setup_generation_tab()
        self.setup_preset_tab()
        
    def setup_system_tab(self):
        tab = self.tabview.tab("System Settings")
        
        # API URL
        ctk.CTkLabel(tab, text="API URL:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.api_url_entry = ctk.CTkEntry(tab, width=300)
        self.api_url_entry.insert(0, "http://192.168.1.100:7860")
        self.api_url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Save Directory
        ctk.CTkLabel(tab, text="Save Directory:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.save_dir_entry = ctk.CTkEntry(tab, width=300)
        self.save_dir_entry.insert(0, "./outputs")
        self.save_dir_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.browse_btn = ctk.CTkButton(tab, text="Browse...", width=80)
        self.browse_btn.grid(row=1, column=2, padx=10, pady=10, sticky="w")
        
        # Theme
        ctk.CTkLabel(tab, text="Theme:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.theme_option = ctk.CTkOptionMenu(tab, values=["System", "Light", "Dark"])
        self.theme_option.set("Dark")
        self.theme_option.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
    def setup_generation_tab(self):
        tab = self.tabview.tab("Base Generation")
        
        # Checkpoint
        ctk.CTkLabel(tab, text="Checkpoint:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.checkpoint_option = ctk.CTkOptionMenu(tab, values=["model_v1.safetensors"], width=250)
        self.checkpoint_option.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.refresh_ckpt_btn = ctk.CTkButton(tab, text="Refresh", width=80)
        self.refresh_ckpt_btn.grid(row=0, column=2, padx=10, pady=10, sticky="w")
        
        # Negative Prompt
        ctk.CTkLabel(tab, text="Negative Prompt:").grid(row=1, column=0, padx=10, pady=10, sticky="nw")
        self.neg_prompt_entry = ctk.CTkTextbox(tab, width=400, height=80)
        self.neg_prompt_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="w")
        
        # Steps & CFG
        ctk.CTkLabel(tab, text="Steps:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.steps_entry = ctk.CTkEntry(tab, width=80)
        self.steps_entry.insert(0, "20")
        self.steps_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(tab, text="CFG Scale:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.cfg_entry = ctk.CTkEntry(tab, width=80)
        self.cfg_entry.insert(0, "7.0")
        self.cfg_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        # Width & Height
        size_frame = ctk.CTkFrame(tab, fg_color="transparent")
        size_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        ctk.CTkLabel(size_frame, text="Width:").pack(side="left")
        self.width_entry = ctk.CTkEntry(size_frame, width=80)
        self.width_entry.insert(0, "512")
        self.width_entry.pack(side="left", padx=(5, 20))
        
        ctk.CTkLabel(size_frame, text="Height:").pack(side="left")
        self.height_entry = ctk.CTkEntry(size_frame, width=80)
        self.height_entry.insert(0, "512")
        self.height_entry.pack(side="left", padx=5)

    def setup_preset_tab(self):
        tab = self.tabview.tab("Preset Management")
        
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=1)
        tab.grid_rowconfigure(0, weight=1)
        
        # Situations
        sit_frame = ctk.CTkFrame(tab)
        sit_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(sit_frame, text="Situations").pack(pady=5)
        self.sit_listbox = ctk.CTkTextbox(sit_frame, height=200)
        self.sit_listbox.pack(fill="x", padx=10, pady=5)
        
        sit_btn_frame = ctk.CTkFrame(sit_frame, fg_color="transparent")
        sit_btn_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(sit_btn_frame, text="Edit", width=60).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(sit_btn_frame, text="Delete", width=60, fg_color="#C62828", hover_color="#b71c1c").pack(side="left", padx=5, expand=True, fill="x")
        
        # Characters
        char_frame = ctk.CTkFrame(tab)
        char_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(char_frame, text="Characters").pack(pady=5)
        self.char_listbox = ctk.CTkTextbox(char_frame, height=200)
        self.char_listbox.pack(fill="x", padx=10, pady=5)
        
        char_btn_frame = ctk.CTkFrame(char_frame, fg_color="transparent")
        char_btn_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(char_btn_frame, text="Edit", width=60).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(char_btn_frame, text="Delete", width=60, fg_color="#C62828", hover_color="#b71c1c").pack(side="left", padx=5, expand=True, fill="x")
