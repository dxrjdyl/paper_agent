import uuid
from agents.base import BaseAgent
from services.pdf_service import PDFService
from services.chunking import chunk_text
from services.library_db import LibraryDB
from services.vector_store import VectorStore
from services.poster_service import PosterService
from prompts.prompt_templates import (
    PAPER_INTERPRET_PROMPT, KEY_INFO_PROMPT, DEEP_ANALYSIS_PROMPT,
    POSTER_PROMPT, REVIEW_PROMPT, POLISH_TRANSLATE_PROMPT
)

MAX_CONTEXT = 14000

def _short(text: str, limit: int = MAX_CONTEXT) -> str:
    return text[:limit]

class IngestionAgent(BaseAgent):
    name = "文献入库Agent"
    def __init__(self):
        super().__init__()
        self.pdf = PDFService()
        self.db = LibraryDB()
        self.vs = VectorStore()

    def run(self, state: dict) -> dict:
        pdf_path = state["pdf_path"]
        raw_text = self.pdf.extract_text(pdf_path)
        metadata = self.pdf.extract_metadata(pdf_path)
        paper_id = state.get("paper_id") or uuid.uuid4().hex[:12]
        title = state.get("title") or metadata.get("title") or paper_id
        authors = state.get("authors", metadata.get("author", ""))
        year = state.get("year", "")
        chunks = chunk_text(raw_text)
        self.db.upsert_paper(paper_id, title, authors, year, pdf_path)
        self.db.add_chunks(paper_id, chunks)
        self.vs.add_paper_chunks(paper_id, title, chunks)
        state.update({"paper_id": paper_id, "title": title, "authors": authors, "year": year, "raw_text": raw_text, "chunks": chunks, "metadata": metadata})
        return self.log(state, f"完成 PDF 解析与向量化，共 {len(chunks)} 个片段。")

class KeyInfoAgent(BaseAgent):
    name = "关键信息提取Agent"
    def run(self, state: dict) -> dict:
        prompt = KEY_INFO_PROMPT.format(title=state.get("title", ""), text=_short(state.get("raw_text", "")))
        state["key_info"] = self.llm.chat(prompt)
        return self.log(state, "完成关键信息提取。")

class InterpretationAgent(BaseAgent):
    name = "文献解读Agent"
    def run(self, state: dict) -> dict:
        prompt = PAPER_INTERPRET_PROMPT.format(user_prompt=state.get("prompt", ""), title=state.get("title", ""), text=_short(state.get("raw_text", "")))
        state["interpretation"] = self.llm.chat(prompt)
        return self.log(state, "完成结构化文献解读。")

class DeepAnalysisAgent(BaseAgent):
    name = "深度解析Agent"
    def run(self, state: dict) -> dict:
        prompt = DEEP_ANALYSIS_PROMPT.format(user_prompt=state.get("prompt", ""), title=state.get("title", ""), text=_short(state.get("raw_text", "")))
        state["deep_analysis"] = self.llm.chat(prompt)
        return self.log(state, "完成深度解析。")

class PosterAgent(BaseAgent):
    name = "学术海报Agent"
    def __init__(self):
        super().__init__()
        self.poster = PosterService()
        self.db = LibraryDB()

    def run(self, state: dict) -> dict:
        prompt = POSTER_PROMPT.format(title=state.get("title", ""), text=_short(state.get("raw_text", "")))
        poster_text = self.llm.chat(prompt, temperature=0.3)
        poster_path = self.poster.create_poster_pdf(state["paper_id"], state.get("title", ""), poster_text)
        state["poster_path"] = str(poster_path)
        self.db.upsert_paper(
            state["paper_id"], state.get("title", ""), state.get("authors", ""), state.get("year", ""),
            state.get("pdf_path", ""), str(poster_path), state.get("key_info", ""), state.get("deep_analysis", ""), state.get("interpretation", "")
        )
        return self.log(state, f"完成学术海报生成：{poster_path}")

class LibraryWriterAgent(BaseAgent):
    name = "文献库更新Agent"
    def __init__(self):
        super().__init__()
        self.db = LibraryDB()

    def run(self, state: dict) -> dict:
        self.db.upsert_paper(
            state["paper_id"], state.get("title", ""), state.get("authors", ""), state.get("year", ""),
            state.get("pdf_path", ""), state.get("poster_path", ""), state.get("key_info", ""), state.get("deep_analysis", ""), state.get("interpretation", "")
        )
        return self.log(state, "分析结果已保存到文献库。")

class ReviewAgent(BaseAgent):
    name = "综述写作Agent"
    def __init__(self):
        super().__init__()
        self.vs = VectorStore()

    def run(self, topic: str, user_prompt: str = "", n_results: int = 8) -> dict:
        retrieved = self.vs.search(topic + " " + user_prompt, n_results=n_results)
        context_parts = []
        for r in retrieved:
            meta = r.get("metadata", {})
            pid = meta.get("paper_id", "UNKNOWN")
            title = meta.get("title", "")
            context_parts.append(f"[文献ID:{pid}] 题名：{title}\n片段：{r['content']}")
        context = "\n\n".join(context_parts)
        prompt = REVIEW_PROMPT.format(topic=topic, user_prompt=user_prompt, context=context)
        review = self.llm.chat(prompt, temperature=0.25)
        return {"topic": topic, "retrieved_docs": retrieved, "review_text": review}

class PolishTranslateAgent(BaseAgent):
    name = "润色翻译Agent"
    def run(self, text: str, task: str) -> str:
        prompt = POLISH_TRANSLATE_PROMPT.format(text=text, task=task)
        return self.llm.chat(prompt, temperature=0.2)
