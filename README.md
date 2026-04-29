# 研究生多Agent文献协同系统

这是一个面向研究生日常科研使用的本地文献智能系统，支持：

1. 上传 PDF 文献并自动解析；
2. 多 Agent 协同完成文献解读、关键信息提取、深度解析；
3. 自动生成结构清晰的学术海报 PDF，并保存到文献库；
4. 构建本地 SQLite 文献库和 Chroma 向量库；
5. 写文献综述时自动检索文献库，匹配相关文献片段并生成带 `[文献ID]` 的引用草稿；
6. 支持中文润色、中译英、英译中、英文论文润色。

## 1. 项目结构

```text
graduate_paper_agent/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── schemas.py
├── agents/
│   ├── base.py
│   ├── literature_agents.py
│   └── workflow.py
├── services/
│   ├── pdf_service.py
│   ├── chunking.py
│   ├── vector_store.py
│   ├── library_db.py
│   ├── poster_service.py
│   └── llm_service.py
├── prompts/
│   └── prompt_templates.py
└── data/
    ├── pdfs/
    ├── posters/
    ├── chroma/
    └── exports/
```

## 2. 安装

建议 Python 3.10 或 3.11。

```bash
cd graduate_paper_agent
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## 3. 配置模型

复制环境变量文件：

```bash
cp .env.example .env
```

然后在 `.env` 中填写：

```text
OPENAI_API_KEY=你的key
OPENAI_MODEL=gpt-4o-mini
```

如果不配置 `OPENAI_API_KEY`，系统仍可打开，但大模型输出会变成离线占位文本。

## 4. 启动

```bash
streamlit run app.py
```

浏览器打开后，即可上传 PDF 文献。

## 5. 多Agent设计

系统内置 6 个核心 Agent：

- 文献入库Agent：保存 PDF、提取全文、切分 chunk、写入 SQLite、写入 Chroma；
- 关键信息提取Agent：面向研究生日常读文献，提取研究对象、方法、结果、可引用观点；
- 文献解读Agent：生成结构化文献解读；
- 深度解析Agent：从科研逻辑、方法可信度、局限性、复现路径等角度分析；
- 学术海报Agent：生成海报文案，并用 ReportLab 输出 A3 横版 PDF；
- 文献库更新Agent：把所有分析结果统一保存到本地文献库。

`agents/workflow.py` 中优先使用 LangGraph 的 StateGraph；如果环境中 LangGraph 不可用，会自动退化为顺序编排，保证系统可运行。

## 6. 数据保存位置

- 上传 PDF：`data/pdfs/`
- 学术海报：`data/posters/`
- SQLite 文献库：`data/library.sqlite3`
- Chroma 向量库：`data/chroma/`

## 7. 注意事项

1. PDF 如果是扫描件，需要先 OCR，本版本主要处理文本型 PDF。
2. 自动引用采用 RAG 检索匹配，不等同于最终论文中的规范参考文献格式；正式投稿前请人工核对作者、年份、题名、期刊等信息。
3. 海报 PDF 使用系统字体。如果中文显示异常，请安装微软雅黑、Noto Sans CJK 或文泉驿字体。
4. 本项目适合作为可扩展原型，你可以继续增加 Zotero 接口、DOI 元数据解析、GB/T 7714 参考文献格式化、OCR、图表抽取等功能。
