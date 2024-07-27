Pada esp32.ino lakukan perubahan pada

const char* ssid = "Masukkan nama wifi";
const char* password = "Masukkan password wifi";
String serverName = "Masukkan IP Address Computer";

port yang digunakan adalah port 5000
const int serverPort = 5000;

Pada Streamlit_app.py lakukan perubahan pada
flask_output_url = "http://Ip Address Computer:5000/output"
flask_image_url = "http://Ip Address Computer/outputs/prediction.jpg"

Pastikan bahwa esp32, perangkat menjalankan server flask, dan perangkat untuk mengakses streamlit menggunakan jaringan yang sama

Cara menjalankan
1. Jalankan pada terminal python app.py
2. Jalankan pada terminal run streamlit Streamlit_app.py
Maka akan secara otomatis mengarahkan pada web streamlit

Jika ingin mengakses web streamlit menggunakan device berbeda dalam jaringan yang sama, masukkan URL yang sama sesuai dengan URL yang diarahkan sebelumnya