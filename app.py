import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Konfigurasi Halaman (Lebar)
st.set_page_config(page_title="Dashboard Lazatto", layout="wide")

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    try:
        # Mencoba membaca file Excel asli Anda
        file_name = 'Data Omset Lazatto Th 2025_Mei 2026.xlsm'
        df_database = pd.read_excel(file_name, sheet_name='database')
        df_general = pd.read_excel(file_name, sheet_name='data general')
        return df_database, df_general
    except Exception:
        # Jika file belum ada di folder yang sama, gunakan data simulasi agar aplikasi tetap jalan
        st.info("💡 File Excel asli belum terbaca. Menampilkan data simulasi untuk preview UI.")
        dates = pd.date_range(start="2025-01-01", periods=100)
        df_database = pd.DataFrame({
            'Bulan': dates.month_name(),
            'Area': np.random.choice(['Area 1', 'Area 2', 'Area 3'], 100),
            'Entitas': np.random.choice(['Lazatto A', 'Lazatto B', 'Lazatto C'], 100),
            'COGS': np.random.randint(5000000, 15000000, 100),
            'Profit': np.random.randint(2000000, 8000000, 100)
        })
        return df_database, None

df_db, df_gen = load_data()

# --- MENU NAVIGASI ---
st.sidebar.title("Navigasi Dashboard")
menu = st.sidebar.radio("Pilih Halaman:", 
    ["📊 1. Dashboard Utama", "📈 2. Grafik & Visual", "⚙️ 3. Admin Panel"]
)

# --- HALAMAN 1: DASHBOARD UTAMA ---
if menu == "📊 1. Dashboard Utama":
    st.title("Tampilan Data General & Database")
    
    st.markdown("### Filter Data")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        area_list = df_db['Area'].unique().tolist()
        selected_area = st.multiselect("Pilih Area", area_list, default=area_list)
    with col2:
        entitas_list = df_db['Entitas'].unique().tolist()
        selected_entitas = st.multiselect("Pilih Entitas", entitas_list, default=entitas_list)
    with col3:
        min_cogs, max_cogs = int(df_db['COGS'].min()), int(df_db['COGS'].max())
        selected_cogs = st.slider("Rentang COGS", min_value=min_cogs, max_value=max_cogs, value=(min_cogs, max_cogs))
    with col4:
        min_profit, max_profit = int(df_db['Profit'].min()), int(df_db['Profit'].max())
        selected_profit = st.slider("Rentang Profit", min_value=min_profit, max_value=max_profit, value=(min_profit, max_profit))

    # Filter Bulan (Beberapa bulan terakhir)
    bulan_list = df_db['Bulan'].unique().tolist()
    selected_bulan = st.multiselect("Pilih Bulan (Tampilan Beberapa Bulan Terakhir)", bulan_list, default=bulan_list[:3])

    # Proses Filtering Data
    filtered_df = df_db[
        (df_db['Area'].isin(selected_area)) &
        (df_db['Entitas'].isin(selected_entitas)) &
        (df_db['COGS'] >= selected_cogs[0]) & (df_db['COGS'] <= selected_cogs[1]) &
        (df_db['Profit'] >= selected_profit[0]) & (df_db['Profit'] <= selected_profit[1]) &
        (df_db['Bulan'].isin(selected_bulan))
    ]

    st.markdown("---")
    st.markdown("### Ringkasan Cepat (Sesuai Tombol UI Data General)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total COGS", f"Rp {filtered_df['COGS'].sum():,.0f}")
    c2.metric("Total Profit", f"Rp {filtered_df['Profit'].sum():,.0f}")
    c3.metric("Total Transaksi", f"{len(filtered_df)} Data")

    st.markdown("### Tabel Database (Tersaring)")
    st.dataframe(filtered_df, use_container_width=True)

# --- HALAMAN 2: GRAFIK ---
elif menu == "📈 2. Grafik & Visual":
    st.title("Grafik Analisa (Halaman Terpisah)")
    st.write("Seluruh grafik visualisasi dipisahkan ke halaman ini agar halaman utama fokus pada angka.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Tren Profit per Bulan")
        trend_df = df_db.groupby('Bulan')['Profit'].sum().reset_index()
        fig_line = px.line(trend_df, x='Bulan', y='Profit', markers=True)
        st.plotly_chart(fig_line, use_container_width=True)
        
    with col2:
        st.subheader("Komparasi Profit per Area")
        pie_df = df_db.groupby('Area')['Profit'].sum().reset_index()
        fig_pie = px.pie(pie_df, names='Area', values='Profit', hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)

# --- HALAMAN 3: ADMIN PANEL ---
elif menu == "⚙️ 3. Admin Panel":
    st.title("Portal Input Data (Khusus Admin)")
    
    # Keamanan Sederhana
    password = st.text_input("Masukkan Password Admin:", type="password")
    
    if password == "admin123":  # Password dummy untuk tes
        st.success("Akses Terbuka!")
        
        st.markdown("### 1. Upload Update File Harian")
        uploaded_file = st.file_uploader("Upload file Excel terbaru (.xlsm / .xlsx)", type=["xlsx", "xlsm"])
        if uploaded_file is not None:
            st.success("File berhasil diunggah! Data siap diproses ke database pusat.")
            
        st.markdown("---")
        st.markdown("### 2. Input Data Manual (Harian)")
        with st.form("input_manual"):
            col_a, col_b = st.columns(2)
            with col_a:
                new_bulan = st.selectbox("Bulan", ["Januari", "Februari", "Maret", "April", "Mei"])
                new_area = st.selectbox("Area", ["Area 1", "Area 2", "Area 3"])
                new_entitas = st.text_input("Nama Entitas")
            with col_b:
                new_cogs = st.number_input("COGS (Rp)", min_value=0)
                new_profit = st.number_input("Profit (Rp)", min_value=0)
            
            submit = st.form_submit_button("Tambahkan ke Database")
            if submit:
                st.success(f"Berhasil! Data {new_entitas} ditambahkan.")
    elif password != "":
        st.error("Password salah. Silakan coba lagi.")