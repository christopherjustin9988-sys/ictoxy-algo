import streamlit as st
import requests
from PIL import Image
import io

# --- 1. KONFIGURASI ---
TELEGRAM_TOKEN = "8682734585:AAE0M9XzplOURia5qxy-V0fDq56yfZNFw-Y"

st.set_page_config(page_title="ICTOXY Visual Terminal", layout="wide")

# Estetika Silver & Chocolate
st.markdown("""
    <style>
    .main { background-color: #1a1a1a; color: #d1d1d1; }
    .stButton>button { background-color: #7b3f00; color: white; border-radius: 5px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏹 ICTOXY Visual Terminal (JPG Support)")

# Sidebar
with st.sidebar:
    st.header("🎛️ Dashboard Control")
    chat_id = st.text_input("Masukkan Chat ID Telegram", placeholder="Cek @userinfobot")
    
    st.divider()
    # Sekarang mendukung JPG, PNG, dan CSV
    uploaded_file = st.file_uploader("Upload Chart (JPG) atau Data (CSV)", type=['jpg', 'jpeg', 'png', 'csv'])
    
    if st.button("🚀 Test Bot"):
        if chat_id:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": chat_id, "text": "🟢 Koneksi Berhasil! Bot siap menerima update."})
            st.success("Cek Telegram kamu!")
        else:
            st.error("Isi Chat ID dulu!")

# --- 2. LOGIKA TAMPILAN ---
if uploaded_file is not None:
    # JIKA FILE ADALAH GAMBAR (JPG/PNG)
    if uploaded_file.type in ["image/jpeg", "image/png"]:
        image = Image.open(uploaded_file)
        st.image(image, caption="Current Chart Screenshot", use_container_width=True)
        
        st.info("💡 Kamu baru saja mengupload gambar. Karena ini bukan data angka (CSV), deteksi otomatis MSS/FVG dinonaktifkan. Gunakan tombol di bawah untuk kirim manual ke Telegram.")
        
        if st.button("📤 Kirim Screenshot ke Telegram"):
            if chat_id:
                # Kirim gambar ke Telegram
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr = img_byte_arr.getvalue()
                
                url_img = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
                files = {'photo': img_byte_arr}
                requests.post(url_img, data={'chat_id': chat_id, 'caption': "📊 My Chart Update from ICTOXY Terminal"}, files=files)
                st.success("Gambar terkirim ke Telegram!")
            else:
                st.error("Masukkan Chat ID di sidebar!")

    # JIKA FILE ADALAH CSV
    else:
        import pandas as pd
        import plotly.graph_objects as go
        df = pd.read_csv(uploaded_file)
        st.success("✅ Data Harga Terdeteksi! Menampilkan Interactive Chart...")
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], increasing_line_color='silver', decreasing_line_color='#7b3f00')])
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("👋 Selamat datang! Silakan upload screenshot chart kamu (JPG) untuk ditampilkan atau file CSV untuk analisis otomatis.")
