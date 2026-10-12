"""
Antarmuka halaman Login.

Sesuai Modul 5, berkas ini berisi antarmuka statis. Kartu login sudah
tersusun rapi, tetapi belum dihubungkan ke Controller. Karena itu
tombol Masuk hanya memeriksa kolom kosong, tanpa memeriksa username
maupun password.

Jalankan berkas ini secara mandiri dengan:
    python views/login_view.py
"""

import customtkinter as ctk
from tkinter import messagebox

from views.laundry_view import _input, _label, _tombol, bind_event

# Warna halaman login.
PALET = {
    "kartu": "#ffffff",
    "aksen": "#0d9488",
    "aksen_muda": "#ccfbf1",
    "teks": "#0f3d38",
    "teks_lunak": "#5f8a84",
    "konsol": "#eff9f6",
    "salah": "#e11d48",
}

# Keterangan yang muncul ketika tombol Masuk ditekan.
PESAN_BELUM = ("Tombol ini belum berfungsi.\n\n"
               "Sesuai Modul 5, antarmuka pada tahap ini belum "
               "dihubungkan ke Controller.")


class LoginView(ctk.CTkFrame):
    """Kartu login berupa antarmuka statis."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.pengguna_masuk = None
        self.warna = PALET
        self.sandi_terlihat = False

        # Kartu dipusatkan dengan satu baris dan satu kolom berbobot penuh.
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build_kartu()
        self._build_kaki()

    # ==================================================================
    # KONSTRUKSI KOMPONEN
    # ==================================================================
    def _build_kartu(self) -> None:
        w = self.warna

        # Gaya bersama supaya setiap baris formulir tetap seragam.
        isi = {"height": 42, "corner_radius": 10, "border_width": 1,
               "fg_color": "#ffffff", "text_color": w["teks"],
               "placeholder_text_color": w["teks_lunak"]}
        judul = {"font": ("Segoe UI", 12, "bold"), "text_color": w["teks"],
                 "anchor": "w"}

        self.kartu = ctk.CTkFrame(self, fg_color=w["kartu"], corner_radius=20,
                                  width=470)
        kartu = self.kartu
        kartu.grid(row=0, column=0, padx=24, pady=(20, 6))
        kartu.grid_columnconfigure(0, weight=1)

        # --- Kepala kartu: blok hijau berisi ikon dan nama aplikasi ---
        kepala = ctk.CTkFrame(kartu, fg_color=w["aksen"], corner_radius=14)
        kepala.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 0))
        # Kolom 1 (judul) yang melar, lencana tetap rata kiri.
        kepala.grid_columnconfigure(1, weight=1)

        # Lencana berisi ikon keranjang, memberi kesan aplikasi laundry.
        lencana = ctk.CTkFrame(kepala, fg_color=w["aksen_muda"],
                               width=56, height=56, corner_radius=16)
        lencana.grid(row=0, column=0, rowspan=2, padx=(16, 0), pady=16)
        lencana.grid_propagate(False)
        _label(lencana, "\U0001F9FA", 0, 0,
               gaya={"font": ("Segoe UI", 26)})

        _label(kepala, "SIM Laundry", 0, 1,
               gaya={"font": ("Segoe UI", 22, "bold"),
                     "text_color": "#ffffff", "anchor": "w"},
               sticky="sw", padx=(14, 16), pady=(18, 0))
        _label(kepala, "Sistem Informasi Manajemen Operasional\nJasa Laundry",
               1, 1,
               gaya={"font": ("Segoe UI", 11), "text_color": "#d6e4ff",
                     "justify": "left", "anchor": "w"},
               sticky="nw", padx=(14, 16), pady=(2, 18))

        # --- Judul formulir ---
        _label(kartu, "Masuk", 1, 0,
               gaya={"font": ("Segoe UI", 18, "bold"),
                     "text_color": w["teks"], "anchor": "w"},
               sticky="ew", padx=28, pady=(22, 0))
        _label(kartu, "Gunakan akun operator untuk masuk.", 2, 0,
               gaya={"font": ("Segoe UI", 12), "text_color": w["teks_lunak"],
                     "anchor": "w"},
               sticky="ew", padx=28, pady=(0, 14))

        # --- Kolom username ---
        _label(kartu, "Username", 3, 0, gaya=judul,
               sticky="ew", padx=28, pady=(0, 4))
        self.entry_username = _input(
            kartu, ctk.CTkEntry, 4, 0,
            gaya={**isi, "placeholder_text": "Masukkan username",
                  "width": 420},
            sticky="ew", padx=28, pady=(0, 12))

        # --- Kolom password beserta tombol untuk menampilkan sandi ---
        _label(kartu, "Password", 5, 0, gaya=judul,
               sticky="ew", padx=28, pady=(0, 4))

        # Kolom sandi dan tombol "Lihat" berdampingan; kolom sandi tetap
        # melebar sehingga panjangnya sama dengan kolom username.
        bungkus = ctk.CTkFrame(kartu, fg_color="transparent")
        bungkus.grid(row=6, column=0, sticky="ew", padx=28, pady=(0, 6))
        bungkus.grid_columnconfigure(0, weight=1)

        self.entry_password = _input(
            bungkus, ctk.CTkEntry, 0, 0,
            gaya={**isi, "placeholder_text": "Masukkan password",
                  "show": "*"},
            sticky="ew")
        self.btn_lihat = _tombol(
            bungkus, "Lihat", self._tampilkan_sandi, 0, 1,
            gaya={"width": 66, "height": 42, "corner_radius": 10,
                  "fg_color": w["aksen_muda"], "text_color": w["aksen"],
                  "hover_color": w["aksen"],
                  "font": ("Segoe UI", 12, "bold")},
            padx=(8, 0))

        # --- Baris pesan kesalahan; selalu ada agar tampilan tidak melompat
        self.label_salah = _label(
            kartu, "", 7, 0,
            gaya={"font": ("Segoe UI", 11, "bold"), "text_color": w["salah"],
                  "anchor": "w"},
            sticky="ew", padx=28, pady=(0, 4))

        # --- Tombol masuk ---
        self.btn_masuk = _tombol(
            kartu, "Masuk", self._aksi_masuk, 8, 0,
            gaya={"height": 44, "corner_radius": 10, "fg_color": w["aksen"],
                  "hover_color": "#0f766e", "text_color": "#ffffff",
                  "font": ("Segoe UI", 14, "bold")},
            sticky="ew", padx=28, pady=(0, 16))

        # --- Kotak informasi: tombol belum terhubung ke Controller ---
        info = ctk.CTkFrame(kartu, fg_color=w["konsol"], corner_radius=12)
        info.grid(row=9, column=0, sticky="ew", padx=28, pady=(0, 20))
        info.grid_columnconfigure(1, weight=1)

        _label(info, "Catatan", 0, 0,
               gaya={"font": ("Segoe UI", 11, "bold"),
                     "text_color": w["teks"], "anchor": "w"},
               sticky="w", padx=(14, 8), pady=12)
        _label(info, "Tombol belum berfungsi", 0, 1,
               gaya={"font": ("Consolas", 11), "text_color": w["teks_lunak"],
                     "anchor": "e"},
               sticky="e", padx=(8, 14), pady=12)

        # Tekan Enter untuk memproses isian.
        masuk = lambda _e: self._aksi_masuk()          # noqa: E731
        bind_event(self.entry_username, "<Return>", masuk)
        bind_event(self.entry_password, "<Return>", masuk)

        # Fokus diarahkan setelah jendela selesai digambar.
        self.after(250, self.entry_username.focus_set)

    def _build_kaki(self) -> None:
        _label(self, "Kelompok 3  \u00b7  Program Studi Sistem Informasi  \u00b7  "
                     "Fakultas Teknik \u2013 Universitas Tadulako", 1, 0,
               gaya={"font": ("Segoe UI", 11),
                     "text_color": self.warna["teks_lunak"]},
               sticky="ew", padx=24, pady=(0, 14))

    # ==================================================================
    # AKSI TOMBOL
    # ==================================================================
    def _tampilkan_sandi(self) -> None:
        """Menampilkan atau menyembunyikan isi kolom sandi."""
        self.sandi_terlihat = not self.sandi_terlihat
        self.entry_password.configure(show="" if self.sandi_terlihat else "*")
        self.btn_lihat.configure(
            text="Tutup" if self.sandi_terlihat else "Lihat",
            fg_color=self.warna["aksen"] if self.sandi_terlihat
            else self.warna["aksen_muda"],
            text_color="#ffffff" if self.sandi_terlihat
            else self.warna["aksen"],
        )

    def _aksi_masuk(self) -> None:
        """Memeriksa kolom kosong, tombol belum terhubung ke Controller."""
        # Pesan lama dibersihkan agar tidak menumpuk saat mencoba lagi.
        self.label_salah.configure(text="")

        if not self.entry_username.get().strip():
            self.label_salah.configure(
                text="Kolom username belum diisi.")
            self.entry_username.focus_set()
            return

        if not self.entry_password.get():
            self.label_salah.configure(
                text="Kolom password belum diisi.")
            self.entry_password.delete(0, "end")
            self.entry_password.focus_set()
            return

        self.pengguna_masuk = self.entry_username.get().strip()
        self._tampilkan_pesan()

    def _tampilkan_pesan(self) -> None:
        """Menampilkan keterangan bahwa tombol belum berfungsi."""
        messagebox.showinfo("Informasi", PESAN_BELUM,
                           parent=self.winfo_toplevel())


if __name__ == "__main__":
    # Pengujian antarmuka secara mandiri sesuai langkah pada Modul 5.
    ctk.set_appearance_mode("light")
    jendela = ctk.CTk(fg_color="#eff9f6")
    jendela.title("Login - SIM Laundry")
    jendela.geometry("880x620")
    jendela.resizable(False, False)
    jendela.grid_rowconfigure(0, weight=1)
    jendela.grid_columnconfigure(0, weight=1)

    tampilan = LoginView(jendela)
    tampilan.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

    jendela.mainloop()