import customtkinter as ctk

class QueueWizardDialog(ctk.CTkToplevel):
    def __init__(self, parent, situations, characters, on_complete):
        super().__init__(parent)
        self.title("キューの追加 (ウィザード)")
        self.geometry("400x320")
        self.attributes("-topmost", True)
        
        self.situations = ["(スキップ)"] + situations
        self.characters = ["(スキップ)"] + characters
        self.on_complete = on_complete
        
        self.step = 1
        self.selected_situation = ""
        self.selected_character = ""
        
        # Step 1 Frame
        self.step1_frame = ctk.CTkFrame(self)
        self.step1_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(self.step1_frame, text="ステップ 1: シチュエーションを選択", font=ctk.CTkFont(size=16)).pack(pady=10)
        self.sit_var = ctk.StringVar(value=self.situations[0])
        self.sit_dropdown = ctk.CTkOptionMenu(self.step1_frame, values=self.situations, variable=self.sit_var, width=250)
        self.sit_dropdown.pack(pady=20)
        
        ctk.CTkButton(self.step1_frame, text="次へ", command=self.go_to_step2).pack(pady=10)
        
        # Step 2 Frame
        self.step2_frame = ctk.CTkFrame(self)
        
        ctk.CTkLabel(self.step2_frame, text="ステップ 2: キャラクターを選択", font=ctk.CTkFont(size=16)).pack(pady=10)
        self.char_var = ctk.StringVar(value=self.characters[0])
        self.char_dropdown = ctk.CTkOptionMenu(self.step2_frame, values=self.characters, variable=self.char_var, width=250)
        self.char_dropdown.pack(pady=20)
        
        btn_frame = ctk.CTkFrame(self.step2_frame, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="戻る", command=self.go_to_step1, width=80).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="完了", command=self.finish_wizard, width=80).pack(side="left", padx=10)

    def go_to_step2(self):
        self.selected_situation = self.sit_var.get()
        self.step1_frame.pack_forget()
        self.step2_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
    def go_to_step1(self):
        self.step2_frame.pack_forget()
        self.step1_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
    def finish_wizard(self):
        self.selected_character = self.char_var.get()
        prompt_parts = []
        if self.selected_situation != "(スキップ)":
            prompt_parts.append(self.selected_situation)
        if self.selected_character != "(スキップ)":
            prompt_parts.append(self.selected_character)
            
        final_text = "\n".join(prompt_parts)
        self.on_complete(final_text)
        self.destroy()
