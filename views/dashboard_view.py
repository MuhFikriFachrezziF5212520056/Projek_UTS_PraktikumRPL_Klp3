from datetime import datetime
import customtkinter as ctk
from tkinter import ttk
from views.laundry_view import _gaya_tabel, _label, _tombol, _tabel

# Pasangan label status cucian dengan kunci ringkasan pada Model.
STATUS_BARIS = (
    ("Antrean", "st_antrean"),
    ("Proses", "st_proses"),
    ("Selesai", "st_selesai"),
    ("Diambil", "st_diambil"),
)

def _rp(nilai) -> str:
    return f"Rp {float(nilai or 0):,.0f}".replace(",", ".")
def _angka(nilai) -> str:
    return f"{float(nilai or 0):g}".replace(".", ",")

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, controller, nama_pengguna: str = "operator"):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.nama_pengguna = nama_pengguna

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(4, weight=3)
        self.grid_rowconfigure(6, weight=2)

        _gaya_tabel(ctk.get_appearance_mode())
        self._build_sapaan()
        self._build_kartu()
        self._build_panel_kontak()
        self._build_panel_status()
        self._build_panel_terbaru()
        self.muat_data()

    # ==================================================================
    # konstruksi komponen
    # ==================================================================
    def _build_sapaan(self) -> None:
        tebal = {"font": ("Segoe UI", 20, "bold"), "anchor": "w"}
        self.label_sapaan = _label(self, f"Halo, {self.nama_pengguna}!",
                                  0, 0, columnspan=3, gaya=tebal,
                                  sticky="w", pady=(0, 2))

        # Tombol refresh agar angka ringkasan dapat disegarkan tanpa
        # harus menutup lalu menjalankan ulang aplikasi.
        self.btn_refresh = _tombol(
            self, "\u21bb  Refresh", self.muat_data, 0, 3,
            gaya={"width": 110, "height": 34, "corner_radius": 12},
            sticky="e")

        abu = {"text_color": "gray", "anchor": "w"}
        self.label_subjudul = _label(
            self, "Ringkasan operasional jasa laundry.", 1, 0,
            columnspan=3, gaya={**abu, "font": ("Segoe UI", 12)},
            sticky="w", pady=(0, 14))

        # Menampilkan jam saat data terakhir diambil dari basis data.
        self.label_waktu = _label(self, "", 1, 3,
                                  gaya={"text_color": "gray",
                                        "anchor": "e",
                                        "font": ("Segoe UI", 10)},
                                  sticky="e", pady=(0, 14))

    def _build_kartu(self) -> None:
        self.frame_kartu = ctk.CTkFrame(self, fg_color="transparent")
        kartu = self.frame_kartu
        kartu.grid(row=2, column=0, columnspan=4, sticky="ew")
        for kolom in range(4):
            kartu.grid_columnconfigure(kolom, weight=1)

        self.frame_kartu_isi = []
        self.label_pelanggan = self._satu_kartu(
            0, "Pelanggan", "Jumlah pelanggan terdaftar")
        self.label_paket = self._satu_kartu(
            1, "Paket Layanan", "Katalog layanan tersedia")
        self.label_transaksi = self._satu_kartu(
            2, "Transaksi", "Total transaksi laundry")
        self.label_pendapatan = self._satu_kartu(
            3, "Total Pendapatan", "Akumulasi seluruh transaksi")

    def _satu_kartu(self, kolom, judul, keterangan) -> ctk.CTkLabel:
        bingkai = ctk.CTkFrame(self.frame_kartu, corner_radius=14)
        bingkai.grid(row=0, column=kolom, sticky="nsew",
                     padx=(0 if kolom == 0 else 5, 5))
        self.frame_kartu_isi.append(bingkai)

        abu = {"text_color": "gray", "anchor": "w"}
        _label(bingkai, judul, 0, 0,
               gaya={**abu, "font": ("Segoe UI", 12)},
               sticky="ew", padx=14, pady=(12, 0))
        nilai = _label(bingkai, "0", 1, 0,
                       gaya={"font": ("Segoe UI", 22, "bold"),
                             "anchor": "w"},
                       sticky="ew", padx=14)
        _label(bingkai, keterangan, 2, 0,
               gaya={**abu, "font": ("Segoe UI", 10)},
               sticky="ew", padx=14, pady=(0, 12))
        return nilai

    def _build_panel_kontak(self) -> None:
        _label(self, "Kontak Pelanggan", 3, 0, columnspan=2,
               gaya={"font": ("Segoe UI", 14, "bold"), "anchor": "w"},
               sticky="w", pady=(0, 6))

        # Ringkasan kelengkapan data kontak di sisi kanan judul.
        abu = {"text_color": "gray", "anchor": "e"}
        self.label_kontak_info = _label(self, "", 3, 2, columnspan=2,
                                        gaya={**abu,
                                              "font": ("Segoe UI", 11)},
                                        sticky="e", padx=(0, 8), pady=(0, 6))

        self.frame_kontak = ctk.CTkFrame(self)
        bingkai = self.frame_kontak
        bingkai.grid(row=4, column=0, columnspan=4, sticky="nsew")
        bingkai.grid_rowconfigure(1, weight=1)
        bingkai.grid_columnconfigure(0, weight=1)

        self.tree_kontak = _tabel(bingkai, (
            ("nama", "Nama Pelanggan", 150, "w"),
            ("telp", "No. Telepon", 140, "w"),
            ("alamat", "Alamat", 260, "w"),
            ("trx", "Transaksi", 95, "center"),
            ("belanja", "Total Belanja", 130, "e"),
        ))

    def _build_panel_status(self) -> None:
        _label(self, "Status Cucian", 5, 0, columnspan=2,
               gaya={"font": ("Segoe UI", 14, "bold"), "anchor": "w"},
               sticky="w", padx=(0, 12), pady=(18, 6))

        self.frame_status = ctk.CTkFrame(self)
        bingkai = self.frame_status
        bingkai.grid(row=6, column=0, columnspan=2, sticky="nsew")
        # Kolom 1 (batang) yang melar, kolom label dan jumlah tetap.
        bingkai.grid_columnconfigure(1, weight=1)
        # Baris terakhir jadi penahan, sehingga kaki panel menempel bawah.
        bingkai.grid_rowconfigure(len(STATUS_BARIS), weight=1)

        self.bar_status = {}
        for nomor, (nama, kunci) in enumerate(STATUS_BARIS):
            _label(bingkai, nama, nomor, 0,
                   gaya={"font": ("Segoe UI", 12), "width": 72,
                         "anchor": "w"},
                   sticky="w", padx=(14, 4), pady=(11, 2))
            batang = ctk.CTkProgressBar(bingkai, height=13, corner_radius=7)
            batang.grid(row=nomor, column=1, sticky="ew",
                        padx=4, pady=(11, 2))
            batang.set(0)
            jumlah = _label(bingkai, "0", nomor, 2,
                            gaya={"font": ("Segoe UI", 13, "bold"),
                                  "width": 34, "anchor": "e"},
                            sticky="e", padx=(4, 14), pady=(11, 2))
            self.bar_status[kunci] = (batang, jumlah)

        self.label_total_cucian = _label(
            bingkai, "Belum ada cucian tercatat.", len(STATUS_BARIS), 0,
            columnspan=3,
            gaya={"font": ("Segoe UI", 11), "text_color": "gray",
                  "anchor": "w"},
            sticky="sw", padx=14, pady=(6, 14))

    def _build_panel_terbaru(self) -> None:
        _label(self, "Transaksi Terbaru", 5, 2,
               gaya={"font": ("Segoe UI", 14, "bold"), "anchor": "w"},
               sticky="w", pady=(18, 6))

        # Akumulasi berat dicantumkan di sisi kanan judul tabel.
        abu = {"font": ("Segoe UI", 11), "text_color": "gray", "anchor": "e"}
        self.label_berat = _label(self, "", 5, 3, gaya=abu,
                                  sticky="e", padx=(0, 8), pady=(18, 6))

        self.frame_terbaru = ctk.CTkFrame(self)
        bingkai = self.frame_terbaru
        bingkai.grid(row=6, column=2, columnspan=2, sticky="nsew")
        bingkai.grid_rowconfigure(1, weight=1)
        bingkai.grid_columnconfigure(0, weight=1)

        self.tree_terbaru = _tabel(bingkai, (
            ("id", "ID", 40, "center"),
            ("pelanggan", "Pelanggan", 110, "w"),
            ("telp", "No. Telp", 128, "w"),
            ("paket", "Paket", 88, "w"),
            ("total", "Total", 95, "e"),
            ("status", "Status", 80, "center"),
        ))

    # ==================================================================
    # PEMUATAN DATA
    # ==================================================================
    def muat_data(self) -> None:
        data = self.controller.ringkasan()
        if not data:
            return

        self._isi_kartu(data)
        self._isi_subjudul(data)
        self._isi_kontak_info(data)
        self._isi_status(data)
        self._isi_terbaru(data)
        self._isi_kontak()
        self._tandai_waktu()

    def _isi_kartu(self, data: dict) -> None:
        self.label_pelanggan.configure(text=str(data["total_pelanggan"]))
        self.label_paket.configure(text=str(data["total_paket"]))
        self.label_transaksi.configure(text=str(data["total_transaksi"]))
        self.label_pendapatan.configure(text=_rp(data["total_pendapatan"]))

    def _isi_subjudul(self, data: dict) -> None:
        self.label_subjudul.configure(
            text="Ringkasan operasional jasa laundry \u00b7 hari ini "
                 f"{int(data.get('trx_hari_ini') or 0)} transaksi "
                 f"({_rp(data.get('pendapatan_hari_ini'))}).")

    def _isi_kontak_info(self, data: dict) -> None:
        jumlah_pelanggan = int(data.get("total_pelanggan") or 0)
        lengkap = int(data.get("pelanggan_kontak") or 0)
        kurang = jumlah_pelanggan - lengkap

        catatan = f"{lengkap}/{jumlah_pelanggan} pelanggan punya nomor telepon"
        if kurang > 0:
            catatan += f" \u00b7 {kurang} belum"
        else:
            catatan += " \u00b7 lengkap"
        self.label_kontak_info.configure(text=catatan)

    def _isi_status(self, data: dict) -> None:
        total_cucian = sum(int(data.get(kunci) or 0) for _, kunci in STATUS_BARIS)

        for _, kunci in STATUS_BARIS:
            batang, jumlah = self.bar_status[kunci]
            nilai = int(data.get(kunci) or 0)
            jumlah.configure(text=str(nilai))
            batang.set(nilai / total_cucian if total_cucian else 0.0)

        if total_cucian:
            self.label_total_cucian.configure(
                text=f"Total {total_cucian} cucian tercatat di semua status.")
        else:
            self.label_total_cucian.configure(
                text="Belum ada cucian tercatat.")

    def _isi_terbaru(self, data: dict) -> None:
        self.label_berat.configure(
            text=f"{_angka(data.get('total_berat'))} kg total"
                 f" \u00b7 rata-rata {_angka(data.get('rata_berat'))} kg")

        for item in self.tree_terbaru.get_children():
            self.tree_terbaru.delete(item)

        for baris in self.controller.ambil_transaksi()[:5]:
            self.tree_terbaru.insert("", "end", values=(
                baris["id_transaksi"],
                baris["nama_pelanggan"],
                baris.get("no_telp_pelanggan") or "-",
                baris["nama_paket"],
                _rp(baris["total_biaya"]),
                baris["status_cucian"],
            ))

    def _isi_kontak(self) -> None:
        for item in self.tree_kontak.get_children():
            self.tree_kontak.delete(item)

        for data in self.controller.ambil_kontak_pelanggan():
            self.tree_kontak.insert("", "end", values=(
                data["nama"],
                data.get("no_telp") or "-",
                data.get("alamat") or "-",
                int(data.get("jumlah_transaksi") or 0),
                _rp(data.get("total_belanja")),
            ))

    def _tandai_waktu(self) -> None:
        if self.label_waktu is not None:
            self.label_waktu.configure(
                text=f"Terakhir diperbarui {datetime.now():%H:%M:%S}")