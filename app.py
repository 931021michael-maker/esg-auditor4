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
    - 🌿 **GRI** 永續性報導準則(必要)
    - 🌍 **SDGs** 聯合國永續發展目標(加分項)
    - 🤝 **SA8000** 社會責任標準(加分項)
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
    pdf.cell(0, 15, "TruESG 智能審核報告書", ln=True, align='C')
    pdf.set_draw_color(46, 117, 89)
    pdf.line(15, 30, 195, 30)
    pdf.ln(10)
    
    pdf.set_font(base_font, size=11)
    pdf.set_text_color(0, 0, 0)
    
    clean_text = clean_text_for_pdf(text_content)
    lines = clean_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(4)
            continue
            
        pdf.set_x(15)
            
        if re.match(r'^(一|二|三|四|五|六|七|八|九|十)、', line):
            pdf.ln(5)
            pdf.set_font(base_font, size=13)
            pdf.set_text_color(255, 255, 255)
            pdf.set_fill_color(44, 62, 80)
            pdf.multi_cell(0, 10, f"  {line}", fill=True, align='L')
            pdf.set_font(base_font, size=11)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(3)
            
        elif "評分：" in line or "分 / 5分" in line or "綜合結論：" in line:
            pdf.ln(2)
            if "1分" in line or "不及格" in line or "不合格" in line:
                pdf.set_fill_color(254, 237, 238)
                pdf.set_text_color(192, 0, 0)
            elif "2分" in line or "需重大改善" in line:
                pdf.set_fill_color(255, 248, 230)
                pdf.set_text_color(212, 143, 56)
            else:
                pdf.set_fill_color(240, 248, 240)
                pdf.set_text_color(46, 117, 89)
            pdf.multi_cell(0, 9, f" {line}", fill=True, align='L')
            pdf.set_text_color(0, 0, 0)
            pdf.ln(2)
            
        elif line.startswith("優點"):
            pdf.set_text_color(46, 117, 89)
            pdf.multi_cell(0, 7, line, align='L')
            pdf.set_text_color(0, 0, 0)
            
        elif line.startswith("缺失") or "嚴重不足" in line or "不合格" in line:
            pdf.set_text_color(192, 57, 43)
            pdf.multi_cell(0, 7, line, align='L')
            pdf.set_text_color(0, 0, 0)
            
        elif line.startswith("・") or line.startswith("·"):
            pdf.set_x(20)
            pdf.multi_cell(0, 7, line, align='L')
        else:
            pdf.multi_cell(0, 7, line, align='L')
            
    return bytes(pdf.output())

# --- 3. 主畫面標題與 Header ---
st.markdown("""
    <div style="padding: 2rem 0 1.5rem 0;">
        <h1 style="color: #1E3A8A; font-size: 2.8rem; font-weight: 800; margin-bottom: 0.5rem;">🌿 TruESG 永續智審平台</h1>
        <p style="font-size: 1.2rem; color: #4B5563; max-width: 800px;">
            交由第三方 AI 智能查核：一鍵上傳永續報告書，即刻獲取最嚴格的防漂綠與合規性分析。
        </p>
    </div>
""", unsafe_allow_html=True)

# --- 4. 檔案上傳區與首頁引導 ---
upload_col, guide_col = st.columns([1.2, 1], gap="large")

with upload_col:
    st.markdown("### 📂 啟動審核程序")
    with st.container(border=True):
        uploaded_file = st.file_uploader("上傳您的永續報告書 (支援 PDF，建議上限 30MB)", type="pdf")
        
        st.markdown("<br>", unsafe_allow_html=True)
        start_btn = st.button("🚀 開始進行智能嚴格審核", use_container_width=True, type="primary")

with guide_col:
    if not uploaded_file and 'audit_report' not in st.session_state:
        st.markdown("### ✨ 為什麼選擇 TruESG？")
        st.markdown("""
        <div style="padding: 15px; border-left: 4px solid #3B82F6; background-color: #EFF6FF; border-radius: 4px; margin-bottom: 12px;">
            <strong style="color: #1D4ED8;">🧠 深度智能掃描</strong><br>
            <span style="color: #475569; font-size: 0.95rem;">對標 GRI、SDGs 等國際永續準則，嚴格檢視各項指標聲明。</span>
        </div>
        <div style="padding: 15px; border-left: 4px solid #10B981; background-color: #ECFDF5; border-radius: 4px; margin-bottom: 12px;">
            <strong style="color: #047857;">🛡️ 防漂綠 (Anti-Greenwashing)</strong><br>
            <span style="color: #475569; font-size: 0.95rem;">揪出過度包裝、缺乏數據支撐或模糊不清的永續宣告。</span>
        </div>
        <div style="padding: 15px; border-left: 4px solid #8B5CF6; background-color: #F5F3FF; border-radius: 4px;">
            <strong style="color: #6D28D9;">📊 專業評級與建議</strong><br>
            <span style="color: #475569; font-size: 0.95rem;">產出視覺化燈號與具體行動方案，隨時可下載為 PDF 報告。</span>
        </div>
        """, unsafe_allow_html=True)

# --- 5. 執行審核與進度顯示 ---
if start_btn:
    if not SYSTEM_API_KEY:
        st.error("⚠️ 系統尚未設定安全金鑰，無法執行審核。請聯繫管理員。")
    elif not uploaded_file:
        st.warning("⚠️ 請先上傳一份 PDF 文件。")
    elif "系統提示：" in system_prompt:
        st.error(system_prompt)
    else:
        # 優化加載體驗
        with st.status("🔍 TruESG 引擎啟動中，請稍候...", expanded=True) as status:
            try:
                st.write("📄 正在從 PDF 萃取高密度文本...")
                proposal_text = extract_text_from_pdf(uploaded_file)
                st.session_state['raw_proposal_text'] = proposal_text
                
                st.write("🌐 連線至 LLM 核心評測叢集...")
                client = genai.Client(api_key=SYSTEM_API_KEY)
                
                final_prompt = f"""
                你是一個嚴格的第三方 ESG 審核系統。請完全依照以下【評分規則書】的邏輯，來審核使用者提交的【企劃書內容】。

                【⚠️ 重要排版與輸出結構要求 - 請嚴格遵守】：
                1. 報告的「最開頭第一段」必須是【一、 總體評估摘要與評分】，請直接排在最前面。
                   此區塊內必須清楚包含以下項目：
                   ・綜合結論：（請撰寫一段約 100~200 字的詳盡摘要，說明該企劃書的核心優勢、最重大的風險或缺失，以及企業整體的永續成熟度定調）
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
                6. 條列式說明請使用全形的「・」或中文數字「（一）、1.」開頭。
                7. 評分邏輯一致性：如果任何維度（E、S、G）的評分低於 5 分，其「缺失」欄位【絕對不可以】填寫「無」。必須具體指出為何未能獲得滿分（例如：缺乏量化目標、無高階認證、揭露不夠全面等扣分原因）。

                【評分規則書】：
                {system_prompt}

                ---
                【企劃書內容】：
                {proposal_text}
                """
                
                st.write("🧠 正在進行防漂綠比對與國際框架交叉分析 (預計 10-20 秒)...")
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=final_prompt
                )
                
                status.update(label="✅ 分析完成，報告已生成！", state="complete", expanded=False)
                st.session_state['audit_report'] = response.text
                st.session_state['audit_time'] = datetime.now().strftime("%Y%m%d_%H%M")
                st.toast("✅ 智審報告已就緒！")

            except Exception as e:
                status.update(label="❌ 處理期間發生錯誤", state="error", expanded=True)
                st.error(f"連線或分析時發生錯誤：{e}")

# --- 6. 專業化報告展示區 (Tab 結構) ---
if 'audit_report' in st.session_state:
    st.markdown("<hr style='margin-top: 3rem; margin-bottom: 2rem;'>", unsafe_allow_html=True)
    report_text = st.session_state['audit_report']
    
    # 提取分數資訊
    e_score = re.search(r'環境.*?(\d+)分', report_text)
    s_score = re.search(r'社會.*?(\d+)分', report_text)
    g_score = re.search(r'治理.*?(\d+)分', report_text)
    
    e_val = f"{e_score.group(1)} / 5" if e_score else "需人工檢視"
    s_val = f"{s_score.group(1)} / 5" if s_score else "不及格 🚨"
    g_val = f"{g_score.group(1)} / 5" if g_score else "需人工檢視"

    # 使用 Tabs 整理資訊架構
    tab1, tab2, tab3 = st.tabs(["📊 總體診斷儀表板", "📋 詳細基準審查", "📄 下載與原始報告"])
    
    # --- Tab 1: 總體診斷 ---
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        
        # 根據分數給予不同顏色的邊框
        def get_color(score_str):
            if "不及格" in score_str or ("/" in score_str and int(score_str.split("/")[0].strip()) <= 2):
                return "#EF4444" # Red
            elif "/" in score_str and int(score_str.split("/")[0].strip()) == 3:
                return "#F59E0B" # Yellow
            return "#10B981" # Green
            
        with m1:
            render_metric_card("環境保護 (E) 評級", e_val, "🌍", get_color(e_val))
        with m2:
            render_metric_card("社會責任 (S) 評級", s_val, "🤝", get_color(s_val))
        with m3:
            render_metric_card("公司治理 (G) 評級", g_val, "🏛️", get_color(g_val))
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📝 綜合結論摘要")
        # 萃取綜合結論部分 (支援多行提取，直到遇到下一個評分標題或段落)
        summary_match = re.search(r'綜合結論：(.*?)(?=・環境|環境（E）|環境\(E\)|二、)', report_text, re.DOTALL)
        summary_text = summary_match.group(1).strip() if summary_match else "請參閱詳細審查內容。"
        st.info(summary_text)

    # --- Tab 2: 詳細基準審查 ---
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        # 將純文字報告進行美化渲染
        with st.container(border=True):
            lines = report_text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if re.match(r'^(一|二|三|四|五|六|七|八|九|十)、', line):
                    st.markdown(f"<h4 style='color: #1E3A8A; margin-top: 1.5rem;'>{line}</h4>", unsafe_allow_html=True)
                    st.divider()
                elif "評分：" in line or "分 / 5分" in line or "綜合結論：" in line:
                    # 讓這些重要資訊在詳細報告區也顯示出來，並加上對應顏色
                    if "1分" in line or "不及格" in line or "不合格" in line:
                        st.markdown(f"<div style='color: #DC2626; font-weight: bold;'>{line}</div>", unsafe_allow_html=True)
                    elif "2分" in line or "需重大改善" in line:
                        st.markdown(f"<div style='color: #D97706; font-weight: bold;'>{line}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div style='color: #059669; font-weight: bold;'>{line}</div>", unsafe_allow_html=True)
                elif line.startswith("優點"):
                    st.markdown(f"<div style='color: #047857; font-weight: 600; padding: 4px 0;'>✅ {line}</div>", unsafe_allow_html=True)
                elif line.startswith("缺失"):
                    st.markdown(f"<div style='color: #B91C1C; font-weight: 600; padding: 4px 0;'>⚠️ {line}</div>", unsafe_allow_html=True)
                elif "嚴重不足" in line or "不合格" in line:
                    st.markdown(f"<div style='color: #DC2626; font-weight: bold; background-color: #FEE2E2; padding: 8px; border-radius: 4px;'>🚨 {line}</div>", unsafe_allow_html=True)
                elif line.startswith("・") or line.startswith("·"):
                    st.markdown(f"<div style='padding-left: 20px; color: #4B5563; line-height: 1.6;'>{line}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='color: #374151; line-height: 1.6;'>{line}</div>", unsafe_allow_html=True)

    # --- Tab 3: 下載與原始資料 ---
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        col_down1, col_down2 = st.columns([1, 1])
        with col_down1:
            st.markdown("### 📥 匯出正式審核報告")
            st.write("您可以將上述 AI 審核結果匯出為具備排版格式的 PDF 檔案，做為內部參考或會議資料。")
            
            pdf_bytes = generate_pdf_bytes(report_text)
            file_name = f"TruESG_Review_Report_{st.session_state['audit_time']}.pdf"
            st.download_button(
                label="📄 點此下載 PDF 報告",
                data=pdf_bytes,
                file_name=file_name,
                mime="application/pdf",
                type="primary"
            )
        
        with col_down2:
            with st.expander("👁️ 檢視 AI 產出的原始文字格式 (Raw Text)"):
                st.text_area("報告原碼", report_text, height=300, disabled=True)
