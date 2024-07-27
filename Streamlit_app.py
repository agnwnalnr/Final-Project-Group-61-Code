import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from streamlit_autorefresh import st_autorefresh
from gtts import gTTS
import base64

flask_output_url = "http://Ip Address Computer:5000/output"
flask_image_url = "http://Ip Address Computer/outputs/prediction.jpg"

def get_output_data():
    response = requests.get(flask_output_url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def hitung_jarak(y_bottom):
    jarak_dict = {1: 905, 2: 676, 3: 606, 4: 506, 5: 475}
    jarak_terdekat = min(jarak_dict.keys(), key=lambda k: abs(jarak_dict[k] - y_bottom))
    return jarak_terdekat

def buat_audio(kelas, jarak):
    teks = f"Ada {kelas} pada jarak {jarak} meter."
    tts = gTTS(text=teks, lang='id')
    nama_file = "output.mp3"
    tts.save(nama_file)
    return nama_file

st.set_page_config(
    page_title="Smart Assistive Device",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="auto"
)

st.markdown("""
    <style>
    .title {
        font-size: 36px;
        font-weight: bold;
        text-align: center;
        color: #4B9CD3;
    }
    .subtitle {
        font-size: 24px;
        text-align: center;
        color: #4B9CD3;
        margin-top: -10px;
    }
    .image-container {
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }
    .caption {
        text-align: center;
        font-size: 24px;
        color: #333;
        font-weight: bold;
        margin-top: 10px;
    }
    .class-container {
        text-align: center;
        margin-top: 20px;
    }
    .class-label {
        font-size: 24px;
        font-weight: bold;
        color: #4B9CD3;
    }
    .class-value {
        font-size: 24px;
        color: #333;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">Smart Assistive Device</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Image Output and Class Display</div>', unsafe_allow_html=True)

st_autorefresh(interval=10000, key="data_refresh")

output_data = get_output_data()

if output_data:
    image_class = output_data.get('class')
    x = output_data.get('x')
    y = output_data.get('y')
    width = output_data.get('width')
    height = output_data.get('height')
    if x and y and width and height:
        y_bottom = y + (height / 2)
        jarak = hitung_jarak(y_bottom)
    else:
        jarak = None

    image_response = requests.get(flask_image_url)
    if image_response.status_code == 200:
        image = Image.open(BytesIO(image_response.content))
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.image(image, caption="", use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="caption">Prediction Output</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="class-container"><span class="class-label">Kelas:</span> <span class="class-value">{image_class}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="class-container"><span class="class-label">Jarak:</span> <span class="class-value">{jarak} meter</span></div>', unsafe_allow_html=True)

        if image_class and jarak:
            nama_file_audio = buat_audio(image_class, jarak)
            audio_file = open(nama_file_audio, 'rb')
            audio_bytes = audio_file.read()
            audio_base64 = base64.b64encode(audio_bytes).decode()

            st.markdown(f"""
                <audio id="audio" controls autoplay>
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                </audio>
                <script>
                    var audio = document.getElementById('audio');
                    audio.muted = true;
                    audio.play();
                    setTimeout(function() {{
                        audio.muted = false;
                    }}, 1000);
                </script>
            """, unsafe_allow_html=True)
    else:
        st.write("Failed to load image from the URL")
else:
    st.write("No output data available")
