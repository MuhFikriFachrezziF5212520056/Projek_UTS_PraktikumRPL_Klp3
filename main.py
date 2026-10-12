import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))
import customtkinter as ctk
from views.login_view import LoginView
from views.dashboard_view import DashboardView
from views.laundry_view import LaundryView, _label, _tombol

JUDUL = "SIM Laundry - Sistem Informasi Manajemen Operasional Jasa Laundry"

# ---------------------------------------------------------------------------
# Palet mint: hijau kebiruan lembut yang menyiratkan kesegaran.
# Seluruh warna antarmuka diambil dari sini agar tampilan konsisten.
# ---------------------------------------------------------------------------
LATAR = "#eff9f6"        # latar halaman, mint sangat muda
SIDE = "#ffffff"         # sidebar
MINT = "#0d9488"         # warna utama
MINT_GELAP = "#0f766e"   # warna saat tombol ditekan
MINT_MUDA = "#ccfbf1"    # latar item menu yang sedang aktif
TEKS = "#0f3d38"         # teks utama
TEKS_LUNAK = "#5f8a84"   # teks keterangan
MERAH = "#f43f5e"        # tombol hapus


# ==================================================================
# UTILITAS
# ==================================================================
def terapkan_tema() -> None:
    """Mengatur tampilan terang dan tema warna bawaan."""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")


def buka_jendela_login() -> str:
    """
    Menampilkan jendela login lalu mengembalikan nama pengguna.

    Karena tombol masuk belum dihubungkan ke Controller, nama pengguna
    diambil dari apa yang diketik operator pada kolom username.
    """
    jendela = ctk.CTk(fg_color=LATAR)
    jendela.title("Login - SIM Laundry")
    jendela.geometry("880x620")
    jendela.resizable(False, False)

    view = LoginView(jendela)
    view.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)
    jendela.grid_rowconfigure(0, weight=1)
    jendela.grid_columnconfigure(0, weight=1)

    jendela.mainloop()

    # Bila jendela ditutup tanpa mengisi nama pengguna, aplikasi
    # dihentikan.
    if getattr(view, "pengguna_masuk", None) is None:
        raise SystemExit

    return view.pengguna_masuk


# ==================================================================
# JENDELA UTAMA
# ==================================================================
def _sidebar(bangunan, pengguna: str, aktif: str):
    """Membangun sidebar berisi logo, menu navigasi, dan kartu pengguna."""
    sisi = ctk.CTkFrame(bangunan, width=232, corner_radius=0,
                        fg_color=SIDE)
    sisi.pack(side="left", fill="y")
    sisi.grid_propagate(False)
    sisi.grid_columnconfigure(0, weight=1)
    sisi.grid_rowconfigure(5, weight=1)

    # --- Logo dan nama aplikasi ---
    _label(sisi, "\U0001F9FA", 0, 0, gaya={"font": ("Segoe UI", 30)},
           pady=(24, 0))
    _label(sisi, "SIM Laundry", 1, 0,
           gaya={"font": ("Segoe UI", 18, "bold"), "text_color": TEKS},
           pady=(4, 0))
    _label(sisi, "Manajemen Operasional\nJasa Laundry", 2, 0,
           gaya={"font": ("Segoe UI", 11), "text_color": TEKS_LUNAK,
                 "justify": "center"},
           pady=(2, 20))

    # --- Menu navigasi ---
    menu = {}
    for baris, (nama, ikon) in enumerate(
            (("Dashboard", "\U0001F4CA"), ("Transaksi Laundry", "\U0001F9FA")),
            start=3):
        terpilih = nama == aktif
        menu[nama] = _tombol(
            sisi, f"  {ikon}   {nama}", None, baris, 0,
            gaya={"anchor": "w", "corner_radius": 12, "height": 44,
                  "font": ("Segoe UI", 13, "bold"), "hover_color": MINT_MUDA,
                  "border_width": 0,
                  "fg_color": MINT_MUDA if terpilih else "transparent",
                  "text_color": MINT_GELAP if terpilih else TEKS},
            sticky="ew", padx=14, pady=4)

    # --- Kartu pengguna di bagian bawah ---
    kartu = ctk.CTkFrame(sisi, fg_color=LATAR, corner_radius=12)
    kartu.grid(row=6, column=0, sticky="ew", padx=14, pady=(0, 20))
    _label(kartu, "Pengguna", 0, 0,
           gaya={"font": ("Segoe UI", 10), "text_color": TEKS_LUNAK,
                 "anchor": "w"}).grid(sticky="ew", padx=12, pady=(8, 0))
    _label(kartu, pengguna, 1, 0,
           gaya={"font": ("Segoe UI", 13, "bold"), "text_color": TEKS,
                 "anchor": "w"}).grid(sticky="ew", padx=12, pady=(0, 8))
    _tombol(kartu, "Keluar", None, 2, 0,
            gaya={"height": 32, "corner_radius": 10, "fg_color": "transparent",
                  "border_width": 1, "border_color": MERAH,
                  "text_color": MERAH, "font": ("Segoe UI", 12, "bold")}
            ).grid(sticky="ew", padx=12, pady=(0, 10))

    return sisi, menu, kartu


def buka_jendela_utama(pengguna: str) -> None:
    """Menampilkan jendela utama yang memuat dashboard dan transaksi."""
    jendela = ctk.CTk(fg_color=LATAR)
    jendela.title(JUDUL)
    jendela.geometry("1260x780+20+20")
    jendela.minsize(1040, 620)

    _, menu, kartu = _sidebar(jendela, pengguna, "Dashboard")

    # --- Area konten di sebelah kanan sidebar ---
    konten = ctk.CTkFrame(jendela, fg_color=LATAR, corner_radius=0)
    konten.pack(side="right", fill="both", expand=True)
    konten.grid_rowconfigure(1, weight=1)
    konten.grid_columnconfigure(0, weight=1)

    _label(konten, "Selamat datang di Sistem Informasi "
                   "Manajemen Operasional Jasa Laundry", 0, 0,
           gaya={"font": ("Segoe UI", 12), "text_color": TEKS_LUNAK,
                 "anchor": "w"},
           sticky="ew", padx=22, pady=(18, 8))

    wadah = ctk.CTkFrame(konten, fg_color=LATAR)
    wadah.grid(row=1, column=0, sticky="nsew", padx=22, pady=(0, 18))
    wadah.grid_rowconfigure(0, weight=1)
    wadah.grid_columnconfigure(0, weight=1)

    # --- Dua View, ditumpuk dan ditampilkan sesuai menu yang dipilih ---
    view_dashboard = DashboardView(wadah, pengguna)
    view_transaksi = LaundryView(wadah)

    for tampilan in (view_dashboard, view_transaksi):
        tampilan.configure(fg_color=LATAR)
        tampilan.grid(row=0, column=0, sticky="nsew")

    # Tombol muat ulang mengikuti warna tema mint.
    view_dashboard.btn_refresh.configure(fg_color=MINT, hover_color=MINT_GELAP)
    view_transaksi.grid_rowconfigure(1, weight=1)
    view_transaksi.grid_columnconfigure(1, weight=1)

    def tampilkan(nama: str) -> None:
        """Menampilkan View sesuai menu yang dipilih."""
        for kunci, tombol in menu.items():
            terpilih = kunci == nama
            tombol.configure(
                fg_color=MINT_MUDA if terpilih else "transparent",
                text_color=MINT_GELAP if terpilih else TEKS,
            )
        if nama == "Dashboard":
            view_dashboard.tkraise()
        else:
            view_transaksi.tkraise()

    menu["Dashboard"].configure(command=lambda: tampilkan("Dashboard"))
    menu["Transaksi Laundry"].configure(
        command=lambda: tampilkan("Transaksi Laundry"))
    kartu.winfo_children()[-1].configure(command=jendela.destroy)

    tampilkan("Dashboard")
    jendela.mainloop()


# ==================================================================
# TITIK MASUK
# ==================================================================
def main() -> None:
    """Merakit seluruh tampilan lalu menjalankan aplikasi."""
    # 1. Tampilan bertema mint.
    terapkan_tema()
    # 2. Login lebih dahulu, baru jendela utama.
    try:
        pengguna = buka_jendela_login()
    except SystemExit:
        return

    buka_jendela_utama(pengguna)


if __name__ == "__main__":
    main()