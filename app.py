"""
app.py — ממשק Streamlit לקיצור שולחן ערוך (source-first).
הרצה:  .venv\Scripts\streamlit run app.py

עטיפה דקה מעל הליבה הקיימת: שליפה (semantic_e5_combined) + גנרציה אופציונלית.
המקור (הסעיף) הוא הגיבור; תשובה מנוסחת היא משנית ומתויגת בבירור — אינה פסק.
"""
import streamlit as st

from retrievers import get_retriever
from step_04_rag_answer import build_context, generate, RETRIEVER
from config import GEN_BACKEND

st.set_page_config(page_title="קיצור שולחן ערוך — חיפוש", page_icon="📖", layout="wide")

st.markdown("""
<style>
  .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] { direction: rtl; }
  .stTextInput input, textarea { direction: rtl; text-align: right; }
  h1, h2, h3, p, label, .stMarkdown { text-align: right; }
  .seif { background:#1a1f35; border:1px solid #2c3354; border-radius:12px;
          padding:14px 18px; margin-bottom:12px; }
  .seif .ref { font-weight:800; color:#6ea8fe; margin-bottom:8px; display:block; }
  .seif .txt { font-size:17px; line-height:1.8; color:#e6e9f5; }
  .ans { background:#15301f; border:1px solid #2e6b46; border-radius:12px; padding:16px 18px;
         color:#eafaf0; font-size:18px; line-height:1.7; }
  .ans b { color:#7CFFB0; }
  .ans .disc { color:#f4c542; font-size:13px; margin-top:10px; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="טוען מודל שליפה...")
def load_retriever():
    r = get_retriever(RETRIEVER)
    r._load()          # טעינה חד-פעמית (cache)
    return r


# ─── סרגל צד ───
with st.sidebar:
    st.header("הגדרות")
    top_k = st.slider("כמה סעיפים לשלוף", 1, 10, 3)
    gen_on = st.checkbox("נסח תשובה (איטי — אינו פסק)", value=False)
    backend = st.selectbox("מנוע גנרציה", ["ollama", "openai"],
                           index=0 if GEN_BACKEND == "ollama" else 1)
    ctx_mode = st.selectbox("הקשר למנוע", ["text", "summary", "both"], index=0,
                            help="טקסט מקורי / סיכום מודרני / שניהם")

st.title("📖 קיצור שולחן ערוך — חיפוש הלכתי")
st.caption("הקלד שאלה בעברית. המערכת שולפת את הסעיפים הרלוונטיים מהמקור.")

query = st.text_input("השאלה שלך", placeholder="לדוגמה: האם מותר לטלטל מוקצה בשבת?")

if query:
    retriever = load_retriever()
    with st.spinner("שולף סעיפים..."):
        chunks = retriever.retrieve(query, top_k=top_k)

    if gen_on:
        with st.spinner("מנסח תשובה... (~40 שניות)"):
            try:
                ans = generate(query, build_context(chunks, ctx_mode), backend, None)
                st.success(f"**ניסוח תשובה:**\n\n{ans}")
                st.caption("⚠️ ניסוח אוטומטי — אינו פסק הלכה. עיין במקור והתייעץ עם רב.")
            except Exception as e:
                st.error(f"גנרציה נכשלה: {e}")

    st.subheader("הסעיפים שנשלפו")
    for c in chunks:
        st.markdown(
            f"<div class='seif'><span class='ref'>סימן {c['siman_parent']} · "
            f"סעיף {c['seif']}  (score {c['score']:.3f})</span>"
            f"<span class='txt'>{c['text']}</span></div>",
            unsafe_allow_html=True)
