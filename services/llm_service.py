from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

class LLMService:
    def __init__(self, model: str = OPENAI_MODEL):
        self.model = model
        self.available = bool(OPENAI_API_KEY)
        self.client = OpenAI(api_key=OPENAI_API_KEY) if self.available else None

    def chat(self, prompt: str, temperature: float = 0.2) -> str:
        if not self.available:
            return (
                "[未检测到 OPENAI_API_KEY，当前为离线占位输出。]\n\n"
                "请在 .env 中配置 OPENAI_API_KEY 后重新运行，即可得到真实模型分析。\n\n"
                f"收到的 Prompt 摘要：{prompt[:1200]}"
            )
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是严谨、专业、适合研究生日常科研工作的多Agent系统。"},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""
