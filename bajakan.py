import time
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from stem import Signal
from stem.control import Controller
import random
import subprocess

# Fungsi untuk menghasilkan MAC Address acak
def generate_random_mac():
    mac = [0x02, 0x00, 0x00,
           random.randint(0x00, 0x7F),
           random.randint(0x00, 0xFF),
           random.randint(0x00, 0xFF)]
    return ':'.join(f'{x:02x}' for x in mac)

# Fungsi untuk mengganti IP menggunakan Tor
def change_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()  # jika Anda menggunakan password, gunakan controller.authenticate(password='YOUR_PASSWORD')
        controller.signal(Signal.NEWNYM)
        print("IP telah diganti.")

# Fungsi untuk mengubah alamat MAC
def change_mac_address(interface):
    new_mac = generate_random_mac()
    print(f"[INFO] Mengubah alamat MAC menjadi {new_mac}")

    # Perintah PowerShell untuk mengubah alamat MAC
    command = f"""
    $interface = Get-NetAdapter -Name '{interface}'
    if ($interface -ne $null) {{
        Set-NetAdapterAdvancedProperty -Name $interface.Name -DisplayName 'Network Address' -DisplayValue '{new_mac.replace(":", "")}'
        Write-Output 'Alat MAC berhasil diubah.'
    }} else {{
        Write-Output 'Interface tidak ditemukan.'
    }}
    """

    try:
        subprocess.run(['powershell', '-Command', command], check=True)
        print(f"[SUCCESS] Alamat MAC berhasil diubah menjadi {new_mac}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Gagal mengubah alamat MAC: {e}")

# Atur opsi untuk Chrome
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--proxy-server=socks5://127.0.0.1:9050')  # Menggunakan proxy Tor
    return webdriver.Chrome(options=chrome_options)

# Aplikasi Streamlit
def main():
    st.title("Aplikasi Ganti MAC Address dan IP")
    
    # Input URL tujuan
    url = st.text_input("Masukkan URL tujuan:", "https://whoer.net/")
    
    if st.button("Ganti MAC dan IP"):
        # Ganti MAC Address dan IP
        interface_name = "Wi-Fi"  # Ganti dengan nama interface yang sesuai
        change_mac_address(interface_name)
        change_ip()
        st.success("MAC Address dan IP telah berhasil diubah.")

    # Inisialisasi ChromeDriver jika belum ada
    if 'driver' not in st.session_state:
        st.session_state.driver = None

    if st.button("Akses URL"):
        # Jika driver belum ada, buat yang baru
        if st.session_state.driver is None:
            st.session_state.driver = setup_driver()
        
        st.session_state.driver.get(url)
        time.sleep(5)  # Tunggu untuk memuat halaman
        
        # Menampilkan halaman yang dituju
        st.write("Halaman yang dituju:")
        st.image(st.session_state.driver.get_screenshot_as_png(), use_column_width=True)

    if st.button("Tutup Driver"):
        if st.session_state.driver:
            st.session_state.driver.quit()
            st.session_state.driver = None
            st.success("Driver ditutup.")

if __name__ == "__main__":
    main()
