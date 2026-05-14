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

    def build_payload(self, prompt, base_params, global_params, n_iter=1):
        payload = {
            "prompt": prompt,
            "negative_prompt": base_params.get("negative_prompt", ""),
            "sampler_name": base_params.get("sampler_name", "Euler a"),
            "scheduler": base_params.get("scheduler", "Automatic"),
            "steps": int(base_params.get("steps", 20)),
            "cfg_scale": float(base_params.get("cfg_scale", 7.0)),
            "width": int(base_params.get("width", 512)),
            "height": int(base_params.get("height", 512)),
            "seed": -1,
            "batch_size": 1,
            "n_iter": n_iter,
            "send_images": True,
            "save_images": False,
        }
        
        checkpoint = base_params.get("checkpoint", "")
        payload["override_settings"] = {"do_not_show_images_grid": True}
        if checkpoint:
            payload["override_settings"]["sd_model_checkpoint"] = checkpoint

        payload["alwayson_scripts"] = {}
        if global_params.get("freeu_enable", False):
            payload["alwayson_scripts"]["freeu integrated (sd 1.x, sd 2.x, sdxl)"] = {
                "args": [
                    float(global_params.get("freeu_b1", 1.01)),
                    float(global_params.get("freeu_b2", 1.02)),
                    float(global_params.get("freeu_s1", 0.99)),
                    float(global_params.get("freeu_s2", 0.95)),
                    float(global_params.get("freeu_start", 0)),
                    float(global_params.get("freeu_end", 1))
                ]
            }

        if global_params.get("adetailer_enable", False):
            payload["alwayson_scripts"]["ADetailer"] = {
                "args": [
                    {
                        "ad_model": global_params.get("adetailer_model", "face_yolov8n.pt"),
                        "ad_prompt": global_params.get("adetailer_prompt", ""),
                        "ad_negative_prompt": "",
                        "ad_denoising_strength": float(global_params.get("adetailer_denoising", 0.4)),
                        "ad_confidence": 0.3
                    }
                ]
            }
        
        if not payload["alwayson_scripts"]:
            del payload["alwayson_scripts"]

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

                max_retries = 3
                retry_count = 0
                success = False

                while retry_count < max_retries and not self._cancel_requested:
                    payload = self.build_payload(prompt, base_params, global_params, n_iter=batch_count)
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
                            savename = f"{timestamp}_{j:02d}.png"
                            filepath = os.path.join(target_dir, savename)
                            image.save(filepath, "PNG")
                            
                            if "on_finish" in self.ui_callbacks:
                                is_last = (j == len(images_b64) - 1)
                                import inspect
                                if inspect.iscoroutinefunction(self.ui_callbacks["on_finish"]):
                                    await self.ui_callbacks["on_finish"](image, filepath, is_last, j + 1, len(images_b64))
                                else:
                                    self.ui_callbacks["on_finish"](image, filepath, is_last, j + 1, len(images_b64))
                        
                        success = True
                        break # Exit retry loop on success
                        
                    except Exception as e:
                        monitor_task.cancel()
                        retry_count += 1
                        print(f"Generation attempt {retry_count}/{max_retries} failed: {e}", flush=True)
                        
                        if retry_count < max_retries and not self._cancel_requested:
                            # Wait and check if server is still busy
                            wait_sec = 5
                            print(f"Connection lost. Checking server status...", flush=True)
                            
                            # Polling until server is not busy
                            while await self.api_client.is_busy() and not self._cancel_requested:
                                print("Server is still processing. Waiting 10s...", flush=True)
                                await asyncio.sleep(10)
                            
                            print(f"Server is idle. Waiting {wait_sec}s before retry...", flush=True)
                            await asyncio.sleep(wait_sec)
                        else:
                            # Final failure
                            import traceback
                            traceback.print_exc()
                            if not self._cancel_requested:
                                if "on_error" in self.ui_callbacks:
                                    import inspect
                                    if inspect.iscoroutinefunction(self.ui_callbacks["on_error"]):
                                        await self.ui_callbacks["on_error"](str(e))
                                    else:
                                        self.ui_callbacks["on_error"](str(e))
                            break # Exit retry loop

                if not success:
                    # If we failed after all retries, stop the whole queue
                    break
                
                if not self._cancel_requested:
                    queue.pop(0)

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Critical queue error: {e}")
            if not self._cancel_requested:
                if "on_error" in self.ui_callbacks:
                    import inspect
                    if inspect.iscoroutinefunction(self.ui_callbacks["on_error"]):
                        await self.ui_callbacks["on_error"](str(e))
                    else:
                        self.ui_callbacks["on_error"](str(e))

        self.is_running = False
        await self.api_client.close() # Clean up session
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
