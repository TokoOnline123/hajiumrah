import streamlit as st
import threading
from streamlit.runtime.scriptrunner import add_script_run_ctx

# 1. Inisialisasi session_state di alur utama
if 'logs' not in st.session_state:
    st.session_state['logs'] = []

def log_callback(msg):
    # Akses session state aman setelah inisialisasi
    if 'logs' in st.session_state:
        st.session_state['logs'].append(msg)

def run_ffmpeg(cmd):
    # Logika eksekusi ffmpeg Anda
    pass

# 2. Saat memanggil thread, tambahkan script run context
def start_ffmpeg_thread(cmd):
    t = threading.Thread(target=run_ffmpeg, args=(cmd,), name="run_ffmpeg")
    add_script_run_ctx(t)  # Menyambungkan thread ke konteks Streamlit
    t.start()

# 3. Ganti st.components.v1.html dengan st.iframe
# Sebelum: st.components.v1.html(html_code)
# Sesudah:
# st.iframe(src="...", width=..., height=...)
