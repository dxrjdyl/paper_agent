from typing import TypedDict, List, Dict, Any, Optional

class PaperState(TypedDict, total=False):
    paper_id: str
    title: str
    authors: str
    year: str
    pdf_path: str
    prompt: str
    raw_text: str
    chunks: List[str]
    metadata: Dict[str, Any]
    key_info: str
    deep_analysis: str
    interpretation: str
    poster_path: str
    logs: List[str]

class ReviewState(TypedDict, total=False):
    topic: str
    user_prompt: str
    retrieved_docs: List[Dict[str, Any]]
    outline: str
    review_text: str
    references: str
