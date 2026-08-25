import sys
import subprocess
import threading
import os
import streamlit.components.v1 as components

# Install streamlit jika belum ada
try:
    import streamlit as st
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    import streamlit as st


def run_ffmpeg(video_path, stream_key, is_shorts, log_callback):
    output_url = f"rtmp://a.rtmp.youtube.com/live2/{stream_key}"
    
    # Membangun perintah FFmpeg dengan urutan filter yang benar
    cmd = [
        "ffmpeg", "-re", "-stream_loop", "-1", "-i", video_path
    ]
    
    # Jika mode Shorts aktif, pasang filter scale sebelum format output
    if is_shorts:
        cmd += ["-vf", "scale=720:1280"]

    cmd += [
        "-c:v", "libx264", "-preset", "veryfast", "-b:v", "2500k",
        "-maxrate", "2500k", "-bufsize", "5000k",
        "-g", "60", "-keyint_min", "60",
        "-c:a", "aac", "-b:a", "128k",
        "-f", "flv",
        output_url
    ]

    log_callback(f"Menjalankan: {' '.join(cmd)}")
    try:
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True
        )
        # Simpan objek proses agar bisa di-terminate saat tombol Stop diklik
        st.session_state['current_process'] = process

        for line in process.stdout:
            log_callback(line.strip())
        process.wait()
    except Exception as e:
        log_callback(f"Error: {e}")
    finally:
        log_callback("Streaming selesai atau dihentikan.")
        st.session_state['current_process'] = None


def main():
    st.set_page_config(
        page_title="YouTube Live Streaming",
        page_icon="🎥",
        layout="wide"
    )
    st.title("Live Streaming YouTube")

    # Bagian iklan (optional)
    show_ads = st.checkbox("Tampilkan Iklan", value=True)
    if show_ads:
        st.subheader("Iklan Sponsor")
        components.html(
            """
            <div style="background:#f0f2f6;padding:20px;border-radius:10px;text-align:center">
                <script type='text/javascript' 
                        src='//pl26562103.profitableratecpm.com/28/f9/95/28f9954a1d5bbf4924abe123c76a68d2.js'>
                </script>
                <p style="color:#888">Iklan akan muncul di sini</p>
            </div>
            """,
            height=300
        )

    # List video yang ada di direktori
    video_files = [f for f in os.listdir('.') if f.endswith(('.mp4', '.flv'))]

    st.write("Video yang tersedia:")
    selected_video = st.selectbox("Pilih video", video_files) if video_files else None

    uploaded_file = st.file_uploader("Upload video baru (maks. 500 MB, mp4/flv - codec H264/AAC)", type=['mp4', 'flv'])

    if uploaded_file:
        video_path = uploaded_file.name
        if not os.path.exists(video_path):
            with st.spinner("Menyimpan video..."):
                with open(video_path, "wb") as f:
                    while True:
                        chunk = uploaded_file.read(1024 * 1024)  # 1 MB
                        if not chunk:
                            break
                        f.write(chunk)
            st.success(f"Video berhasil diupload: {uploaded_file.name}")
            st.rerun()
        else:
            video_path = uploaded_file.name
    elif selected_video:
        video_path = selected_video
    else:
        video_path = None

    # Input stream key YouTube
    stream_key = st.text_input("Stream Key YouTube", type="password")
    is_shorts = st.checkbox("Mode Shorts (720x1280)")

    # Tempat log
    log_placeholder = st.empty()
    if 'logs' not in st.session_state:
        st.session_state['logs'] = []

    def log_callback(msg):
        st.session_state['logs'].append(msg)
        try:
            log_placeholder.text("\n".join(st.session_state['logs'][-20:]))
        except:
            print(msg)

    if 'ffmpeg_thread' not in st.session_state:
        st.session_state['ffmpeg_thread'] = None
    if 'current_process' not in st.session_state:
        st.session_state['current_process'] = None

    col_btn1, col_btn2 = st.columns(2)

    # Tombol Start
    with col_btn1:
        if st.button("Mulai Streaming", type="primary"):
            if not video_path or not stream_key:
                st.error("Video dan Stream Key harus diisi!")
            else:
                st.session_state['streaming'] = True
                st.session_state['ffmpeg_thread'] = threading.Thread(
                    target=run_ffmpeg, args=(video_path, stream_key, is_shorts, log_callback), daemon=True)
                st.session_state['ffmpeg_thread'].start()
                st.success("Streaming dimulai ke YouTube!")

    # Tombol Stop (Menghentikan proses spesifik tanpa pkill massal)
    with col_btn2:
        if st.button("Hentikan Streaming"):
            st.session_state['streaming'] = False
            proc = st.session_state.get('current_process')
            if proc is not None:
                proc.terminate()
                st.session_state['current_process'] = None
                st.warning("Streaming dihentikan!")
            else:
                st.info("Tidak ada proses streaming aktif yang perlu dihentikan.")

    log_placeholder.text("\n".join(st.session_state['logs'][-20:]))


if __name__ == '__main__':
    main()
