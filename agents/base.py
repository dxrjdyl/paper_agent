from services.llm_service import LLMService

class BaseAgent:
    name = "base"
    def __init__(self, llm: LLMService | None = None):
        self.llm = llm or LLMService()

    def log(self, state: dict, message: str):
        state.setdefault("logs", []).append(f"[{self.name}] {message}")
        return state
