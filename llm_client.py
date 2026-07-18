import sys
import httpx
from typing import Dict, Any, Optional

sys.path.insert(0, '/Users/tnt/keys')
try:
    from api_keys import NVIDIA_MODELS, nvidia_chat
except ImportError:
    NVIDIA_MODELS = {}
    nvidia_chat = None


class NIMClient:
    """Client for NVIDIA NIM API."""

    def __init__(self):
        self.base_url = "https://integrate.api.nvidia.com/v1"
        self.models = NVIDIA_MODELS if NVIDIA_MODELS else self._default_models()
        self.api_key = self._get_api_key()

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment or keys module."""
        if nvidia_chat:
            return getattr(nvidia_chat, 'api_key', None)
        return None

    def _default_models(self) -> Dict[str, str]:
        """Default model mapping if api_keys module unavailable."""
        return {
            'nemotron': 'nvidia/llama-3.1-nemotron-ultra-253b-v1',
            'deepseek': 'deepseek-ai/deepseek-r1',
            'qwq': 'qwen/qwq-32b',
            'llama': 'meta/llama-3.3-70b-instruct',
        }

    async def call_model(self, model: str, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Call NVIDIA NIM API with given prompts."""
        if not self.api_key:
            return self._mock_response(model)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "top_p": 1.0,
            "max_tokens": 2048,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    def _mock_response(self, model: str) -> Dict[str, Any]:
        """Mock response when API key unavailable."""
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": "Mock response: API key not configured",
                        "reasoning_content": f"Mock reasoning for {model}: This would show actual reasoning chain."
                    }
                }
            ],
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 100,
            }
        }

    def get_available_models(self) -> Dict[str, str]:
        """Return available models."""
        return self.models
