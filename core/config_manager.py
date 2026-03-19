import json
import os
import uuid

class ConfigManager:
    def __init__(self, config_dir="."):
        self.config_dir = config_dir
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.presets_file = os.path.join(self.config_dir, "presets.json")
        self.queue_state_file = os.path.join(self.config_dir, "queue_state.json")
        self.freeu_presets_file = os.path.join(self.config_dir, "freeu_presets.json")
        
        self.config = self.load_config()
        self.presets = self.load_presets()
        self.queue_state = self.load_queue_state()
        self.freeu_presets = self.load_freeu_presets()
        
        # Initialize language
        from core.i18n import set_language
        set_language(self.config.get("language", "ja"))

    def load_json(self, filepath, default_data):
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
        return default_data
        
    def save_json(self, filepath, data):
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")

    def load_config(self):
        default_config = {
            "api_url": "http://127.0.0.1:7860",
            "save_dir": "./outputs",
            "theme": "Dark",
            "language": "ja",
            "base_params": {
                "checkpoint": "",
                "negative_prompt": "",
                "steps": 20,
                "cfg_scale": 7.0,
                "width": 512,
                "height": 512
            },
            "global_params": {
                "batch_count": 1,
                "freeu_enable": False,
                "freeu_b1": 1.01,
                "freeu_b2": 1.02,
                "freeu_s1": 0.99,
                "freeu_s2": 0.95,
                "freeu_start": 0,
                "freeu_end": 1,
                "adetailer_enable": False,
                "adetailer_model": "face_yolov8n.pt",
                "adetailer_denoising": 0.4,
                "adetailer_prompt": ""
            }
        }
        loaded = self.load_json(self.config_file, default_config)
        # Verify structure
        if "base_params" not in loaded: loaded["base_params"] = default_config["base_params"]
        if "global_params" not in loaded: loaded["global_params"] = default_config["global_params"]
        return loaded
        
    def save_config(self):
        self.save_json(self.config_file, self.config)
        
    def load_presets(self):
        from core.i18n import t
        default_presets = {
            "situations": [{"name": t("default_sit_name"), "text_front": "1girl, outdoors, highly detailed", "text_back": ""}],
            "characters": [{"name": t("default_char_name"), "text": "masterpiece, best quality, smiling"}]
        }
        loaded = self.load_json(self.presets_file, default_presets)
        if "situations" not in loaded: loaded["situations"] = default_presets["situations"]
        if "characters" not in loaded: loaded["characters"] = default_presets["characters"]
        
        # Add UI IDs for stable keys in ReorderableListView
        for key in ["situations", "characters"]:
            for item in loaded.get(key, []):
                if "_ui_id" not in item:
                    item["_ui_id"] = str(uuid.uuid4())
        return loaded
        
    def save_presets(self):
        self.save_json(self.presets_file, self.presets)
        
    def load_queue_state(self):
        default_state = {
            "queue": []
        }
        loaded = self.load_json(self.queue_state_file, default_state)
        if "queue" not in loaded: loaded["queue"] = default_state["queue"]
        return loaded
        
    def save_queue_state(self):
        self.save_json(self.queue_state_file, self.queue_state)

    def load_freeu_presets(self):
        default = {"presets": []}
        loaded = self.load_json(self.freeu_presets_file, default)
        if "presets" not in loaded:
            loaded["presets"] = []
        return loaded

    def save_freeu_presets(self):
        self.save_json(self.freeu_presets_file, self.freeu_presets)

    def add_freeu_preset(self, name, params):
        """FreeUプリセットを追加して保存する。"""
        self.freeu_presets["presets"].append({"name": name, "params": params})
        self.save_freeu_presets()

    def delete_freeu_preset(self, index):
        """指定インデックスのFreeUプリセットを削除して保存する。"""
        presets = self.freeu_presets["presets"]
        if 0 <= index < len(presets):
            presets.pop(index)
            self.save_freeu_presets()
        
    def add_preset(self, type, data):
        """Adds a new preset and saves it."""
        if type in self.presets:
            if "_ui_id" not in data:
                data["_ui_id"] = str(uuid.uuid4())
            self.presets[type].append(data)
            self.save_presets()
