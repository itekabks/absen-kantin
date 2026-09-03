import datetime
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.title("📌 Absensi Sederhana")

# Hubungkan ke Google Sheet
conn = st.connection("gsheets", type=GSheetsConnection)

# Input NIK
nik = st.text_input("Masukkan NIK Anda:")

if st.button("Kirim Absen"):
    if nik:
        # Ambil data lama & buat DataFrame data baru
        data_lama = conn.read()
        waktu = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Nama kolom disesuaikan: "waktu" (huruf kecil) dan "NIK" (huruf besar)
        data_baru = pd.DataFrame([{"waktu": waktu, "NIK": nik}])

        # Gabungkan data lama dan baru
        df_update = pd.concat([data_lama, data_baru], ignore_index=True)

        # Simpan kembali ke Google Sheet
        conn.update(data=df_update)
        st.success(f"✅ Berhasil absen untuk NIK: {nik}")
    else:
        st.warning("Isi NIK terlebih dahulu!")
