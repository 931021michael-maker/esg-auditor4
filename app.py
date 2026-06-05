import streamlit as st
from google import genai
import PyPDF2
from datetime import datetime
import os
import re
from fpdf import FPDF

# --- 1. 基本設定與網頁配置 ---
st.set_page_config(
    page_title="TruESG 永續智審平台", 
    page_icon="🌿", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🌟 UI 優化：注入現代化 CSS 與隱藏預設元素
st.markdown("""
<style>
    /* 引入 Google 現代字體 */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans TC', sans-serif !important;
    }
    
    /* 隱藏預設選單與浮水印 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 優化按鈕樣式 */
    .stButton>button {
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(46, 117, 89, 0.2);
    }

    /* 優化 Tabs 標籤頁樣式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0px 0px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-size: 16px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- 自訂 UI 元件函數 ---
def render_metric_card(title, value, icon, color, bg_color="#ffffff"):
    """渲染具有專業感的資料卡片"""
    st.markdown(f"""
    <div style="background-color: {bg_color}; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.04); border-left: 6px solid {color}; height: 100%;">
        <p style="margin:0; color: #666; font-size: 15px; font-weight: 600; display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 18px;">{icon}</span> {title}
        </p>
        <p style="margin:0; color: #2c3e50; font-size: 32px; font-weight: 800; padding-top: 12px; letter-spacing: -0.5px;">{value}</p>
    </div>
    """, unsafe_allow_html=True)

# 🌟 安全機制：讀取金鑰
try:
    SYSTEM_API_KEY = st.secrets.get("GEMINI_API_KEY", None)
except:
    SYSTEM_API_KEY = None

# --- 2. 專業感左側邊欄 (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8042/8042125.png", width=60) # 替換為您的 Logo
    st.title("⚙️ 系統核心狀態")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if SYSTEM_API_KEY:
        st.success("🟢 **安全連線已建立**\n\n引擎：Gemini 2.5 Flash")
    else:
        st.error("🔴 **未授權**\n\n請於系統環境變數設定金鑰")
        
    st.markdown("---")
    st.markdown("### 📋 內建查核引擎標準")
    st.info("""
    **核心對標框架：**
    - 🌿 **GRI** 永續性報導準則
    - 🌍 **SDGs** 聯合國永續發展目標
    - 🤝 **SA8000** 社會責任標準
    - 🛡️ **Anti-Greenwashing** 反漂綠檢核
    """)
    
    st.markdown("<div style='margin-top: 100px;'></div>", unsafe_allow_html=True)
    st.caption("© 2026 TruESG 智能審核系統 V2.0")

# --- 後台邏輯函數 ---
@st.cache_data(show_spinner=False)
def load_system_prompt():
    try:
        with open("system_prompt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "系統提示：請確保根目錄下有 system_prompt 檔案。"

system_prompt = load_system_prompt()

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = "".join([page.extract_text() or "" for page in pdf_reader.pages])
    return text

def clean_text_for_pdf(raw_text):
    text = re.sub(r'[*#$_~`]', '', raw_text)
    text = re.sub(r'^[\-\+]\s+', '・ ', text, flags=re.MULTILINE)
    text = re.sub(r'([\u4e00-\u9fa5])([a-zA-Z0-9])', r'\1 \2', text)
    text = re.sub(r'([a-zA-Z0-9])([\u4e00-\u9fa5])', r'\1 \2', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'^\s*[\.\,\;\:\'\"\]\[\}\{\(\)]\s*$', '', text, flags=re.MULTILINE)
    return text.strip()

def generate_pdf_bytes(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    
    font_path = "NotoSansTC-Regular.ttf"  
    if os.path.exists(font_path):
        pdf.add_font("ChineseFont", "", font_path)
        base_font = "ChineseFont"
    else:
        base_font = "Helvetica"
    
    # PDF Header
    pdf.set_font(base_font, size=20)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0
