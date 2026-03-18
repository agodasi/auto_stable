import asyncio
from datetime import datetime
import os
from core.api_client import SDForgeAPIClient

class QueueManager:
    def __init__(self, config_manager, api_client: SDForgeAPIClient, ui_callbacks=None):
        self.config_manager = config_manager
        self.api_client = api_client
        self.ui_callbacks = ui_callbacks or {}
        
        self.is_running = False
        self._cancel_requested = False

    def check_save_directory(self):
        save_dir = self.config_manager.config["save_dir"]
        if not os.path.exists(save_dir):
            raise FileNotFoundError(f"Directory not found: {save_dir}")
        return save_dir

    def build_payload(self, prompt, base_params, global_params):
        payload = {
            "prompt": prompt,
            "negative_prompt": base_params.get("negative_prompt", ""),
            "steps": int(base_params.get("steps", 20)),
            "cfg_scale": float(base_params.get("cfg_scale", 7.0)),
            "width": int(base_params.get("width", 512)),
            "height": int(base_params.get("height", 512)),
            "seed": -1,
            "batch_size": 1,
            "n_iter": 1,
            "send_images": True,
            "save_images": False,
        }
        
        checkpoint = base_params.get("checkpoint", "")
        if checkpoint:
            payload["override_settings"] = {"sd_model_checkpoint": checkpoint}

        if global_params.get("freeu_enable", False):
            payload["alwayson_scripts"] = {
                "freeu integrated (sd 1.x, sd 2.x, sdxl)": {
                    "args": [
                        float(global_params.get("freeu_b1", 1.01)),
                        float(global_params.get("freeu_b2", 1.02)),
                        float(global_params.get("freeu_s1", 0.99)),
                        float(global_params.get("freeu_s2", 0.95)),
                        float(global_params.get("freeu_start", 0)),
                        float(global_params.get("freeu_end", 1))
                    ]
                }
            }
        return payload

    async def run_queue(self):
        self.is_running = True
        self._cancel_requested = False
        
        try:
            save_dir = self.check_save_directory()
            queue = self.config_manager.queue_state.get("queue", [])
            
            while queue and not self._cancel_requested:
                current_item = queue[0]
                prompt = current_item.get("prompt", "")
                
                base_params = self.config_manager.config.get("base_params", {})
                global_params = self.config_manager.config.get("global_params", {})
                batch_count = int(global_params.get("batch_count", 1))

                for i in range(batch_count):
                    if self._cancel_requested:
                        break
                        
                    if "on_start" in self.ui_callbacks:
                        import inspect
                        if inspect.iscoroutinefunction(self.ui_callbacks["on_start"]):
                            await self.ui_callbacks["on_start"](current_item, i + 1, batch_count)
                        else:
                            self.ui_callbacks["on_start"](current_item, i + 1, batch_count)

                    payload = self.build_payload(prompt, base_params, global_params)

                    gen_task = asyncio.create_task(self.api_client.generate_image(payload))
                    monitor_task = asyncio.create_task(self._monitor_progress())

                    try:
                        images_b64 = await gen_task
                        monitor_task.cancel()
                        
                        self.config_manager.queue_state["last_finished_prompt"] = prompt
                        self.config_manager.save_queue_state()
                        
                        for j, img_b64 in enumerate(images_b64):
                            image = self.api_client.decode_base64_image(img_b64)
                            
                            # Create date-based subfolder
                            date_folder = datetime.now().strftime("%Y-%m-%d")
                            target_dir = os.path.join(save_dir, date_folder)
                            os.makedirs(target_dir, exist_ok=True)
                            
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            savename = f"{timestamp}_{i:02d}_{j:02d}.png"
                            filepath = os.path.join(target_dir, savename)
                            image.save(filepath, "PNG")
                            
                            if "on_finish" in self.ui_callbacks:
                                # 最後のバッチの最後の画像かどうか
                                is_last = (i == batch_count - 1) and (j == len(images_b64) - 1)
                                import inspect
                                if inspect.iscoroutinefunction(self.ui_callbacks["on_finish"]):
                                    await self.ui_callbacks["on_finish"](image, filepath, is_last)
                                else:
                                    self.ui_callbacks["on_finish"](image, filepath, is_last)
                        
                    except Exception as e:
                        monitor_task.cancel()
                        if not self._cancel_requested:
                            if "on_error" in self.ui_callbacks:
                                import inspect
                                if inspect.iscoroutinefunction(self.ui_callbacks["on_error"]):
                                    await self.ui_callbacks["on_error"](str(e))
                                else:
                                    self.ui_callbacks["on_error"](str(e))
                        break
                
                if not self._cancel_requested:
                    queue.pop(0)

        except Exception as e:
            if not self._cancel_requested:
                if "on_error" in self.ui_callbacks:
                    import inspect
                    if inspect.iscoroutinefunction(self.ui_callbacks["on_error"]):
                        await self.ui_callbacks["on_error"](str(e))
                    else:
                        self.ui_callbacks["on_error"](str(e))

        self.is_running = False
        if "on_queue_empty" in self.ui_callbacks:
            import inspect
            if inspect.iscoroutinefunction(self.ui_callbacks["on_queue_empty"]):
                await self.ui_callbacks["on_queue_empty"]()
            else:
                self.ui_callbacks["on_queue_empty"]()

    async def _monitor_progress(self):
        while not self._cancel_requested:
            try:
                progress_info = await self.api_client.get_progress()
                if "on_progress" in self.ui_callbacks:
                    import inspect
                    if inspect.iscoroutinefunction(self.ui_callbacks["on_progress"]):
                        await self.ui_callbacks["on_progress"](progress_info)
                    else:
                        self.ui_callbacks["on_progress"](progress_info)
            except Exception:
                pass
            await asyncio.sleep(1.0)

    async def cancel(self):
        if self.is_running:
            self._cancel_requested = True
            await self.api_client.interrupt()
