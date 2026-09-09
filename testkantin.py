# Eksekusi Proses Absen
if st.session_state.last_submitted_nik:
    input_nik = st.session_state.last_submitted_nik
    st.session_state.last_submitted_nik = ""
    
    # 1. Cek apakah hanya angka
    if not input_nik.isdigit():
        st.error("⚠️ NIK hanya boleh berisi angka!")
    # 2. Cek apakah panjang NIK tepat 8 digit
    elif len(input_nik) != 8:
        st.error(f"❌ NIK harus berjumlah tepat 8 digit angka! (Anda mengetik {len(input_nik)} digit)")
    else:
        nik_clean = input_nik
        if is_already_absent_today(nik_clean):
            st.error(f"❌ NIK {nik_clean} SUDAH ABSEN HARI INI!")
        else:
            nama_karyawan = db_karyawan.get(nik_clean, "Nama Tidak Ditemukan")
            payload = {
                ENTRY_NIK: nik_clean,
                ENTRY_NAMA: nama_karyawan
            }
            try:
                response = requests.post(FORM_URL, data=payload)
                if response.status_code == 200:
                    if nama_karyawan != "Nama Tidak Ditemukan":
                        st.success(f"✅ Berhasil Absen: **{nama_karyawan.title()}** (NIK: {nik_clean})")
                    else:
                        st.warning(f"⚠️ Berhasil Absen NIK: **{nik_clean}** *(Nama tidak di database)*")
                else:
                    st.error(f"❌ Gagal mengirim data. Code: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan koneksi: {e}")
