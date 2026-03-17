import json
import os

class ConfigManager:
    def __init__(self, config_dir="."):
        self.config_dir = config_dir
        self.config_file = os.path.join(self.config_dir, "config.json")
        self.presets_file = os.path.join(self.config_dir, "presets.json")
        self.queue_state_file = os.path.join(self.config_dir, "queue_state.json")
        
        self.config = self.load_config()
        self.presets = self.load_presets()
        self.queue_state = self.load_queue_state()
        
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
                "freeu_s2": 0.95
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
            "situations": [{"name": t("default_sit_name"), "text": "1girl, outdoors, highly detailed"}],
            "characters": [{"name": t("default_char_name"), "text": "masterpiece, best quality, smiling"}]
        }
        loaded = self.load_json(self.presets_file, default_presets)
        if "situations" not in loaded: loaded["situations"] = default_presets["situations"]
        if "characters" not in loaded: loaded["characters"] = default_presets["characters"]
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
