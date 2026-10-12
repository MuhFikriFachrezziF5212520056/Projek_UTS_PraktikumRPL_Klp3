"""
Antarmuka halaman Transaksi Laundry.

Sesuai Modul 5, berkas ini berisi antarmuka statis. Form, tombol, dan
tabel sudah tersusun rapi, tetapi belum dihubungkan ke Controller.
Karena itu tombol Simpan, Perbarui, dan Hapus hanya menampilkan
keterangan bahwa tombol tersebut belum berfungsi.

Isi tabel dan daftar pilihan diambil dari data contoh di bawah, bukan
dari basis data. Model pada folder models tetap tersedia dan tidak
diubah oleh berkas ini.

Jalankan berkas ini secara mandiri dengan:
    python views/laundry_view.py
"""

from datetime import date

import customtkinter as ctk
from tkinter import ttk, messagebox

# ==================================================================
# DATA CONTOH
#
# Hanya untuk mengisi tampilan. Tidak pernah dikirim ke basis data.
# ==================================================================
DATA_PELANGGAN = [
    {"nama": "Heather", "no_telp": "082637261726", "alamat": "Tondo"},
    {"nama": "Fikri", "no_telp": "081125456756", "alamat": "Palu"},
    {"nama": "Muh", "no_telp": "081122435576", "alamat": "Arab"},
    {"nama": "Rusli", "no_telp": "081333444555", "alamat": "Manado"},
    {"nama": "Sinta", "no_telp": "081444555666", "alamat": "Gorontalo"},
]

DATA_PAKET = [
    {"nama": "Cuci Kering", "jenis": "Cuci Kering", "harga": 7000},
    {"nama": "Cuci Basah", "jenis": "Cuci Basah", "harga": 8000},
    {"nama": "Pembersihan Karpet", "jenis": "Pembersihan Karpet",
     "harga": 15000},
    {"nama": "Setrika", "jenis": "Setrika", "harga": 5000},
]

DATA_TRANSAKSI = [
    {"id": 1, "pelanggan": "Heather", "telp": "082637261726",
     "paket": "Cuci Kering", "berat": 5, "total": 35000, "status": "Selesai"},
    {"id": 2, "pelanggan": "Fikri", "telp": "081125456756",
     "paket": "Setrika", "berat": 4, "total": 20000, "status": "Proses"},
    {"id": 3, "pelanggan": "Muh", "telp": "081122435576",
     "paket": "Cuci Basah", "berat": 6, "total": 48000, "status": "Antrean"},
    {"id": 4, "pelanggan": "Rusli", "telp": "081333444555",
     "paket": "Pembersihan Karpet", "berat": 3, "total": 45000,
     "status": "Selesai"},
    {"id": 5, "pelanggan": "Sinta", "telp": "081444555666",
     "paket": "Cuci Kering", "berat": 7, "total": 49000, "status": "Diambil"},
]

STATUS_CUCIAN = ["Antrean", "Proses", "Selesai", "Diambil"]

# Keterangan yang muncul ketika tombol ditekan.
PESAN_BELUM = ("Tombol ini belum berfungsi.\n\n"
               "Sesuai Modul 5, antarmuka pada tahap ini belum "
               "dihubungkan ke Controller.")


# ==================================================================
# HELPER TAMPILAN
# ==================================================================
# Warna dasar tampilan. Dipakai bersama oleh ketiga view agar
# kartunya tidak perlu diwarnai ulang dari main.py.
WARNA_KARTU = "#ffffff"

# Palet tabel agar senada dengan tema terang.
_TERANG = {"bg": "#ffffff", "fg": "#1a1a1a", "head_bg": "#e6e6e6",
           "head_fg": "#1a1a1a", "sel_bg": "#1f6aa5"}


def _gaya_tabel() -> None:
    """Menyesuaikan warna tabel dengan tema terang."""
    p = _TERANG
    gaya = ttk.Style()
    try:
        gaya.theme_use("clam")
    except Exception:  # noqa: BLE001
        pass

    gaya.configure("Laundry.Treeview", background=p["bg"],
                   fieldbackground=p["bg"], foreground=p["fg"],
                   rowheight=26, borderwidth=0)
    gaya.configure("Laundry.Treeview.Heading", background=p["head_bg"],
                   foreground=p["head_fg"], relief="flat", padding=(6, 6))
    gaya.map("Laundry.Treeview",
             background=[("selected", p["sel_bg"])],
             foreground=[("selected", "#ffffff")])
    gaya.configure("Laundry.Vertical.TScrollbar", background=p["head_bg"],
                   troughcolor=p["bg"], bordercolor=p["bg"],
                   arrowcolor=p["fg"])


def bind_event(widget, event: str, fungsi) -> None:
    """Mengikat kejadian pada bagian dalam widget customtkinter."""
    internal = getattr(widget, "_entry", None)
    if internal is not None:
        internal.bind(event, fungsi)


def _tanggal_hari_ini() -> str:
    """Mengembalikan tanggal hari ini dalam format tahun-bulan-hari."""
    return date.today().isoformat()


def _rp(nilai) -> str:
    """Mengubah angka menjadi teks bergaya Rupiah."""
    return f"Rp {float(nilai or 0):,.0f}".replace(",", ".")


def _label(bapak, teks, baris=0, kolom=0, *, gaya=None, **tempat):
    """Menempatkan satu label ke dalam wadah."""
    label = ctk.CTkLabel(bapak, text=teks, **(gaya or {}))
    label.grid(row=baris, column=kolom, **tempat)
    return label


def _input(bapak, kelas, baris=0, kolom=0, *, gaya=None, **tempat):
    """Menempatkan widget isian, yaitu kolom teks atau kotak pilihan."""
    widget = kelas(bapak, **(gaya or {}))
    widget.grid(row=baris, column=kolom, **tempat)
    return widget


def _tombol(bapak, teks, perintah=None, baris=0, kolom=0, *, gaya=None,
            **tempat):
    """Menempatkan satu tombol ke dalam wadah."""
    tombol = ctk.CTkButton(bapak, text=teks, command=perintah,
                           **(gaya or {}))
    tombol.grid(row=baris, column=kolom, **tempat)
    return tombol


def _tabel(bapak, kolom, *, baris=1, tinggi=3):
    """
    Membuat tabel beserta judul dan lebar kolomnya.

    Setiap isi kolom berbentuk (nama, judul, lebar, jangkar). Kolom yang
    rata kiri ikut melar mengikuti lebar jendela, selain itu lebarnya
    dikunci supaya tabel tidak bergeser.
    """
    pohon = ttk.Treeview(bapak, columns=tuple(k for k, _j, _l, _a in kolom),
                          show="headings", height=tinggi,
                          style="Laundry.Treeview")
    for kunci, teks, lebar, jangkar in kolom:
        pohon.heading(kunci, text=teks)
        pohon.column(kunci, width=lebar, anchor=jangkar,
                      stretch=jangkar == "w")
    pohon.grid(row=baris, column=0, sticky="nsew", padx=10, pady=(4, 10))
    return pohon


def _isi(kolom, teks) -> None:
    """Mengosongkan lalu mengisi satu kolom isian dalam satu perintah."""
    kolom.delete(0, "end")
    if teks not in (None, ""):
        kolom.insert(0, str(teks))


# ==================================================================
# ANTARMUKA TRANSAKSI
# ==================================================================
class LaundryView(ctk.CTkFrame):
    """Halaman transaksi laundry berupa antarmuka statis."""

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        _gaya_tabel()
        self._build_form()
        self._build_tabel()
        self.muat_data_contoh()
        self.muat_daftar()

    # ==================================================================
    # FORM TRANSAKSI
    # ==================================================================
    def _build_form(self) -> None:
        # Dua label sisi form memakai jarak kiri berbeda supaya kolom
        # kiri dan kanan tidak saling menempel.
        def label_kiri(teks, baris):
            _label(form, teks, baris, 0, sticky="w", padx=(10, 4), pady=2)

        def label_kanan(teks, baris):
            _label(form, teks, baris, 2, sticky="w", padx=(12, 4), pady=2)

        _label(self, "Form Transaksi Laundry", 0, 0, columnspan=5,
               gaya={"font": ("Segoe UI", 14, "bold"), "anchor": "w"},
               sticky="w", pady=(0, 6))

        self.frame_form = ctk.CTkFrame(self, fg_color=WARNA_KARTU,
                                      corner_radius=14)
        form = self.frame_form
        form.grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        form.grid_columnconfigure(0, weight=3)
        form.grid_columnconfigure(2, weight=3)

        merah = {"fg_color": "#b3261e", "hover_color": "#8f1e18"}
        kecil = {"width": 58, "height": 28}

        # --- Baris 1: Pelanggan dan Paket Layanan ---
        label_kiri("Pelanggan", 0)
        label_kanan("Paket Layanan", 0)

        # state="normal" supaya operator bebas mengetik nama baru.
        self.combo_pelanggan = _input(
            form, ctk.CTkComboBox, 1, 0,
            gaya={"state": "normal", "values": ["-"]},
            sticky="ew", padx=(10, 4), pady=2)
        bind_event(self.combo_pelanggan, "<KeyRelease>",
                   self._pelanggan_diubah)

        self.btn_hapus_pelanggan = _tombol(
            form, "Hapus", self._belum_terhubung, 1, 1,
            gaya={**kecil, **merah}, padx=(0, 12), pady=2)

        self.combo_paket = _input(
            form, ctk.CTkComboBox, 1, 2,
            gaya={"state": "readonly", "values": ["-"]},
            sticky="ew", padx=(12, 4), pady=2)

        self.btn_tambah_paket = _tombol(
            form, "+ Paket", self._buka_dialog_paket, 1, 3,
            gaya=kecil, padx=4, pady=2)

        self.btn_hapus_paket = _tombol(
            form, "Hapus", self._belum_terhubung, 1, 4,
            gaya={**kecil, **merah}, padx=(4, 10), pady=2)

        # --- Baris 2: Nomor Telepon dan Alamat pelanggan ---
        label_kiri("No. Telepon", 2)
        label_kanan("Alamat", 2)
        self.entry_telp = _input(form, ctk.CTkEntry, 3, 0,
                                 gaya={"placeholder_text": "08xxxxxxxxxx"},
                                 sticky="ew", padx=(10, 12), pady=2)
        self.entry_alamat = _input(form, ctk.CTkEntry, 3, 2, columnspan=3,
                                   gaya={"placeholder_text":
                                         "Alamat lengkap pelanggan"},
                                   sticky="ew", padx=(12, 10), pady=2)

        # --- Baris 3: Berat dan Status Cucian ---
        label_kiri("Berat (Kg)", 4)
        label_kanan("Status Cucian", 4)
        self.entry_berat = _input(form, ctk.CTkEntry, 5, 0,
                                  gaya={"placeholder_text": "Contoh: 3.5"},
                                  sticky="ew", padx=(10, 12), pady=2)
        bind_event(self.entry_berat, "<KeyRelease>",
                   lambda _e: self._hitung_total())
        self.combo_status = _input(form, ctk.CTkComboBox, 5, 2, columnspan=3,
                                   gaya={"state": "readonly",
                                         "values": STATUS_CUCIAN},
                                   sticky="ew", padx=(12, 10), pady=2)

        # --- Baris 4: Tanggal Terima dan Tanggal Selesai ---
        label_kiri("Tanggal Terima", 6)
        label_kanan("Tanggal Selesai", 6)
        self.entry_terima = _input(form, ctk.CTkEntry, 7, 0,
                                   gaya={"placeholder_text": "YYYY-MM-DD"},
                                   sticky="ew", padx=(10, 12), pady=2)
        self.entry_selesai = _input(form, ctk.CTkEntry, 7, 2, columnspan=3,
                                    gaya={"placeholder_text":
                                          "YYYY-MM-DD (opsional)"},
                                    sticky="ew", padx=(12, 10), pady=2)

        self.label_total = _label(form, "Total Biaya: Rp 0", 8, 0,
                                  columnspan=5,
                                  gaya={"font": ("Segoe UI", 14, "bold")},
                                  sticky="w", padx=10, pady=(12, 2))

        # --- Tombol aksi utama ---
        tombol = ctk.CTkFrame(form, fg_color="transparent")
        tombol.grid(row=9, column=0, columnspan=5, sticky="ew",
                    padx=10, pady=(6, 12))
        tombol.grid_columnconfigure((0, 1, 2), weight=1)

        aksi = {"height": 34}
        _tombol(tombol, "Simpan Data", self._belum_terhubung, 0, 0,
                gaya=aksi, sticky="ew", padx=(0, 4))
        _tombol(tombol, "Perbarui", self._belum_terhubung, 0, 1,
                gaya={**aksi, "fg_color": "#1f6aa5"}, sticky="ew", padx=4)
        _tombol(tombol, "Hapus", self._belum_terhubung, 0, 2,
                gaya={**aksi, **merah}, sticky="ew", padx=(4, 0))

    # ==================================================================
    # TABEL TRANSAKSI
    # ==================================================================
    def _build_tabel(self) -> None:
        _label(self, "Daftar Transaksi", 0, 1,
               gaya={"font": ("Segoe UI", 14, "bold"), "anchor": "w"},
               sticky="w", pady=(0, 6))

        self.frame_tabel = ctk.CTkFrame(self, fg_color=WARNA_KARTU,
                                       corner_radius=14)
        bingkai = self.frame_tabel
        bingkai.grid(row=1, column=1, sticky="nsew")
        bingkai.grid_rowconfigure(1, weight=1)
        bingkai.grid_columnconfigure(0, weight=1)

        self.tree = _tabel(bingkai, (
            ("id", "ID", 45, "center"),
            ("pelanggan", "Pelanggan", 150, "w"),
            ("paket", "Paket", 120, "w"),
            ("berat", "Berat", 70, "e"),
            ("total", "Total Biaya", 110, "e"),
            ("status", "Status", 90, "center"),
        ), tinggi=14)
        self.tree.bind("<<TreeviewSelect>>", self._baris_dipilih)

        scroll = ttk.Scrollbar(bingkai, orient="vertical",
                               command=self.tree.yview,
                               style="Laundry.Vertical.TScrollbar")
        scroll.grid(row=1, column=1, sticky="ns", padx=(0, 10), pady=(4, 6))
        self.tree.configure(yscrollcommand=scroll.set)

        _tombol(bingkai, "Muat Ulang Tampilan", self.muat_daftar, 2, 0,
                columnspan=2, gaya={"height": 28, "fg_color": "transparent",
                                    "border_width": 1,
                                    "text_color": "gray"},
                sticky="ew", padx=10, pady=(0, 10))

    # ==================================================================
    # PENGISIAN DARI DATA CONTOH
    # ==================================================================
    def muat_data_contoh(self) -> None:
        """Mengisi daftar pilihan dengan isi data contoh."""
        nama = [d["nama"] for d in DATA_PELANGGAN] or ["-"]
        self.combo_pelanggan.configure(values=nama)
        self.combo_pelanggan.set(nama[0])

        paket = [d["nama"] for d in DATA_PAKET] or ["-"]
        self.combo_paket.configure(values=paket)
        self.combo_paket.set(paket[0])

        self.combo_status.configure(values=STATUS_CUCIAN)
        self.combo_status.set(STATUS_CUCIAN[0])

        self._isi_tanggal_default()
        self._isi_kontak()

    def muat_daftar(self) -> None:
        """Mengisi tabel dengan data contoh transaksi."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for baris in DATA_TRANSAKSI:
            self.tree.insert("", "end", values=(
                baris["id"],
                baris["pelanggan"],
                baris["paket"],
                f"{baris['berat']:g} kg",
                _rp(baris["total"]),
                baris["status"],
            ))

    def _baris_dipilih(self, _event=None) -> None:
        """Menyalin isi baris tabel yang dipilih ke dalam form."""
        pilihan = self.tree.selection()
        if not pilihan:
            return

        id_terpilih = self.tree.item(pilihan[0], "values")[0]
        for baris in DATA_TRANSAKSI:
            if str(baris["id"]) != str(id_terpilih):
                continue
            self.combo_pelanggan.set(baris["pelanggan"])
            self._isi_kontak()
            self.combo_paket.set(baris["paket"])
            _isi(self.entry_berat, f"{baris['berat']:g}")
            _isi(self.entry_telp, baris["telp"])
            self.combo_status.set(baris["status"])
            self._hitung_total()
            break

    # ==================================================================
    # PENGISIAN FORM
    # ==================================================================
    def _isi_tanggal_default(self) -> None:
        """Mengisi tanggal terima dengan hari ini bila kolom masih kosong."""
        if not self.entry_terima.get().strip():
            _isi(self.entry_terima, _tanggal_hari_ini())

    def _pelanggan_diubah(self, _event=None) -> None:
        """Menampilkan kontak pelanggan contoh sesuai nama yang diketik."""
        self._isi_tanggal_default()
        self._isi_kontak()
        self._hitung_total()

    def _isi_kontak(self) -> None:
        """Mengisi kolom telepon dan alamat dari daftar data contoh."""
        target = self.combo_pelanggan.get().strip().lower()
        for orang in DATA_PELANGGAN:
            if orang["nama"].strip().lower() == target:
                _isi(self.entry_telp, orang["no_telp"])
                _isi(self.entry_alamat, orang["alamat"])
                return
        _isi(self.entry_telp, "")
        _isi(self.entry_alamat, "")

    def _hitung_total(self) -> None:
        """Menampilkan perkalian berat dengan harga paket contoh."""
        harga = 0
        for paket in DATA_PAKET:
            if paket["nama"] == self.combo_paket.get():
                harga = paket["harga"]
                break
        try:
            berat = float(self.entry_berat.get().strip() or 0)
        except ValueError:
            berat = 0
        self.label_total.configure(text=f"Total Biaya: {_rp(berat * harga)}")

    # ==================================================================
    # DIALOG TAMBAH PAKET
    # ==================================================================
    def _buka_dialog_paket(self) -> None:
        """Menampilkan jendela kecil berisi isian paket layanan."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Tambah Paket Layanan")
        dialog.geometry("360x230")
        dialog.resizable(False, False)
        dialog.transient(self.winfo_toplevel())

        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=18, pady=16)
        frame.grid_columnconfigure(1, weight=1)

        def label(teks, baris):
            _label(frame, teks, baris, 0, gaya={"anchor": "w"},
                   sticky="w", pady=(0, 2))

        label("Nama Paket", 0)
        entry_nama = _input(frame, ctk.CTkEntry, 1, 0, columnspan=2,
                            gaya={"placeholder_text": "Contoh: Cuci Kilat"},
                            sticky="ew", pady=(0, 10))

        label("Jenis Layanan", 2)
        combo_jenis = _input(frame, ctk.CTkComboBox, 3, 0, columnspan=2,
                             gaya={"state": "normal",
                                   "values": ["Cuci Kering", "Cuci Basah",
                                              "Setrika",
                                              "Pembersihan Karpet", "Lipat"]},
                             sticky="ew", pady=(0, 10))
        combo_jenis.set("Cuci Kering")

        label("Harga per Kg (Rp)", 4)
        _input(frame, ctk.CTkEntry, 5, 0, columnspan=2,
               gaya={"placeholder_text": "Contoh: 7500"},
               sticky="ew", pady=(0, 14))

        def tutup(_event=None):
            messagebox.showinfo("Informasi", PESAN_BELUM, parent=dialog)
            dialog.destroy()

        tombol = ctk.CTkFrame(frame, fg_color="transparent")
        tombol.grid(row=6, column=0, columnspan=2, sticky="ew")
        tombol.grid_columnconfigure((0, 1), weight=1)
        _tombol(tombol, "Batal", dialog.destroy, 0, 0,
                gaya={"height": 32, "fg_color": "transparent",
                      "border_width": 1, "text_color": "gray"},
                sticky="ew", padx=(0, 4))
        _tombol(tombol, "Simpan Paket", tutup, 0, 1,
                gaya={"height": 32}, sticky="ew", padx=(4, 0))

        entry_nama.focus_set()
        bind_event(entry_nama, "<Return>", tutup)

    # ==================================================================
    # TOMBOL YANG BELUM TERHUBUNG
    # ==================================================================
    def _belum_terhubung(self) -> None:
        """Menampilkan keterangan bahwa tombol belum berfungsi."""
        messagebox.showinfo("Informasi", PESAN_BELUM, parent=self)


if __name__ == "__main__":
    # Pengujian antarmuka secara mandiri sesuai langkah pada Modul 5.
    ctk.set_appearance_mode("light")
    jendela = ctk.CTk()
    jendela.title("Halaman Transaksi Laundry")
    jendela.geometry("1180x760")
    jendela.grid_rowconfigure(0, weight=1)
    jendela.grid_columnconfigure(0, weight=1)

    tampilan = LaundryView(jendela)
    tampilan.grid(row=0, column=0, sticky="nsew")
    tampilan.grid_rowconfigure(1, weight=1)
    tampilan.grid_columnconfigure(1, weight=1)

    jendela.mainloop()