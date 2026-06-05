import streamlit as st
from google import genai
import PyPDF2
from datetime import datetime
import os
import re
from fpdf import FPDF

# --- 1. 基本設定 ---
st.set_page_config(page_title="TruESG 永續智審平台", page_icon="🌿", layout="wide")

# 🌟 UI 優化：隱藏預設選單與底部浮水印 (提升專業感)
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 🌟 安全機制：從 Streamlit 雲端保險箱讀取金鑰
try:
    SYSTEM_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    SYSTEM_API_KEY = None

# --- 2. 專業感左側邊欄 (Sidebar) ---
with st.sidebar:
    st.title("⚙️ 系統狀態與設定")
    
    if SYSTEM_API_KEY:
        st.success("🟢 狀態：系統已安全授權\n\n引擎：Gemini 2.5 Flash")
    else:
        st.error("🔴 狀態：伺服器未設定安全金鑰")
        
    st.markdown("---")
    st.markdown("### 📋 內建審核標準")
    st.markdown("""
    - **GRI** 永續性報導準則 (核心基準)
    - **SDGs** 聯合國永續發展目標 (亮點)
    - **SA8000** 社會責任標準 (亮點)
    - **反漂綠 (Anti-Greenwashing)** 檢核
    """)
    st.markdown("---")
    st.caption("© 2026 TruESG 智能審核系統")

# --- 3. 主畫面標題與載入 Prompt ---
st.title("🌿 TruESG 永續智審平台")
st.markdown("交由第三方 AI 智能查核：一鍵上傳 ESG 文件，即刻獲取最嚴格的防漂綠與合規性分析。")

@st.cache_data
def load_system_prompt():
    try:
        with open("system_prompt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "錯誤：找不到 system_prompt！"

system_prompt = load_system_prompt()

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text()
    return text

def clean_text_for_pdf(raw_text):
    # 1. 移除 Markdown 符號
    text = re.sub(r'[*#$_~`]', '', raw_text)
    # 2. 統一條列式符號
    text = re.sub(r'^[\-\+]\s+', '・ ', text, flags=re.MULTILINE)
    
    # 🌟 終極排版修復：中英文自動加空白，防止 PDF 引擎切斷單字
    text = re.sub(r'([\u4e00-\u9fa5])([a-zA-Z0-9])', r'\1 \2', text)
    text = re.sub(r'([a-zA-Z0-9])([\u4e00-\u9fa5])', r'\1 \2', text)
    
    # 3. 避免過多空白與空行
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # 4. 移除換行時孤立的標點符號
    text = re.sub(r'^\s*[\.\,\;\:\'\"\]\[\}\{\(\)]\s*$', '', text, flags=re.MULTILINE)
    
    return text.strip()

def generate_pdf_bytes(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(10, 10, 10)
    
    font_path = "NotoSansTC-Regular.ttf"  
    
    if os.path.exists(font_path):
        pdf.add_font("ChineseFont", "", font_path)
        base_font = "ChineseFont"
    else:
        base_font = "Helvetica"
    
    pdf.set_font(base_font, size=16)
    pdf.set_text_color(44, 62, 80)
    pdf.cell(0, 12, "TruESG 專業審核報告書", ln=True, align='C')
    pdf.ln(6)
    
    pdf.set_font(base_font, size=11)
    pdf.set_text_color(0, 0, 0)
    
    clean_text = clean_text_for_pdf(text_content)
    lines = clean_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue
            
        pdf.set_x(10)
            
        if re.match(r'^(一|二|三|四|五|六|七|八|九|十)、', line):
            pdf.ln(3)
            pdf.set_font(base_font, size=12)
            pdf.set_text_color(255, 255, 255)
            pdf.set_fill_color(44, 62, 80)
            pdf.multi_cell(0, 9, f" {line}", fill=True, align='L')
            pdf.set_font(base_font, size=11)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)
            
        elif "評分：" in line or "分 / 5分" in line or "綜合結論：" in line:
            pdf.ln(1)
            if "1分" in line or "不及格" in line or "不合格" in line:
                pdf.set_fill_color(254, 237, 238)
                pdf.set_text_color(192, 0, 0)
            elif "2分" in line or "需重大改善" in line:
                pdf.set_fill_color(255, 248, 230)
                pdf.set_text_color(212, 143, 56)
            else:
                pdf.set_fill_color(240, 248, 240)
                pdf.set_text_color(56, 87, 35)
            pdf.multi_cell(0, 8, f" {line}", fill=True, align='L')
            pdf.set_text_color(0, 0, 0)
            pdf.ln(1)
            
        elif line.startswith("優點"):
            pdf.set_text_color(46, 117, 89)
            pdf.multi_cell(0, 7, line, align='L')
            pdf.set_text_color(0, 0, 0)
            
        elif line.startswith("缺失"):
            pdf.set_text_color(170, 57, 57)
            pdf.multi_cell(0, 7, line, align='L')
            pdf.set_text_color(0, 0, 0)
            
        elif "嚴重不足" in line or "不合格" in line:
            pdf.set_text_color(170, 57, 57)
            pdf.multi_cell(0, 7, line, align='L')
            pdf.set_text_color(0, 0, 0)
            
        elif line.startswith("・") or line.startswith("·"):
            pdf.set_x(16)
            pdf.multi_cell(0, 7, line, align='L')
        else:
            pdf.multi_cell(0, 7, line, align='L')
            
    return bytes(pdf.output())

# --- 4. 檔案上傳區與首頁引導 ---
st.markdown("### 📂 第一步：上傳文件")
uploaded_file = st.file_uploader("支援格式：PDF (建議檔案大小不超過 30MB)", type="pdf")

if not uploaded_file and 'audit_report' not in st.session_state:
    st.markdown("---")
    st.markdown("#### ✨ 歡迎使用 TruESG 智能評測系統")
    st.write("只需三個步驟，即可為您的企業永續報告進行深度體檢：")
    
    step1, step2, step3 = st.columns(3)
    with step1:
        st.info("📄 **1. 上傳報告**\n\n支援 PDF 格式，系統將自動萃取企劃書或企業 CSR/ESG 報告內文。")
    with step2:
        st.info("🧠 **2. 智能掃描**\n\n對標 GRI、SDGs 等國際永續準則與框架，進行深度的防漂綠（Anti-Greenwashing）檢核。")
    with step3:
        st.info("📊 **3. 獲取評級**\n\n產出具備總結摘要、視覺化燈號與具體改善建議的企業級專業 PDF 報告。")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    start_btn = st.button("🚀 開始智能嚴格審核", use_container_width=True, type="primary")

# --- 5. 執行審核與進度顯示 ---
if start_btn:
    if not SYSTEM_API_KEY:
        st.error("⚠️ 系統尚未設定安全金鑰，無法執行審核。請聯繫網站管理員。")
    elif not uploaded_file:
        st.warning("⚠️ 請先上傳一份 PDF 企劃書。")
    elif "錯誤" in system_prompt:
        st.error(system_prompt)
    else:
        with st.status("🔍 系統啟動審核程序...", expanded=True) as status:
            try:
                st.write("📄 正在萃取 PDF 內容...")
                proposal_text = extract_text_from_pdf(uploaded_file)
                st.session_state['raw_proposal_text'] = proposal_text
                
                st.write("🌐 正在連線至 AI 評測引擎...")
                client = genai.Client(api_key=SYSTEM_API_KEY)
                
                # 🌟 新版：配合 GRI 主 + SA8000/SDG 輔 的輸出結構
                final_prompt = f"""
                你是一個嚴格的第三方 ESG 審核系統。請完全依照以下【評分規則書】的邏輯，來審核使用者提交的【企劃書內容】。

                【⚠️ 重要排版與輸出結構要求 - 請嚴格遵守】：
                1. 報告的「最開頭第一段」必須是【一、 總體評估摘要與評分】，請直接排在最前面。
                   此區塊內必須清楚包含以下項目：
                   ・綜合結論：（請用一到兩句話對整份計畫書進行定調短評）
                   ・環境（E）評分：X分 / 5分
                   ・社會（S）評分：X分 / 5分（若因核心底線觸發不合格，請註明直接判定不及格）
                   ・治理（G）評分：X分 / 5分
                2. 在【一、 總體評估摘要與評分】完全結束後，才可以往下撰寫後續的詳細章節，結構依序為：
                   ・二、 GRI 核心基準審查 (基礎合規檢視，分別列出環境、社會、治理的優點與缺失)
                   ・三、 進階亮點與國際對齊 (SA8000 & SDGs 加分項說明)
                   ・四、 具體改善策略與下一步建議
                3. 絕對禁止使用任何 Markdown 語法。
                4. 絕對禁止使用 Emoji 或特殊圖形。
                5. 請完全使用「純文字」與「全形標點符號」來撰寫報告。
                6. 條列式說明請使用全形的「・」或中文數字「（一）、1.」開頭，段落之間請保持乾淨俐落。

                【評分規則書】：
                {system_prompt}

                ---
                【企劃書內容】：
                {proposal_text}
                """
                
                st.write("🧠 AI 正在進行防漂綠與交叉比對分析 (約需 10-20 秒)...")
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=final_prompt
                )
                
                status.update(label="✅ 審核完成！", state="complete", expanded=False)
                
                st.session_state['audit_report'] = response.text
                st.session_state['audit_time'] = datetime.now().strftime("%Y%m%d_%H%M")
                st.toast("✅ 報告生成完畢！請向下捲動查看結果。")

            except Exception as e:
                status.update(label="❌ 發生錯誤", state="error", expanded=True)
                st.error(f"連線或分析時發生錯誤：{e}")

# --- 6. 報告展示區與 PDF 下載 ---
if 'audit_report' in st.session_state:
    st.markdown("---")
    
    # 🌟 頂部：標題與下載按鈕
    title_col, btn_col = st.columns([3, 1])
    with title_col:
        st.markdown("### 📋 專業審核報告書")
    with btn_col:
        pdf_bytes = generate_pdf_bytes(st.session_state['audit_report'])
        file_name = f"ESG_Review_Report_{st.session_state['audit_time']}.pdf"
        st.download_button(
            label="⬇️ 下載 PDF 審核報告",
            data=pdf_bytes,
            file_name=file_name,
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
        
    # 🌟 儀表板：自動抓取並顯示大數字分數
    report_text = st.session_state['audit_report']
    e_score = re.search(r'環境.*?(\d+)分', report_text)
    s_score = re.search(r'社會.*?(\d+)分', report_text)
    g_score = re.search(r'治理.*?(\d+)分', report_text)
    
    e_val = f"{e_score.group(1)} / 5" if e_score else "需檢視"
    s_val = f"{s_score.group(1)} / 5" if s_score else "不及格 🚨"
    g_val = f"{g_score.group(1)} / 5" if g_score else "需檢視"

    m1, m2, m3 = st.columns(3)
    m1.metric(label="🌍 環境 (E)", value=e_val)
    m2.metric(label="🤝 社會 (S)", value=s_val)
    m3.metric(label="🏛️ 治理 (G)", value=g_val)
    
    st.divider()
    
    # 🌟 報告內文渲染：帶外框且支援上色
    with st.container(border=True):
        lines = st.session_state['audit_report'].split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if re.match(r'^(一|二|三|四|五|六|七|八|九|十)、', line):
                st.markdown(f"#### 📘 {line}")
            elif "評分：" in line or "分 / 5分" in line or "綜合結論：" in line:
                if "1分" in line or "不及格" in line or "不合格" in line:
                    st.error(line)
                elif "2分" in line or "需重大改善" in line:
                    st.warning(line)
                else:
                    st.success(line)
            elif line.startswith("優點"):
                st.markdown(f"🍏 <span style='color:#2e7559; font-weight:bold;'>{line}</span>", unsafe_allow_html=True)
            elif line.startswith("缺失"):
                st.markdown(f"🍎 <span style='color:#aa3939; font-weight:bold;'>{line}</span>", unsafe_allow_html=True)
            elif "嚴重不足" in line or "不合格" in line:
                st.markdown(f"<span style='color:#aa3939; font-weight:bold;'>{line}</span>", unsafe_allow_html=True)
            elif line.startswith("・") or line.startswith("·"):
                st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{line}")
            else:
                st.write(line)