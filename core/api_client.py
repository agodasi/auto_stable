import aiohttp
import base64
from io import BytesIO
from PIL import Image

class SDForgeAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        
    async def generate_image(self, payload):
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/sdapi/v1/txt2img", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("images", [])
                else:
                    text = await response.text()
                    raise Exception(f"API Error {response.status}: {text}")
                    
    async def get_progress(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/sdapi/v1/progress") as response:
                if response.status == 200:
                    return await response.json()
                return {}

    async def interrupt(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/sdapi/v1/interrupt") as response:
                return response.status == 200

    async def get_models(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/sdapi/v1/sd-models") as response:
                if response.status == 200:
                    return await response.json()
                return []

    def decode_base64_image(self, b64_str):
        image_data = base64.b64decode(b64_str)
        image = Image.open(BytesIO(image_data))
        return image
