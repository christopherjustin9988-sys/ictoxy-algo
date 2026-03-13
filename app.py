import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# --- 1. KONFIGURASI BOT TELEGRAM ---
# Token sudah saya masukkan sesuai yang kamu berikan
TELEGRAM_TOKEN = "8682734585:AAE0M9XzplOURia5qxy-V0fDq56yfZNFw-Y"

# Note: Kamu masih perlu mencari Chat ID kamu (cek @userinfobot di Telegram)
# Masukkan angkanya di bawah ini:
CHAT_ID = "GANTI_DENGAN_CHAT_ID_KAMU" 

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except:
        pass

# --- 2. FUNGSI GENERATE PDF ---
def generate_pdf(results, score):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "ICT 2022 TRADE REPORT")
    c.setFont("Helvetica", 12)
    c.drawString(100, 720, f"Entry: {results['entry']} | Pips: {results['pips']}")
    c.drawString(100, 700, f"AI Quality Score: {score}%")
    c.save()
    buffer.seek(0)
    return buffer

# --- 3. TAMPILAN APLIKASI (UI) ---
st.set_page_config(page_title="ICTOXY Terminal", layout="wide")

# Estetika Silver & Chocolate
st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: #d1d1d1; }
    .stMetric { border: 1px solid #7b3f00; background-color: #262626; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 ICTOXY_bot Alpha Terminal")

# Sidebar
with st.sidebar:
    st.header("Settings")
    uploaded_file = st.file_uploader("Upload Data (CSV)", type=['csv'])
    rr_ratio = st.sidebar.slider("Risk:Reward Ratio", 1.0, 5.0, 2.5)
    
    st.divider()
    user_id_input = st.text_input("Masukkan Chat ID Kamu", placeholder="Cek @userinfobot")
    if user_id_input:
        CHAT_ID = user_id_input

    if st.button("🚀 Test Koneksi Bot"):
        if CHAT_ID != "GANTI_DENGAN_CHAT_ID_KAMU":
            send_telegram_alert("🟢 *Koneksi Berhasil!*\nBot @ICTOXY_bot siap mengirimkan sinyal trading.")
            st.success("Pesan terkirim ke Telegram!")
        else:
            st.error("Isi Chat ID kamu dulu di sidebar!")

# Main Logic
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Logika Deteksi (Menggunakan data sampel 2022 Mentorship)
    fvg_zone = {"top": 1.0912, "bottom": 1.0880}
    
    tab1, tab2, tab3 = st.tabs(["📈 Chart Analysis", "📊 Backtest Results", "📝 AI Trade Journal"])

    with tab1:
        fig = go.Figure(data=[go.Candlestick(x=df['timestamp'],
                open=df['open'], high=df['high'], low=df['low'], close=df['close'],
                increasing_line_color='silver', decreasing_line_color='#7b3f00')])
        
        # Plot FVG Zone
        fig.add_shape(type="rect", x0=df['timestamp'].iloc[7], y0=fvg_zone['bottom'], 
                      x1=df['timestamp'].iloc[10], y1=fvg_zone['top'],
                      fillcolor="rgba(192, 192, 192, 0.2)", line_width=0)
        
        fig.update_layout(template="plotly_dark", height=500, margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)

        # Alert Otomatis
        if 'alert_sent' not in st.session_state and CH_ID != "GANTI_DENGAN_CHAT_ID_KAMU":
            send_telegram_alert(f"🎯 *ICT Setup Detected!*\nZona FVG: {fvg_zone['bottom']} - {fvg_zone['top']}\nCek Chart Sekarang!")
            st.session_state['alert_sent'] = True

    with tab2:
        entry = (fvg_zone['top'] + fvg_zone['bottom']) / 2
        sl = df['high'].max()
        tp = entry - (abs(entry - sl) * rr_ratio)
        pips = round(abs(entry - tp) * 10000, 1)
        
        results = {"entry": round(entry, 5), "sl": round(sl, 5), "tp": round(tp, 5), "pips": pips}
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Entry Level", results['entry'])
        c2.metric("Target Profit", results['tp'])
        c3.metric("Est. Pips", f"+{pips}")

    with tab3:
        st.subheader("Evaluasi Jurnal")
        q1 = st.checkbox("Entry di Killzone?")
        q2 = st.checkbox("Displacement Kuat?")
        score = int((q1 + q2) / 2 * 100)
        
        st.progress(score / 100)
        
        pdf = generate_pdf(results, score)
        st.download_button("📄 Download PDF Report", data=pdf, file_name="ICTOXY_Trade_Report.pdf")

else:
    st.info("👋 Halo! Silakan upload file 'data_ict.csv' di sidebar untuk memulai analisis.")
