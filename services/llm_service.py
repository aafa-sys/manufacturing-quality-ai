import json
import logging
import re
from typing import Dict, Any, Optional

from google import genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config import GEMINI_API_KEY
import os
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, model: str = None):
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY tidak ditemukan di file .env")

        if model is None:
            model = GEMINI_MODEL
            
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = model

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((json.JSONDecodeError, KeyError, TypeError, ValueError)),
        reraise=True
    )
    def generate_structured_json(self, prompt: str) -> Dict[str, Any]:
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "temperature": 0.0,
                }
            )
            usage = response.usage_metadata
            if usage:
                logger.info(
                    f"Token usage - Input: {usage.prompt_token_count}, "
                    f"Output: {usage.candidates_token_count}, "
                    f"Total: {usage.total_token_count}"
    )
            # Hitung estimasi biaya (sesuaikan harga model)
            INPUT_PRICE_PER_MILLION = 0.10   # $ per 1 juta token
            OUTPUT_PRICE_PER_MILLION = 0.40  # $ per 1 juta token

            cost_input = (usage.prompt_token_count / 1_000_000) * INPUT_PRICE_PER_MILLION
            cost_output = (usage.candidates_token_count / 1_000_000) * OUTPUT_PRICE_PER_MILLION
            total_cost_usd = cost_input + cost_output
            total_cost_idr = total_cost_usd * 16000  # kurs kasar

            logger.info(
               f"Estimasi biaya: ${total_cost_usd:.6f} "
               f"(~Rp {total_cost_idr:.2f})"
)
            raw_text = response.text
            if not raw_text:
                raise ValueError("Respons kosong dari Gemini")

            try:
                data = json.loads(raw_text)
                return data
            except json.JSONDecodeError:
                extracted = self._extract_json_from_text(raw_text)
                if extracted:
                    return extracted
                raise

        except Exception as e:
            logger.error(f"LLM call error: {e}")
            raise

    def _extract_json_from_text(self, text: str) -> Optional[Dict[str, Any]]:
    # 1. Coba cari blok di dalam markdown fences ```json ... ```
       match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
       if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # 2. Coba cari blok { ... } terluar
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
          candidate = match.group(0)

        # 2a. Coba parse langsung
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            pass

        # 2b. Bersihkan trailing comma
        cleaned = re.sub(r',\s*([}\]])', r'\1', candidate)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

       return None

from services.llm_service import LLMService
