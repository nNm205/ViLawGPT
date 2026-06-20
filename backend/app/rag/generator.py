from __future__ import annotations
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from app.core.config import settings

class Generator:
    def __init__(self):
        self.model_name = settings.LLM_MODEL

        # =========================
        # Tokenizer
        # =========================
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )

        # =========================
        # Model loading
        # =========================

        # Case 1: GPU available
        if torch.cuda.is_available():
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="auto",
                torch_dtype=torch.float16,
                load_in_4bit=True if getattr(settings, "USE_4BIT", True) else False,
                trust_remote_code=True
            )
        # Case 2: CPU fallback
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                device_map="cpu",
                trust_remote_code=True
            )

        self.model.eval()

    def generate(self, prompt: str) -> str:
        messages = [{
            "role": "user",
            "content": prompt
        }]

        # Chat template (Qwen format)
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.0,  
                top_p=1.0,
                do_sample=False
            )

        response = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True
        )

        return response.strip()