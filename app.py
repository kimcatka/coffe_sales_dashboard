import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="From Beans to Business - Analytics Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

sns.set_theme(style="whitegrid")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'

@st.cache_data
def load_data():
    df = pd.read_csv('coffe_sales.csv')
    
    df['Date'] = pd.to_datetime(df['Date'])
    df['Day_Type'] = np.where(df['Weekday'].isin(['Sat', 'Sun']), 'Weekend', 'Weekday')
    df['Beverage_Category'] = np.where(df['coffee_name'].isin(['Hot Chocolate', 'Cocoa']), 'Non-Coffee', 'Coffee')
    
    df['YearMonth'] = df['Date'].dt.to_period('M').astype(str)
    
    df = df.drop_duplicates().reset_index(drop=True)
    return df

df = load_data()

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/924/924514.png", width=80)

st.sidebar.title("☕ Filter Dashboard")
st.sidebar.markdown("Sesuaikan tampilan data di bawah ini:")

st.sidebar.subheader("1. Kategori Minuman")
show_coffee = st.sidebar.checkbox("Coffee (Latte, Americano, dll)", value=True)
show_non_coffee = st.sidebar.checkbox("Non-Coffee (Cocoa, Hot Chocolate)", value=True)

selected_categories = []
if show_coffee: selected_categories.append('Coffee')
if show_non_coffee: selected_categories.append('Non-Coffee')

st.sidebar.subheader("2. Tipe Hari")
show_weekday = st.sidebar.checkbox("Weekday (Senin - Jumat)", value=True)
show_weekend = st.sidebar.checkbox("Weekend (Sabtu - Minggu)", value=True)

selected_days = []
if show_weekday: selected_days.append('Weekday')
if show_weekend: selected_days.append('Weekend')

st.sidebar.subheader("3. Periode Bulan")
available_months = sorted(df['YearMonth'].unique())
selected_months = st.sidebar.multiselect(
    "Pilih Bulan - Tahun:",
    options=available_months,
    default=available_months,
    help="Hapus pilihan untuk melihat bulan tertentu saja, atau biarkan semua terpilih untuk tren tahunan."
)

filtered_df = df[
    (df['Beverage_Category'].isin(selected_categories)) & 
    (df['Day_Type'].isin(selected_days)) &
    (df['YearMonth'].isin(selected_months))
]

if filtered_df.empty:
    st.warning("⚠️ Data tidak ditemukan! Silakan centang minimal satu pilihan pada setiap filter di sidebar kiri.")
    st.stop()

st.title("☕ From Beans to Business: Mengubah Data Transaksi Kopi Menjadi Strategi Pertumbuhan Revenue")
st.markdown("---")

total_revenue = filtered_df['money'].sum()
total_trx = len(filtered_df)
aov = total_revenue / total_trx if total_trx > 0 else 0
peak_hour = filtered_df['hour_of_day'].mode()[0] if not filtered_df.empty else "-"

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="💰 Total Revenue", value=f"${total_revenue:,.1f}")
with col2:
    st.metric(label="☕ Total Produk Terjual", value=f"{total_trx:,} Cup")
with col3:
    st.metric(label="🛒 Rata-Rata Nilai Transaksi", value=f"${aov:,.2f}")
with col4:
    st.metric(label="⏰ Jam Padat (Peak Hour)", value=f"{peak_hour}:00")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "⏰ Pola Jam Sibuk", 
    "☕ Kinerja Menu Produk", 
    "📅 Weekday vs Weekend", 
    "📈 Tren Finansial Bulanan"
])

with tab1:
    st.subheader("Analisis Jam Operasional & Peak Hours")
    st.markdown("Visualisasi di bawah memetakan volume pemesanan per jam untuk membantu penempatan jadwal shift barista.")
    
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    hour_counts = filtered_df['hour_of_day'].value_counts().sort_index()
    sns.barplot(x=hour_counts.index, y=hour_counts.values, palette="Blues_d", ax=ax1)
    
    for p in ax1.patches:
        ax1.annotate(f'{int(p.get_height())}', 
                     (p.get_x() + p.get_width() / 2., p.get_height()), 
                     ha='center', va='center', xytext=(0, 5), textcoords='offset points')
                     
    ax1.set_xlabel("Jam Operasional", fontsize=11)
    ax1.set_ylabel("Jumlah Transaksi (Cup)", fontsize=11)
    st.pyplot(fig1)
    
    st.info("💡 **Operasional:** Lonjakan pesanan tertinggi terjadi pada sesi pagi (**10:00 - 11:00**) dan kembali meningkat pada sesi sore (**16:00**). Sangat disarankan untuk memberlakukan *dynamic shift* pada jendela waktu tersebut.")

with tab2:
    st.subheader("Evaluasi Produk: Volume vs. Kontribusi Revenue")
    st.markdown("Membandingkan menu *Traffic Driver* (paling banyak dibeli) dengan menu *Revenue Generator* (penghasil uang terbesar).")
    
    fig2, axes2 = plt.subplots(1, 2, figsize=(16, 6))
    
    product_sales = filtered_df['coffee_name'].value_counts()
    sns.barplot(y=product_sales.index, x=product_sales.values, palette="viridis", ax=axes2[0])
    axes2[0].set_title("A. Menu Terlaris (Volume / Cup)", fontsize=13, fontweight='bold')
    axes2[0].set_xlabel("Cup Terjual")
    for p in axes2[0].patches:
        axes2[0].annotate(f'{int(p.get_width())}', (p.get_width(), p.get_y() + p.get_height() / 2.), 
                          ha='left', va='center', xytext=(5, 0), textcoords='offset points')
                          
    product_revenue = filtered_df.groupby('coffee_name')['money'].sum().sort_values(ascending=False)
    sns.barplot(y=product_revenue.index, x=product_revenue.values, palette="magma", ax=axes2[1])
    axes2[1].set_title("B. Kontribusi Pendapatan (Total Revenue)", fontsize=13, fontweight='bold')
    axes2[1].set_xlabel("Total Revenue ($)")
    axes2[1].set_ylabel("")
    for p in axes2[1].patches:
        axes2[1].annotate(f'{p.get_width():,.1f}', (p.get_width(), p.get_y() + p.get_height() / 2.), 
                          ha='left', va='center', xytext=(5, 0), textcoords='offset points')
                          
    plt.tight_layout()
    st.pyplot(fig2)
    
    st.success("💡 **Strategi Upselling:** Meskipun **Americano with Milk** memimpin dari segi volume penjualan, menu **Latte** adalah penyumbang pendapatan terbesar. Latih kasir untuk aktif merekomendasikan Latte guna memaksimalkan *Rata-Rata Nilai Penjualan*.")

with tab3:
    st.subheader("Perbandingan Pola Konsumsi: Hari Kerja vs. Akhir Pekan")
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.markdown("#### Proporsi Volume Transaksi")
        fig3_left, ax3_left = plt.subplots(figsize=(6, 6))
        day_counts = filtered_df['Day_Type'].value_counts()
        sns.barplot(x=day_counts.index, y=day_counts.values, palette="Set2", ax=ax3_left)
        ax3_left.set_ylabel("Total Transaksi")
        st.pyplot(fig3_left)
        
    with col_right:
        st.markdown("#### Pergeseran Jam Sibuk: Weekday vs Weekend")
        fig3_right, ax3_right = plt.subplots(figsize=(10, 5.5))
        sns.countplot(data=filtered_df, x='hour_of_day', hue='Day_Type', palette="Set2", ax=ax3_right)
        ax3_right.set_xlabel("Jam Operasional")
        ax3_right.set_ylabel("Jumlah Transaksi")
        ax3_right.legend(title='Tipe Hari')
        st.pyplot(fig3_right)
        
    st.warning("💡 **Karakteristik Target Pasar:** Transaksi sangat didominasi oleh hari kerja (**Weekday**). Ini menandakan kedai kopi berlokasi di kawasan perkantoran atau kampus, dimana pelanggan mencari kopi untuk rutinitas kerja, bukan rekreasi akhir pekan.")

with tab4:
    st.subheader("Tren Pertumbuhan Pendapatan Bulanan")
    st.markdown("Memantau fluktuasi pendapatan dari bulan ke bulan untuk mengidentifikasi pola musiman (*seasonality*).")
    
    monthly_rev = filtered_df.groupby('YearMonth')['money'].sum().reset_index()
    
    fig4, ax4 = plt.subplots(figsize=(14, 5))
    sns.lineplot(data=monthly_rev, x='YearMonth', y='money', marker='o', color='#06b6d4', linewidth=3, ax=ax4)
    ax4.set_xlabel("Bulan - Tahun", fontsize=11)
    ax4.set_ylabel("Total Pendapatan ($)", fontsize=11)
    plt.xticks(rotation=45)
    ax4.grid(True, linestyle='--', alpha=0.6)
    st.pyplot(fig4)
    
    st.error("💡 **Mitigasi Seasonality:** Terjadi lonjakan pada bulan Oktober & Februari (masa aktif kantor/kuliah), namun mengalami penurunan tajam pada bulan Juli & Januari (musim liburan panjang). Toko disarankan melayani langganan katering B2B saat musim liburan untuk menjaga stabilitas omset.")

st.markdown("---")
st.caption("☕ Project Akhir DQLab Bootcamp Data Analyst | Framework CRISP-DM | Disusun oleh: Hakim U.")