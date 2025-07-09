import streamlit as st
import json
import os

# --- PENGATURAN AWAL ---
st.set_page_config(page_title="Aplikasi Ujian Online", layout="wide")
st.title("📝 Aplikasi Ujian Online Sederhana")
st.write("Jawablah pertanyaan di bawah ini dengan memilih salah satu jawaban yang paling tepat.")

# --- FUNGSI UNTUK MEMUAT SOAL DARI SATU FILE ---
@st.cache_data # Cache data agar tidak perlu memuat ulang file setiap kali ada interaksi
def muat_soal():
    """Memuat semua soal dari satu file JSON."""
    file_path = 'data/bank_soal.json' # Nama file soal kita
    
    # Pastikan file ada
    if not os.path.exists(file_path):
        st.error(f"File soal '{file_path}' tidak ditemukan. Mohon buat dan upload filenya.")
        return []
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            daftar_soal = json.load(f)
        return daftar_soal
    except json.JSONDecodeError:
        st.error(f"Terdapat kesalahan format pada file JSON '{file_path}'. Mohon periksa kembali sintaksnya.")
        return []
    except Exception as e:
        st.error(f"Terjadi error saat memuat soal: {e}")
        return []


# --- BAGIAN UTAMA APLIKASI (Tidak ada yang berubah dari sini ke bawah) ---

# --- MEMUAT DATA SOAL ---
daftar_soal = muat_soal()

# Inisialisasi state
if 'jawaban_pengguna' not in st.session_state:
    st.session_state.jawaban_pengguna = {}
if 'ujian_selesai' not in st.session_state:
    st.session_state.ujian_selesai = False

# --- TAMPILAN SOAL UJIAN ---
if not st.session_state.ujian_selesai and daftar_soal:
    with st.form("form_ujian"):
        for i, soal in enumerate(daftar_soal):
            st.subheader(f"Soal {i+1}: {soal['pertanyaan']}")
            pilihan_jawaban = [f"{key.upper()}) {value}" for key, value in soal['pilihan'].items()]
            jawaban = st.radio(
                "Pilih jawaban Anda:",
                options=pilihan_jawaban,
                key=f"soal_{i}",
                label_visibility="collapsed"
            )
            st.session_state.jawaban_pengguna[i] = jawaban.split(')')[0].lower()
            st.markdown("---")

        tombol_selesai = st.form_submit_button("Selesai Ujian")
        if tombol_selesai:
            st.session_state.ujian_selesai = True
            st.experimental_rerun()

# --- TAMPILAN HASIL DAN PEMBAHASAN ---
elif st.session_state.ujian_selesai and daftar_soal:
    st.header("✨ Hasil Ujian Anda")
    
    skor = 0
    for i, soal in enumerate(daftar_soal):
        if st.session_state.jawaban_pengguna.get(i) == soal['jawaban_benar']:
            skor += 1

    persentase_skor = (skor / len(daftar_soal)) * 100
    st.success(f"Skor Anda: **{skor} dari {len(daftar_soal)} soal benar** ({persentase_skor:.2f}%)")
    st.markdown("---")

    st.header("🔑 Kunci Jawaban dan Penjelasan")
    for i, soal in enumerate(daftar_soal):
        with st.container():
            st.subheader(f"Soal {i+1}: {soal['pertanyaan']}")
            jawaban_benar = soal['jawaban_benar']
            jawaban_user = st.session_state.jawaban_pengguna.get(i)
            
            st.write(f"Jawaban Anda: **{jawaban_user.upper() if jawaban_user else 'Tidak dijawab'}**")
            st.write(f"Kunci Jawaban: **{jawaban_benar.upper()}**")

            if jawaban_user == jawaban_benar:
                st.markdown("✅ **Benar**")
            else:
                st.markdown("❌ **Salah**")
            
            with st.expander("Lihat Penjelasan"):
                st.info(soal['penjelasan'])
        st.markdown("---")

    if st.button("Ulangi Ujian"):
        st.session_state.ujian_selesai = False
        st.session_state.jawaban_pengguna = {}
        st.experimental_rerun()

elif not daftar_soal:
    st.info("Tidak ada soal yang tersedia atau file soal gagal dimuat.")