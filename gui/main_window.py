import customtkinter as ctk

from core.config_manager import ConfigManager
from core.api_client import SDForgeAPIClient
from core.queue_manager import QueueManager

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.config_manager = ConfigManager()
        self.api_client = SDForgeAPIClient(self.config_manager.config["api_url"])
        
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
        
        # Load Existing Queue
        self.load_queue_from_state()
        
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
        
        gp = self.config_manager.config.get("global_params", {})
        
        # Batch count
        batch_frame = ctk.CTkFrame(global_frame, fg_color="transparent")
        batch_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(batch_frame, text="Batch count:").pack(side="left", padx=5)
        self.batch_entry = ctk.CTkEntry(batch_frame, width=60)
        self.batch_entry.insert(0, str(gp.get("batch_count", 1)))
        self.batch_entry.pack(side="left")
        
        # FreeU Integrated
        freeu_frame = ctk.CTkFrame(global_frame, fg_color="transparent")
        freeu_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        self.freeu_var = ctk.BooleanVar(value=gp.get("freeu_enable", False))
        self.freeu_switch = ctk.CTkSwitch(freeu_frame, text="FreeU Enable", variable=self.freeu_var)
        self.freeu_switch.grid(row=0, column=0, columnspan=8, sticky="w", pady=2)
        
        self.freeu_entries = {}
        fields = [("B1", "freeu_b1"), ("B2", "freeu_b2"), ("S1", "freeu_s1"), ("S2", "freeu_s2")]
        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(freeu_frame, text=f"{label}:").grid(row=1, column=i*2, padx=2)
            entry = ctk.CTkEntry(freeu_frame, width=40)
            entry.insert(0, str(gp.get(key, 1.0)))
            entry.grid(row=1, column=i*2+1, padx=2)
            self.freeu_entries[key] = entry
        
        # Queue Area (Scrollable)
        self.queue_frame = ctk.CTkScrollableFrame(self.left_frame, label_text="Jobs Queue")
        self.queue_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        # Queue Add Buttons
        btn_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        btn_frame.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkButton(btn_frame, text="+ キューを追加 (Wizard)", command=self.add_queue_wizard).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="+ 空のキューを追加", command=self.add_empty_queue).grid(row=0, column=1, padx=5, sticky="ew")

    def load_queue_from_state(self):
        for item in self.config_manager.queue_state.get("queue", []):
            self.add_queue_card(item.get("prompt", ""), save=False)

    def open_settings(self):
        from gui.settings_window import SettingsWindow
        if not hasattr(self, "settings_window") or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self, self.config_manager)
        else:
            self.settings_window.focus()
        
    def add_queue_wizard(self):
        from gui.wizard_dialog import QueueWizardDialog
        
        situations = [item["text"] for item in self.config_manager.presets["situations"]]
        characters = [item["text"] for item in self.config_manager.presets["characters"]]
        
        def on_wizard_complete(prompt_text):
            self.add_queue_card(prompt_text)
            
        QueueWizardDialog(self, situations, characters, on_wizard_complete)

    def add_queue_card(self, initial_text="", save=True):
        card = ctk.CTkFrame(self.queue_frame)
        card.pack(fill="x", padx=5, pady=5)
        
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=5, pady=2)
        ctk.CTkLabel(header, text="Queue Item", font=ctk.CTkFont(weight="bold")).pack(side="left")
        
        def delete_item():
            card.destroy()
            self.save_current_queue_state()
            
        ctk.CTkButton(header, text="🗑", width=30, fg_color="#C62828", hover_color="#b71c1c", command=delete_item).pack(side="right")
        
        textbox = ctk.CTkTextbox(card, height=60)
        textbox.pack(fill="x", padx=5, pady=5)
        if initial_text:
            textbox.insert("1.0", initial_text)
            
        textbox.bind("<FocusOut>", lambda e: self.save_current_queue_state())
        
        if save:
            self.save_current_queue_state()

    def save_current_queue_state(self):
        queue_data = []
        for card in self.queue_frame.winfo_children():
            if isinstance(card, ctk.CTkFrame):
                for child in card.winfo_children():
                    if isinstance(child, ctk.CTkTextbox):
                        text = child.get("1.0", "end-1c").strip()
                        queue_data.append({"prompt": text})
        self.config_manager.queue_state["queue"] = queue_data
        self.config_manager.save_queue_state()

    def add_empty_queue(self):
        self.add_queue_card("")

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

    def toggle_generation(self):
        if not hasattr(self, "queue_manager") or not self.queue_manager.is_running:
            self.start_generation()
        else:
            self.stop_generation()

    def start_generation(self):
        import asyncio
        import threading
        
        # Update UI state
        self.generate_btn.configure(text="■ キャンセル (Cancel)", fg_color="#C62828", hover_color="#b71c1c")
        
        # Sync current queue from UI to config
        self.save_current_queue_state()
        
        # Setup QueueManager with UI callbacks
        callbacks = {
            "on_start": self.on_gen_start,
            "on_progress": self.on_gen_progress,
            "on_finish": self.on_gen_finish,
            "on_error": self.on_gen_error,
            "on_queue_empty": self.on_gen_complete
        }
        
        self.queue_manager = QueueManager(self.config_manager, self.api_client, callbacks)
        
        # Run in thread since loop.run_until_complete is blocking
        def run_asyncio():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.queue_manager.run_queue())
            
        threading.Thread(target=run_asyncio, daemon=True).start()

    def stop_generation(self):
        import asyncio
        if hasattr(self, "queue_manager"):
            # We need to run the async cancel in the event loop or a temporary one
            async def do_cancel():
                await self.queue_manager.cancel()
            asyncio.run(do_cancel())

    def on_gen_start(self, item):
        self.after(0, lambda: self.status_label.configure(text=f"Status: Generating..."))

    def on_gen_progress(self, info):
        progress = info.get("progress", 0)
        self.after(0, lambda: [
            self.progress_bar.set(progress),
            self.status_label.configure(text=f"Status: Generating ({int(progress*100)}%)")
        ])

    def on_gen_finish(self, image, filepath):
        # Update preview (simplified)
        from PIL import ImageTk
        img_w, img_h = self.preview_label.winfo_width(), self.preview_label.winfo_height()
        if img_w < 10: img_w, img_h = 512, 512
        
        image.thumbnail((img_w, img_h))
        photo = ImageTk.PhotoImage(image)
        
        def update_ui():
            self.preview_label.configure(image=photo, text="")
            self.preview_label.image = photo  # Keep reference
            self.refresh_queue_ui_after_pop()
            
        self.after(0, update_ui)

    def refresh_queue_ui_after_pop(self):
        # Remove the top card from UI if it matches the completed one
        children = self.queue_frame.winfo_children()
        if children:
            children[0].destroy()

    def on_gen_error(self, err_msg):
        from tkinter import messagebox
        self.after(0, lambda: [
            messagebox.showerror("Error", err_msg),
            self.on_gen_complete()
        ])

    def on_gen_complete(self):
        self.after(0, lambda: [
            self.generate_btn.configure(text="▶ 生成開始 (Generate)", fg_color="green", hover_color="darkgreen"),
            self.status_label.configure(text="Status: Idle (0%)"),
            self.progress_bar.set(0.0)
        ])

    def save_preset(self):
        from gui.preset_save_dialog import PresetSaveDialog
        
        # In a real app, you might want to get the last generated prompt
        # For now, we take it from the configuration or current active card
        current_prompt = "1girl, outdoors, smiling" # Mock or get from UI
        
        def on_preset_save(sit_data, char_data):
            if sit_data.get("name"):
                self.config_manager.presets["situations"].append(sit_data)
            if char_data.get("name"):
                self.config_manager.presets["characters"].append(char_data)
            self.config_manager.save_presets()
            
        PresetSaveDialog(self, current_prompt, on_preset_save)

