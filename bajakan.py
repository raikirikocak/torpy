import time
import streamlit as st
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

    if st.button("Tampilkan Halaman"):
        # Menyematkan halaman web menggunakan iframe
        st.markdown(f'<iframe src="{url}" width="800" height="600" frameborder="0"></iframe>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
