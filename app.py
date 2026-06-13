 % cat ~/Downloads/querymy-main/app.py
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from gemini_helper import ask_gemini, generate_sql, auto_insight
from data_handler import load_file, get_data_summary, detect_anomalies
from sql_handler import load_csv_to_db, run_sql, get_schema
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import json

st.set_page_config(page_title="QueryMy Pro", page_icon="⚡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');
* { font-family: 'Syne', sans-serif !important; }
.stApp { background-color: #020408 !important; background-image: linear-gradient(rgba(0,212,255,0.04) 1px, transparent 1px), linear-gradient(90deg, rgba(0,212,255,0.04) 1px, transparent 1px); background-size: 48px 48px; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #070d14 0%, #050a10 100%) !important; border-right: 1px solid #0f2035 !important; }
section[data-testid="stSidebar"] * { color: #a8c8e8 !important; }
.stChatMessage { background: linear-gradient(135deg, #0b1520, #070d14) !important; border: 1px solid #0f2035 !important; border-radius: 12px !important; margin-bottom: 10px !important; }
.stChatMessage:hover { border-color: rgba(0,212,255,0.25) !important; }
.stButton > button { background: linear-gradient(135deg, #0066ff, #00d4ff) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 600 !important; box-shadow: 0 4px 15px rgba(0,102,255,0.3) !important; }
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 30px rgba(0,102,255,0.5) !important; }
.stFileUploader { background: linear-gradient(135deg, #0b1520, #070d14) !important; border: 1px dashed rgba(0,212,255,0.2) !important; border-radius: 12px !important; }
[data-testid="stFileUploaderDropzoneInput"] + div { display: none !important; }
[data-testid="stFileuploaderDropzone"] button { background: linear-gradient(135deg, #0066ff, #00d4ff) !important; color: white !important; border: none !important; border-radius: 8px !important; padding: 8px 20px !important; font-weight: 600 !important; cursor: pointer !important; }
[data-testid="stFileuploaderDropzone"] button::before { content: "📂 Browse Files" !important; }
[data-testid="stFileploaderDropzone"] button span { display: none !important; }
.stExpander { background: linear-gradient(135deg, #0b1520, #070d14) !important; border: 1px solid #0f2035 !important; border-radius: 12px !important; }
.stDataFrame { background-color: #0b1520 !important; border-radius: 8px !important; border: 1px solid #0f2035 !important; }
.stSuccess { background: linear-gradient(135deg, #052e16, #063a1c) !important; border: 1px solid rgba(0,255,136,0.3) !important; border-radius: 8px !important; }
h1, h2, h3 { color: #e8f4ff !important; }
p, label { color: #a8c8e8 !important; }
.metric-card { background: linear-gradient(135deg, #0b1520, #070d14); border: 1px solid #0f2035; border-radius: 12px; padding: 16px 20px; text-align: center; }
.metric-value { font-size: 1.8rem; font-weight: 800; background: linear-gradient(135deg, #00d4ff, #0066ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.metric-label { font-size: 0.7rem; color: #3a5a78; font-family: monospace; text-transform: uppercase; letter-spacing: 0.1em; margin-top: 4px; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #0f2035; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #00d4ff; }
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }
header { visibility: hidden !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
[data-testid="stFileUploaderDropzone"] span { display: none !important; }
[data-testid="stFileUploaderDropzone"]::before { content: "📂 Click to upload or drag file here"; color: #a8c8e8; font-size: 0.85rem; font-family: monospace; }
[data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="padding:8px 0 24px;border-bottom:1px solid #0f2035;margin-bottom:24px;">
<div style="font-family:monospace;font-size:0.7rem;color:#00d4ff;letter-spacing:0.2em;text-transform:uppercase;margin-bottom:10px;">// AI-Powered Data Intelligence</div>
<div style="font-size:2.8rem;font-weight:800;letter-spacing:-0.04em;line-height:1;background:linear-gradient(135deg,#00d4ff,#0066ff,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:8px;">⚡ QueryMy Pro</div>
<div style="font-size:0.8rem;color:#3a5a78;font-family:monospace;">Ask anything about your data — built by Ananya Gautam</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    # THEME TOGGLE
    if "theme" not in st.session_state:
        st.session_state["theme"] = "dark"
    theme_label = "☀️ Light Mode" if st.session_state["theme"] == "dark" else "🌙 Dark Mode"
    if st.button(theme_label, key="theme_toggle"):
        st.session_state["theme"] = "light" if st.session_state["theme"] == "dark" else "dark"
        st.rerun()

    # DEPLOY BUTTON
    st.markdown("---")
    st.markdown("<div style='font-family:monospace;font-size:0.7rem;color:#00d4ff;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:8px;'>// Deploy</div>", unsafe_allow_html=True)
    st.link_button("🚀 Deploy on Streamlit Cloud", "https://share.streamlit.io", use_container_width=True)
    st.markdown("---")

    st.markdown("<div style='font-family:monospace;font-size:0.7rem;color:#00d4ff;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid #0f2035;'>// Data Source</div>", unsafe_allow_html=True)
    data_source = st.radio("Select source", ["Upload CSV/Excel", "Live Stock Data"], label_visibility="collapsed")
    if data_source == "Upload CSV/Excel":
        uploaded_file = st.file_uploader("Upload file", type=["csv", "xlsx", "xls"])
        if uploaded_file:
            df = load_file(uploaded_file)
            if df is not None:
                st.success(f"✅ {uploaded_file.name}")
                st.markdown(f"<div style='font-family:monospace;font-size:0.75rem;color:#3a5a78;margin:8px 0;'>{df.shape[0]} rows · {df.shape[1]} cols</div>", unsafe_allow_html=True)
                st.dataframe(df.head(5), use_container_width=True)
                st.session_state["df"] = df
                st.session_state["data_summary"] = get_data_summary(df)
                load_csv_to_db(df)
                st.session_state["db_loaded"] = True
                st.session_state.pop("auto_insight", None)
    elif data_source == "Live Stock Data":
        ticker = st.text_input("Stock symbol", value="RELIANCE.NS")
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y"])
        if st.button("⚡ Fetch Live Data"):
            with st.spinner("Fetching..."):
                df = yf.download(ticker, period=period)
                df.reset_index(inplace=True)
                st.success(f"✅ {ticker} loaded")
                st.dataframe(df.tail(5), use_container_width=True)
                st.session_state["df"] = df
                st.session_state["data_summary"] = get_data_summary(df)
                load_csv_to_db(df)
                st.session_state["db_loaded"] = True
                st.session_state.pop("auto_insight", None)

if "df" in st.session_state:
    df = st.session_state["df"]
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    st.markdown("<div style='font-family:monospace;font-size:0.7rem;color:#00d4ff;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:12px;'>// Dataset Overview</div>", unsafe_allow_html=True)
    cols = st.columns(4)
    with cols[0]:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{df.shape[0]:,}</div><div class='metric-label'>Total Rows</div></div>", unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{df.shape[1]}</div><div class='metric-label'>Columns</div></div>", unsafe_allow_html=True)
    with cols[2]:
        if numeric_cols:
            val = f"{df[numeric_cols[0]].sum():,.0f}"
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{val}</div><div class='metric-label'>Total {numeric_cols[0]}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{df.shape[1]}</div><div class='metric-label'>Features</div></div>", unsafe_allow_html=True)
    with cols[3]:
        missing = df.isnull().sum().sum()
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{missing}</div><div class='metric-label'>Missing Values</div></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

if "df" in st.session_state and "auto_insight" not in st.session_state:
    with st.spinner("🤖 AI is analyzing your dataset..."):
        insight = auto_insight(st.session_state["data_summary"])
        st.session_state["auto_insight"] = insight

if "auto_insight" in st.session_state:
    st.markdown("<div style='font-family:monospace;font-size:0.7rem;color:#00d4ff;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:8px;'>// AI Executive Summary</div>", unsafe_allow_html=True)
    insight_html = st.session_state["auto_insight"].replace("\n", "<br>")
    st.markdown(f"<div style='background:linear-gradient(135deg,#0b1520,#070d14);border:1px solid #0f2035;border-left:3px solid #00d4ff;border-radius:12px;padding:20px;margin-bottom:24px;font-size:0.9rem;color:#a8c8e8;line-height:2;'>{insight_html}</div>", unsafe_allow_html=True)

if "df" in st.session_state:
    with st.expander("🔍 Anomaly Detection"):
        anomalies = detect_anomalies(st.session_state["df"])
        st.write(anomalies)
        if st.button("🧠 Explain Anomalies with AI"):
            explanation = ask_gemini("Explain these anomalies in simple business terms", anomalies)
            st.write(explanation)

if "df" in st.session_state:
    with st.expander("🗄️ Text to SQL — Ask in Plain English"):
        sql_question = st.text_input("Ask a SQL question:", placeholder="e.g. Show top 5 categories by total sales")
        if st.button("⚡ Run SQL Query"):
            with st.spinner("Generating SQL..."):
                schema = get_schema()
                sql = generate_sql(sql_question, schema)
                st.markdown(f"```sql\n{sql}\n```")
                result, error = run_sql(sql)
                if error:
                    st.error(f"Error: {error}")
                else:
                    st.dataframe(result, use_container_width=True)
                    st.caption(f"⚡ SQL generated and executed in {round(time.time() - start, 2)}s")

if "df" in st.session_state:
    if st.button("📄 Generate PDF Report"):
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 750, "QueryMy Pro — Data Analysis Report")
        c.setFont("Helvetica", 12)
        c.drawString(50, 720, f"Rows: {st.session_state['df'].shape[0]} | Columns: {st.session_state['df'].shape[1]}")
        summary_lines = st.session_state["data_summary"].split("\n")
        y = 690
        for line in summary_lines[:15]:
            c.drawString(50, y, line[:90])
            y -= 18
        c.save()
        buffer.seek(0)
        st.download_button("📥 Download Report", buffer, file_name="querymy_report.pdf")

if "df" in st.session_state:
    st.markdown("<div style='font-family:monospace;font-size:0.7rem;color:#00d4ff;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:8px;margin-top:16px;'>// Quick Questions</div>", unsafe_allow_html=True)
    if st.button("🎲 Surprise Me — Generate 3 Questions"):
        with st.spinner("Generating questions..."):
            data_context = st.session_state.get("data_summary", "")
            suggestion_prompt = f"""Based on this dataset, generate exactly 3 interesting business questions a manager would ask.
Dataset: {data_context}
Return ONLY 3 questions, numbered 1. 2. 3. Nothing else."""
            suggestions = ask_gemini(suggestion_prompt, data_context)
            st.session_state["suggestions"] = suggestions
    if "suggestions" in st.session_state:
        st.markdown(f"<div style='background:#0b1520;border:1px solid #0f2035;border-radius:12px;padding:16px;margin-bottom:16px;font-size:0.9rem;color:#a8c8e8;line-height:1.8;'>{st.session_state['suggestions']}</div>", unsafe_allow_html=True)


if "df" in st.session_state:
    st.markdown("<div style='font-family:monospace;font-size:0.7rem;color:#00d4ff;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:8px;margin-top:24px;'>// Self-Looping AI Agent</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.85rem;color:#3a5a78;margin-bottom:12px;font-family:monospace;'>AI investigates your data automatically — asks and answers 7 questions on its own</div>", unsafe_allow_html=True)
    if st.button("🤖 Run Deep Dive Agent — 7 Auto Loops"):
        from gemini_helper import self_loop_agent
        loop_results = []
        progress = st.progress(0)
        status = st.empty()
        for i in range(7):
            status.markdown(f"<div style='color:#00d4ff;font-family:monospace;font-size:0.8rem;'>🔄 Loop {i+1}/7 — AI is investigating...</div>", unsafe_allow_html=True)
            progress.progress((i+1)/7)
            if i == 0:
                from gemini_helper import self_loop_agent
                results = self_loop_agent(st.session_state["data_summary"], loops=7)
                loop_results = results
                break
        progress.empty()
        status.empty()
        st.session_state["loop_results"] = loop_results

    if "loop_results" in st.session_state:
        for i, item in enumerate(st.session_state["loop_results"]):
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#0b1520,#070d14);border:1px solid #0f2035;border-left:3px solid #00d4ff;border-radius:12px;padding:16px 20px;margin-bottom:12px;'>
                <div style='font-family:monospace;font-size:0.7rem;color:#00d4ff;letter-spacing:0.1em;margin-bottom:8px;'>LOOP {i+1} — QUESTION</div>
                <div style='color:#e8f4ff;font-size:0.95rem;font-weight:600;margin-bottom:10px;'>{item["question"]}</div>
                <div style='font-family:monospace;font-size:0.7rem;color:#00ff88;letter-spacing:0.1em;margin-bottom:6px;'>→ FINDING</div>
                <div style='color:#a8c8e8;font-size:0.88rem;line-height:1.7;'>{item["answer"]}</div>
            </div>""", unsafe_allow_html=True)


if "df" in st.session_state:
    with st.expander("🔎 Natural Language Filter — Describe what you want to see"):
        filter_question = st.text_input("Filter your data:", placeholder="e.g. show only orders above 500 from New York")
        if st.button("⚡ Apply Filter"):
            with st.spinner("Filtering..."):
                import time
                start = time.time()
                from gemini_helper import natural_language_filter
                from sql_handler import get_schema
                schema = get_schema()
                filter_code = natural_language_filter(filter_question, schema, st.session_state["data_summary"])
                try:
                    filtered_df = eval(filter_code, {"df": st.session_state["df"]})
                    elapsed = round(time.time() - start, 2)
                    st.markdown(f"<div style='font-family:monospace;font-size:0.75rem;color:#00ff88;margin-bottom:8px;'>✓ Filter applied — {len(filtered_df)} rows matched</div>", unsafe_allow_html=True)
                    st.code(filter_code, language="python")
                    st.dataframe(filtered_df, use_container_width=True)
                    st.caption(f"⚡ Filter applied in {elapsed}s")
                except Exception as e:
                    st.error(f"Could not apply filter — try rephrasing: {e}")

if "df" in st.session_state:
    with st.expander("📈 Predictive Analysis — AI forecasts what happens next"):
        if st.button("🔮 Generate Prediction"):
            with st.spinner("Analyzing trends and predicting..."):
                import time
                start = time.time()
                from gemini_helper import predict_trend
                prediction = predict_trend(st.session_state["data_summary"])
                elapsed = round(time.time() - start, 2)
                prediction_html = prediction.replace("\n", "<br>")
                st.markdown(f"<div style='background:linear-gradient(135deg,#0b1520,#070d14);border:1px solid #0f2035;border-left:3px solid #00ff88;border-radius:12px;padding:20px;margin-top:8px;font-size:0.9rem;color:#a8c8e8;line-height:2;'>{prediction_html}</div>", unsafe_allow_html=True)
                st.caption(f"⚡ Prediction generated in {elapsed}s")



# FEATURE 1: DATA CLEANING ASSISTANT
if "df" in st.session_state:
    with st.expander("🧹 Data Cleaning Assistant — AI detects and fixes dirty data"):
        if st.button("Scan for Issues", key="scan_issues"):
            with st.spinner("Scanning your data..."):
                df_info = str(st.session_state["df"].dtypes) + "\n\nMissing:\n" + str(st.session_state["df"].isnull().sum()) + "\n\nDuplicates: " + str(st.session_state["df"].duplicated().sum())
                from gemini_helper import clean_data_suggestions
                raw = clean_data_suggestions(st.session_state["data_summary"], df_info)
                try:
                    s = raw.find("[")
                    e = raw.rfind("]") + 1
                    issues = json.loads(raw[s:e])
                    st.session_state["clean_issues"] = issues
                except:
                    st.error("Could not parse issues. Try again.")
        if "clean_issues" in st.session_state:
            issues = st.session_state["clean_issues"]
            st.success(f"Found {len(issues)} issue(s)")
            for issue in issues:
                sev = issue.get("severity", "Medium")
                color = "red" if sev == "High" else "orange"
                st.markdown(f":{color}[**{sev}**] — {issue.get('issue','')} | Fix: `{issue.get('fix','')}`")
            if st.button("Auto-Fix All Issues", key="autofix"):
                df_clean = st.session_state["df"].copy()
                fixed = []
                for issue in issues:
                    col = issue.get("column")
                    fix = issue.get("fix")
                    try:
                        if fix == "drop_duplicates":
                            df_clean = df_clean.drop_duplicates()
                            fixed.append("Dropped duplicates")
                        elif fix == "fill_mean" and col in df_clean.columns:
                            df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
                            fixed.append(f"Filled {col} with mean")
                        elif fix == "fill_median" and col in df_clean.columns:
                            df_clean[col] = df_clean[col].fillna(df_clean[col].median())
                            fixed.append(f"Filled {col} with median")
                        elif fix == "fill_zero" and col in df_clean.columns:
                            df_clean[col] = df_clean[col].fillna(0)
                            fixed.append(f"Filled {col} with 0")
                        elif fix == "fill_unknown" and col in df_clean.columns:
                            df_clean[col] = df_clean[col].fillna("Unknown")
                            fixed.append(f"Filled {col} with Unknown")
                        elif fix == "drop_negative" and col in df_clean.columns:
                            df_clean = df_clean[df_clean[col] >= 0]
                            fixed.append(f"Dropped negative {col}")
                        elif fix == "strip_whitespace":
                            for c in df_clean.select_dtypes(include="object").columns:
                                df_clean[c] = df_clean[c].str.strip()
                            fixed.append("Stripped whitespace")
                    except:
                        pass
                st.session_state["df"] = df_clean
                st.session_state["data_summary"] = get_data_summary(df_clean)
                load_csv_to_db(df_clean)
                st.success(f"Cleaned! {df_clean.shape[0]} rows remaining. Fixed: {', '.join(fixed)}")
                st.session_state.pop("clean_issues", None)

# FEATURE 2: AUTO DASHBOARD
if "df" in st.session_state:
    with st.expander("📊 Auto Dashboard — AI builds 4 charts instantly"):
        if st.button("Generate Full Dashboard", key="gen_dashboard"):
            with st.spinner("Building your dashboard..."):
                from gemini_helper import generate_dashboard_config
                cols_list = list(st.session_state["df"].columns)
                raw = generate_dashboard_config(st.session_state["data_summary"], cols_list)
                try:
                    s = raw.find("[")
                    e = raw.rfind("]") + 1
                    charts = json.loads(raw[s:e])
                    st.session_state["dashboard_charts"] = charts
                except:
                    st.error("Could not generate dashboard. Try again.")
        if "dashboard_charts" in st.session_state:
            col1, col2 = st.columns(2)
            cols_cycle = [col1, col2, col1, col2]
            df = st.session_state["df"]
            for i, chart in enumerate(st.session_state["dashboard_charts"][:4]):
                ct = chart.get("chart_type", "bar")
                x = chart.get("x_col")
                y = chart.get("y_col")
                title = chart.get("title", f"Chart {i+1}")
                try:
                    if x not in df.columns or y not in df.columns:
                        continue
                    if ct == "bar":
                        fig = px.bar(df, x=x, y=y, title=title, color_discrete_sequence=["#00d4ff"])
                    elif ct == "line":
                        fig = px.line(df, x=x, y=y, title=title, color_discrete_sequence=["#00d4ff"])
                    elif ct == "pie":
                        fig = px.pie(df, names=x, values=y, title=title)
                    else:
                        fig = px.scatter(df, x=x, y=y, title=title, color_discrete_sequence=["#00d4ff"])
                    fig.update_layout(paper_bgcolor="#0b1520", plot_bgcolor="#070d14", font_color="#e8f4ff", title_font_color="#00d4ff", xaxis=dict(gridcolor="#0f2035"), yaxis=dict(gridcolor="#0f2035"), margin=dict(t=40, b=20))
                    with cols_cycle[i]:
                        st.plotly_chart(fig, use_container_width=True)
                except:
                    pass

# FEATURE 3: EXPORT TO EXCEL
if "df" in st.session_state:
    with st.expander("📥 Export to Excel — Download clean formatted data"):
        export_cols = st.multiselect("Select columns (leave empty for all)", options=list(st.session_state["df"].columns), key="export_cols")
        if st.button("Download as Excel", key="dl_excel"):
            df_export = st.session_state["df"][export_cols] if export_cols else st.session_state["df"]
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_export.to_excel(writer, index=False, sheet_name="QueryMy Data")
                worksheet = writer.sheets["QueryMy Data"]
                for col in worksheet.columns:
                    max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col)
                    worksheet.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)
            buffer.seek(0)
            st.download_button("Click to Download", buffer, file_name="querymy_export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            st.success(f"Ready! {len(df_export)} rows, {len(df_export.columns)} columns")


if "messages" not in st.session_state:
    st.session_state["messages"] = []

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        if msg.get("chart") is not None:
            st.plotly_chart(msg["chart"], use_container_width=True)
        else:
            st.write(msg["content"])

if prompt := st.chat_input("Ask anything... try 'show me a bar chart of Sales by Category'"):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            data_context = st.session_state.get("data_summary", "No data loaded yet.")
            chart_keywords = ["chart", "plot", "graph", "visualize", "show me", "bar", "line", "pie"]
            wants_chart = any(k in prompt.lower() for k in chart_keywords)

            if wants_chart and "df" in st.session_state:
                chart_prompt = f"""You are a data analyst. Based on this dataset and question, return ONLY a JSON object.
Dataset info: {data_context}
Question: {prompt}
Return ONLY this JSON, nothing else:
{{"chart_type": "bar" or "line" or "pie", "title": "chart title", "x_col": "exact column name", "y_col": "exact column name"}}"""
                raw = ask_gemini(chart_prompt, data_context)
                try:
                    start = raw.find('{')
                    end = raw.rfind('}') + 1
                    config = json.loads(raw[start:end])
                    df = st.session_state["df"]
                    ct = config.get("chart_type", "bar")
                    x = config.get("x_col")
                    y = config.get("y_col")
                    title = config.get("title", "Chart")
                    if ct == "bar":
                        fig = px.bar(df, x=x, y=y, title=title, color_discrete_sequence=["#00d4ff"])
                    elif ct == "line":
                        fig = px.line(df, x=x, y=y, title=title, color_discrete_sequence=["#00d4ff"])
                    elif ct == "pie":
                        fig = px.pie(df, names=x, values=y, title=title)
                    fig.update_layout(paper_bgcolor="#0b1520", plot_bgcolor="#070d14", font_color="#e8f4ff", title_font_color="#00d4ff", xaxis=dict(gridcolor="#0f2035"), yaxis=dict(gridcolor="#0f2035"))
                    st.plotly_chart(fig, use_container_width=True)
                    st.session_state["messages"].append({"role": "assistant", "content": "", "chart": fig})
                except Exception as e:
                    import time
                    start = time.time()
                    response = ask_gemini(prompt, data_context)
                    elapsed = round(time.time() - start, 2)
                    st.write(response)
                    st.caption(f"⚡ Response generated in {elapsed}s")
                    st.session_state["messages"].append({"role": "assistant", "content": response, "elapsed": elapsed})
            else:
                import time
                start = time.time()
                response = ask_gemini(prompt, data_context)
                elapsed = round(time.time() - start, 2)
                st.write(response)
                st.caption(f"⚡ Response generated in {elapsed}s")
                st.session_state["messages"].append({"role": "assistant", "content": response, "elapsed": elapsed})
