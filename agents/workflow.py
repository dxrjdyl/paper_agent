try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_AVAILABLE = True
except Exception:
    LANGGRAPH_AVAILABLE = False
    StateGraph = None
    END = None

from schemas import PaperState
from agents.literature_agents import (
    IngestionAgent, KeyInfoAgent, InterpretationAgent,
    DeepAnalysisAgent, PosterAgent, LibraryWriterAgent
)

class LiteratureWorkflow:
    """
    多Agent协同流程：
    PDF入库 -> 关键信息提取 -> 文献解读 -> 深度解析 -> 海报生成 -> 文献库保存

    如果 LangGraph 可用，使用 StateGraph；否则使用顺序编排，保证项目能运行。
    """
    def __init__(self):
        self.ingest = IngestionAgent()
        self.key = KeyInfoAgent()
        self.interpret = InterpretationAgent()
        self.deep = DeepAnalysisAgent()
        self.poster = PosterAgent()
        self.writer = LibraryWriterAgent()
        self.graph = self._build_graph() if LANGGRAPH_AVAILABLE else None

    def _build_graph(self):
        g = StateGraph(PaperState)
        g.add_node("ingest", self.ingest.run)
        g.add_node("key_info", self.key.run)
        g.add_node("interpret", self.interpret.run)
        g.add_node("deep_analysis", self.deep.run)
        g.add_node("poster", self.poster.run)
        g.add_node("save", self.writer.run)

        g.set_entry_point("ingest")
        g.add_edge("ingest", "key_info")
        g.add_edge("key_info", "interpret")
        g.add_edge("interpret", "deep_analysis")
        g.add_edge("deep_analysis", "poster")
        g.add_edge("poster", "save")
        g.add_edge("save", END)
        return g.compile()

    def run(self, state: PaperState) -> PaperState:
        if self.graph:
            return self.graph.invoke(state)
        for agent in [self.ingest, self.key, self.interpret, self.deep, self.poster, self.writer]:
            state = agent.run(state)
        return state
