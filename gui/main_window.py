import customtkinter as ctk

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("SD Forge Queue Manager")
        self.geometry("1100x700")
        self.minsize(900, 600)
        
        # Configure grid layout (1x2)
        self.grid_columnconfigure(0, weight=4)  # Left Column (Settings & Queue)
        self.grid_columnconfigure(1, weight=6)  # Right Column (Preview)
        self.grid_rowconfigure(0, weight=1)

        # Left Frame
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Right Frame
        self.right_frame = ctk.CTkFrame(self)
        self.right_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")
        
        self.setup_left_panel()
        self.setup_right_panel()
        
    def setup_left_panel(self):
        # Configure left grid
        self.left_frame.grid_rowconfigure(2, weight=1)  # Area for Queue Cards
        self.left_frame.grid_columnconfigure(0, weight=1)
        
        # Header Area (Settings button, title)
        header_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(header_frame, text="Queue Manager", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, sticky="w")
        
        settings_btn = ctk.CTkButton(header_frame, text="⚙ Settings", width=80, command=self.open_settings)
        settings_btn.grid(row=0, column=1, sticky="e")
        
        # Global Settings Area
        global_frame = ctk.CTkFrame(self.left_frame)
        global_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(global_frame, text="Global Settings", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        # Batch count
        batch_frame = ctk.CTkFrame(global_frame, fg_color="transparent")
        batch_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(batch_frame, text="Batch count:").pack(side="left", padx=5)
        self.batch_entry = ctk.CTkEntry(batch_frame, width=60)
        self.batch_entry.insert(0, "1")
        self.batch_entry.pack(side="left")
        
        # FreeU Integrated
        freeu_frame = ctk.CTkFrame(global_frame, fg_color="transparent")
        freeu_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.freeu_var = ctk.BooleanVar(value=False)
        self.freeu_switch = ctk.CTkSwitch(freeu_frame, text="FreeU Enable", variable=self.freeu_var)
        self.freeu_switch.grid(row=0, column=0, columnspan=8, sticky="w", pady=2)
        
        ctk.CTkLabel(freeu_frame, text="B1:").grid(row=1, column=0, padx=2)
        ctk.CTkEntry(freeu_frame, width=40).grid(row=1, column=1, padx=2)
        ctk.CTkLabel(freeu_frame, text="B2:").grid(row=1, column=2, padx=2)
        ctk.CTkEntry(freeu_frame, width=40).grid(row=1, column=3, padx=2)
        ctk.CTkLabel(freeu_frame, text="S1:").grid(row=1, column=4, padx=2)
        ctk.CTkEntry(freeu_frame, width=40).grid(row=1, column=5, padx=2)
        ctk.CTkLabel(freeu_frame, text="S2:").grid(row=1, column=6, padx=2)
        ctk.CTkEntry(freeu_frame, width=40).grid(row=1, column=7, padx=2)
        
        # Queue Area (Scrollable)
        self.queue_frame = ctk.CTkScrollableFrame(self.left_frame, label_text="Jobs Queue")
        self.queue_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        # Queue Add Buttons
        btn_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(btn_frame, text="+ キューを追加 (Wizard)", command=self.add_queue_wizard).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="+ 空のキューを追加", command=self.add_empty_queue).grid(row=0, column=1, padx=5, sticky="ew")

    def setup_right_panel(self):
        self.right_frame.grid_rowconfigure(0, weight=1)
        self.right_frame.grid_columnconfigure(0, weight=1)
        
        # Preview Image Area
        self.preview_label = ctk.CTkLabel(self.right_frame, text="Image Preview Area", fg_color="gray20", corner_radius=10)
        self.preview_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")
        
        # Progress Bar & Status
        progress_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        progress_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.set(0.0)
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=5)
        
        self.status_label = ctk.CTkLabel(progress_frame, text="Status: Idle (0%)")
        self.status_label.grid(row=1, column=0, sticky="w")
        
        # Save Preset Button
        save_preset_btn = ctk.CTkButton(self.right_frame, text="💾 現在のプロンプトをプリセット保存", command=self.save_preset)
        save_preset_btn.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        # Generation Control
        self.generate_btn = ctk.CTkButton(self.right_frame, text="▶ 生成開始 (Generate)", fg_color="green", hover_color="darkgreen", height=50, font=ctk.CTkFont(size=16, weight="bold"), command=self.toggle_generation)
        self.generate_btn.grid(row=3, column=0, padx=10, pady=(5, 10), sticky="ew")

    def open_settings(self):
        from gui.settings_window import SettingsWindow
        if not hasattr(self, "settings_window") or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self)
        else:
            self.settings_window.focus()
        
    def add_queue_wizard(self):
        from gui.wizard_dialog import QueueWizardDialog
        # Mock options for now
        situations = ["1girl, outdoor", "cityscape, night"]
        characters = ["hatsune miku", "original character"]
        
        def on_wizard_complete(prompt_text):
            self.add_queue_card(prompt_text)
            
        QueueWizardDialog(self, situations, characters, on_wizard_complete)

    def add_queue_card(self, initial_text=""):
        card = ctk.CTkFrame(self.queue_frame)
        card.pack(fill="x", padx=5, pady=5)
        
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(header, text="Queue Item", font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkButton(header, text="🗑", width=30, fg_color="#C62828", hover_color="#b71c1c", command=card.destroy).pack(side="right")
        
        textbox = ctk.CTkTextbox(card, height=60)
        textbox.pack(fill="x", padx=5, pady=5)
        if initial_text:
            textbox.insert("1.0", initial_text)

    def add_empty_queue(self):
        self.add_queue_card("")

    def toggle_generation(self):
        print("Toggle Generation")

    def save_preset(self):
        from gui.preset_save_dialog import PresetSaveDialog
        
        # Mock currently generated prompt
        current_prompt = "1girl, outdoors, smiling"
        
        def on_preset_save(sit_data, char_data):
            print("Saved Situation:", sit_data)
            print("Saved Character:", char_data)
            
        PresetSaveDialog(self, current_prompt, on_preset_save)
