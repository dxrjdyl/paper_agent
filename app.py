import streamlit as st
from pathlib import Path
from config import APP_TITLE
from services.pdf_service import PDFService
from services.library_db import LibraryDB
from agents.workflow import LiteratureWorkflow
from agents.literature_agents import ReviewAgent, PolishTranslateAgent

st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title("🎓 研究生多Agent文献协同系统")
st.caption("PDF文献解读｜深度解析｜关键信息提取｜自动海报｜文献库RAG引用｜润色翻译")

pdf_service = PDFService()
db = LibraryDB()

with st.sidebar:
    st.header("功能导航")
    page = st.radio(
        "选择功能",
        ["1 文献上传与多Agent解析", "2 文献库", "3 综述写作与自动引用", "4 润色与中英互译"],
    )
    st.divider()
    st.info("首次运行会下载本地向量模型；如需真实生成，请在 .env 中配置 OPENAI_API_KEY。")

if page == "1 文献上传与多Agent解析":
    st.subheader("📄 上传 PDF 并启动多Agent解析")
    uploaded = st.file_uploader("上传一篇 PDF 文献", type=["pdf"])
    col1, col2, col3 = st.columns(3)
    with col1:
        title = st.text_input("论文题名，可留空自动读取")
    with col2:
        authors = st.text_input("作者，可留空")
    with col3:
        year = st.text_input("年份，可留空")
    user_prompt = st.text_area(
        "你的阅读需求 / Prompt",
        value="请按照研究生组会汇报的要求，提取创新点、方法、实验结论、局限性和可借鉴之处。",
        height=100,
    )
    if st.button("🚀 启动多Agent协同处理", type="primary", disabled=uploaded is None):
        with st.spinner("正在解析、入库、向量化、调用Agent、生成海报……"):
            pdf_path = pdf_service.save_uploaded_pdf(uploaded)
            wf = LiteratureWorkflow()
            state = wf.run({
                "pdf_path": str(pdf_path),
                "title": title,
                "authors": authors,
                "year": year,
                "prompt": user_prompt,
                "logs": [],
            })
        st.success("处理完成，结果已保存到文献库。")
        st.write("### 处理日志")
        st.code("\n".join(state.get("logs", [])))
        tab1, tab2, tab3, tab4 = st.tabs(["关键信息", "文献解读", "深度解析", "学术海报"])
        with tab1:
            st.markdown(state.get("key_info", ""))
        with tab2:
            st.markdown(state.get("interpretation", ""))
        with tab3:
            st.markdown(state.get("deep_analysis", ""))
        with tab4:
            poster_path = state.get("poster_path")
            if poster_path and Path(poster_path).exists():
                st.success(f"海报已保存：{poster_path}")
                with open(poster_path, "rb") as f:
                    st.download_button("下载学术海报 PDF", f, file_name=Path(poster_path).name)
            else:
                st.warning("未生成海报。")

elif page == "2 文献库":
    st.subheader("📚 本地文献库")
    papers = db.list_papers()
    if not papers:
        st.info("文献库为空，请先上传 PDF。")
    else:
        for p in papers:
            with st.expander(f"{p.get('title') or p['paper_id']}  |  ID: {p['paper_id']}"):
                st.write(f"**作者：** {p.get('authors') or '未填写'}")
                st.write(f"**年份：** {p.get('year') or '未填写'}")
                st.write(f"**PDF路径：** `{p.get('pdf_path')}`")
                if p.get("poster_path"):
                    st.write(f"**海报路径：** `{p.get('poster_path')}`")
                    if Path(p["poster_path"]).exists():
                        with open(p["poster_path"], "rb") as f:
                            st.download_button("下载海报", f, file_name=Path(p["poster_path"]).name, key=p["paper_id"])
                st.markdown("#### 关键信息")
                st.markdown(p.get("key_info") or "暂无")

elif page == "3 综述写作与自动引用":
    st.subheader("📝 调用文献库写综述并自动匹配引用")
    topic = st.text_input("综述主题", value="动力电池安全状态评估与异常检测")
    user_prompt = st.text_area("写作要求", value="请按研究现状、方法分类、局限性和未来趋势组织。", height=120)
    n_results = st.slider("检索文献片段数量", 3, 15, 8)
    if st.button("生成综述草稿", type="primary"):
        with st.spinner("正在检索文献库并生成综述……"):
            result = ReviewAgent().run(topic, user_prompt, n_results=n_results)
        st.markdown("### 综述草稿")
        st.markdown(result["review_text"])
        st.markdown("### 匹配到的文献片段")
        for r in result["retrieved_docs"]:
            meta = r.get("metadata", {})
            st.markdown(f"**[{meta.get('paper_id')}] {meta.get('title')}**")
            st.caption(f"相似距离：{r.get('distance')}")
            st.write(r.get("content")[:800] + "...")

elif page == "4 润色与中英互译":
    st.subheader("🌐 学术润色 / 中英互译")
    task = st.selectbox("任务类型", ["中文学术润色", "中译英", "英译中", "英文论文润色"])
    text = st.text_area("输入文本", height=260)
    if st.button("执行", type="primary", disabled=not text.strip()):
        with st.spinner("正在处理……"):
            out = PolishTranslateAgent().run(text, task)
        st.markdown("### 输出结果")
        st.markdown(out)
