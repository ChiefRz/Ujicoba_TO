import streamlit as st
import json
import os
import streamlit.components.v1 as components

# --- PENGATURAN AWAL ---
st.set_page_config(page_title="Aplikasi Ujian Online", layout="wide")
st.title("📝 Aplikasi Ujian Online Sederhana")
# MENAMBAHKAN JANGKAR (ANCHOR) YANG TIDAK TERLIHAT DI SINI
st.markdown("<a id='top'></a>", unsafe_allow_html=True)
st.write("Jawablah pertanyaan di bawah ini dengan memilih salah satu jawaban yang paling tepat.")

# --- FUNGSI UNTUK MEMUAT SOAL DARI SATU FILE ---
@st.cache_data
def muat_soal():
    """Memuat semua soal dari satu file JSON."""
    file_path = 'data/bank_soal.json'
    
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

# --- BAGIAN UTAMA APLIKASI ---

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
            st.subheader(f"{i+1}. {soal['pertanyaan']}")
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
            st.rerun()

# --- TAMPILAN HASIL DAN PEMBAHASAN ---
elif st.session_state.ujian_selesai and daftar_soal:
    
    # MENGGUNAKAN METODE JANGKAR UNTUK LANGSUNG LOMPAT KE ATAS
    components.html(
        """
        <script>
            window.location.hash = "#top";
        </script>
        """,
        height=0
    )
    
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
            st.subheader(f"{i+1}. {soal['pertanyaan']}")
            
            # Mendefinisikan kunci jawaban sekali saja untuk kebersihan kode
            jawaban_benar_key = soal['jawaban_benar']
            jawaban_user_key = st.session_state.jawaban_pengguna.get(i)
            
            # Membuat teks jawaban lengkap
            jawaban_benar_lengkap = f"{jawaban_benar_key.upper()}. {soal['pilihan'][jawaban_benar_key]}"
            if jawaban_user_key:
                jawaban_user_lengkap = f"{jawaban_user_key.upper()}. {soal['pilihan'][jawaban_user_key]}"
            else:
                jawaban_user_lengkap = "Tidak dijawab"

            # Menampilkan jawaban
            st.write(f"Jawaban Anda: **{jawaban_user_lengkap}**")
            st.write(f"Kunci Jawaban: **{jawaban_benar_lengkap}**")

            # Memeriksa kebenaran jawaban
            if jawaban_user_key == jawaban_benar_key:
                st.markdown("✅ **Benar**")
            else:
                st.markdown("❌ **Salah**")
            
            with st.expander("Lihat Penjelasan"):
                st.info(soal['penjelasan'])
        st.markdown("---")

    if st.button("Ulangi Ujian"):
        st.session_state.ujian_selesai = False
        st.session_state.jawaban_pengguna = {}
        st.rerun()

elif not daftar_soal:
    st.info("Tidak ada soal yang tersedia atau file soal gagal dimuat.")