import customtkinter as ctk

class PresetSaveDialog(ctk.CTkToplevel):
    def __init__(self, parent, current_prompt, on_save):
        super().__init__(parent)
        self.title("現在のプロンプトをプリセット保存")
        self.geometry("800x600")
        self.attributes("-topmost", True)
        self.on_save = on_save
        
        # Bottom Prompt Area (Permanent)
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        ctk.CTkLabel(self.bottom_frame, text="現在のプロンプト (上の欄へコピー＆ペーストして利用してください):", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=5)
        self.prompt_text = ctk.CTkTextbox(self.bottom_frame, height=100)
        self.prompt_text.pack(fill="x", padx=5, pady=5)
        self.prompt_text.insert("1.0", current_prompt)
        self.prompt_text.configure(state="disabled")
        
        # Top Area container
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(side="top", fill="both", expand=True, padx=10, pady=10)
        
        # Step 1: Situation
        self.step1_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.step1_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(self.step1_frame, text="ステップ 1: シチュエーションとして保存", font=ctk.CTkFont(size=16)).pack(pady=5)
        self.sit_name_entry = ctk.CTkEntry(self.step1_frame, placeholder_text="プリセット名 (新規入力または既存名)", width=400)
        self.sit_name_entry.pack(pady=10)
        self.sit_text_entry = ctk.CTkTextbox(self.step1_frame, height=200)
        self.sit_text_entry.pack(fill="x", padx=20, pady=5)
        
        btn_frame1 = ctk.CTkFrame(self.step1_frame, fg_color="transparent")
        btn_frame1.pack(pady=10)
        ctk.CTkButton(btn_frame1, text="スキップ", command=self.go_step2, width=100).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame1, text="次へ", command=self.go_step2, width=100).pack(side="left", padx=10)
        
        # Step 2: Character
        self.step2_frame = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        
        ctk.CTkLabel(self.step2_frame, text="ステップ 2: キャラクターとして保存", font=ctk.CTkFont(size=16)).pack(pady=5)
        self.char_name_entry = ctk.CTkEntry(self.step2_frame, placeholder_text="プリセット名 (新規入力または既存名)", width=400)
        self.char_name_entry.pack(pady=10)
        self.char_text_entry = ctk.CTkTextbox(self.step2_frame, height=200)
        self.char_text_entry.pack(fill="x", padx=20, pady=5)
        
        btn_frame2 = ctk.CTkFrame(self.step2_frame, fg_color="transparent")
        btn_frame2.pack(pady=10)
        ctk.CTkButton(btn_frame2, text="戻る", command=self.go_step1, width=100).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame2, text="保存", command=self.save_and_close, width=100).pack(side="left", padx=10)

    def go_step1(self):
        self.step2_frame.pack_forget()
        self.step1_frame.pack(fill="both", expand=True)

    def go_step2(self):
        self.step1_frame.pack_forget()
        self.step2_frame.pack(fill="both", expand=True)
        
    def save_and_close(self):
        sit_data = {"name": self.sit_name_entry.get(), "text": self.sit_text_entry.get("1.0", "end-1c").strip()}
        char_data = {"name": self.char_name_entry.get(), "text": self.char_text_entry.get("1.0", "end-1c").strip()}
        self.on_save(sit_data, char_data)
        self.destroy()
