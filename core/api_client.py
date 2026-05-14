import aiohttp
import base64
from io import BytesIO
from PIL import Image

class SDForgeAPIClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self._session = None
        self._timeout = aiohttp.ClientTimeout(total=3600, connect=10, sock_read=3600) # 1 hour
        self._connector = aiohttp.TCPConnector(keepalive_timeout=60, limit=1)

    async def get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=self._timeout, 
                connector=self._connector
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def generate_image(self, payload):
        session = await self.get_session()
        try:
            async with session.post(f"{self.base_url}/sdapi/v1/txt2img", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("images", [])
                else:
                    text = await response.text()
                    err = f"API Error {response.status}: {text}"
                    print(err, flush=True)
                    raise Exception(err)
        except Exception as e:
            print(f"API Request Error (txt2img): {e}", flush=True)
            raise e
                    
    async def get_progress(self):
        # Progress check should have short timeout to not hang
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(f"{self.base_url}/sdapi/v1/progress") as response:
                    if response.status == 200:
                        return await response.json()
                    return {}
            except Exception:
                return {}

    async def interrupt(self):
        session = await self.get_session()
        async with session.post(f"{self.base_url}/sdapi/v1/interrupt") as response:
            return response.status == 200

    async def get_models(self):
        session = await self.get_session()
        async with session.get(f"{self.base_url}/sdapi/v1/sd-models") as response:
            if response.status == 200:
                return await response.json()
            return []

    async def get_samplers(self):
        session = await self.get_session()
        async with session.get(f"{self.base_url}/sdapi/v1/samplers") as response:
            if response.status == 200:
                return await response.json()
            return []

    async def get_schedulers(self):
        session = await self.get_session()
        try:
            async with session.get(f"{self.base_url}/sdapi/v1/schedulers") as response:
                if response.status == 200:
                    return await response.json()
                return []
        except Exception:
            return []

    async def is_busy(self):
        """サーバーが現在生成中（ビジー状態）かどうかを判定する。"""
        try:
            progress = await self.get_progress()
            # progress["state"]["job_count"] が 0 より大きい場合はビジー
            state = progress.get("state", {})
            return state.get("job_count", 0) > 0
        except Exception:
            return False

    def decode_base64_image(self, b64_str):
        image_data = base64.b64decode(b64_str)
        image = Image.open(BytesIO(image_data))
        return image
