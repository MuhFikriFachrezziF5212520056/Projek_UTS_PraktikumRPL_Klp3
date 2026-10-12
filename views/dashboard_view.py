"""
Antarmuka halaman Dashboard.

Sesuai Modul 5, berkas ini berisi antarmuka statis. Kartu ringkasan,
panel, dan tabel sudah tersusun rapi, tetapi belum dihubungkan ke
Controller. Angka dan isi tabel diambil dari data contoh pada
views/laundry_view.py, bukan dari basis data.

Jalankan berkas ini secara mandiri dengan:
    python views/dashboard_view.py
"""

from datetime import datetime

import customtkinter as ctk

from views.laundry_view import (
    DATA_PAKET, DATA_PELANGGAN, DATA_TRANSAKSI, WARNA_KARTU, _gaya_tabel,
    _label, _rp, _tabel, _tombol)

# Gaya huruf yang sering dipakai, ditulis sekali agar tidak berulang.
_JUDUL = {"font": ("Segoe UI", 14, "bold"), "anchor": "w"}
_ABU = {"text_color": "gray", "anchor": "w"}

# Pasangan label status cucian dengan kunci ringkasan.
STATUS_BARIS = (
    ("Antrean", "st_antrean"),
    ("Proses", "st_proses"),
    ("Selesai", "st_selesai"),
    ("Diambil", "st_diambil"),
)


def _angka(nilai) -> str:
    """Mengubah angka menjadi teks dengan pemisah desimal koma."""
    return f"{float(nilai or 0):g}".replace(".", ",")


class DashboardView(ctk.CTkFrame):
    """Halaman ringkasan operasional berupa antarmuka statis."""

    def __init__(self, master, nama_pengguna: str = "operator"):
        super().__init__(master, fg_color="transparent")
        self.nama_pengguna = nama_pengguna

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(4, weight=3)
        self.grid_rowconfigure(6, weight=2)

        _gaya_tabel()
        self._build_sapaan()
        self._build_kartu()
        self._build_panel_kontak()
        self._build_panel_status()
        self._build_panel_terbaru()
        self.muat_data()

    # ==================================================================
    # KONSTRUKSI KOMPONEN
    # ==================================================================
    def _build_sapaan(self) -> None:
        _label(self, f"Halo, {self.nama_pengguna}!", 0, 0, columnspan=3,
               gaya={"font": ("Segoe UI", 20, "bold"), "anchor": "w"},
               sticky="w", pady=(0, 2))

        self.btn_refresh = _tombol(
            self, "\u21bb  Muat Ulang", self.muat_data, 0, 3,
            gaya={"width": 130, "height": 34, "corner_radius": 12},
            sticky="e")

        self.label_subjudul = _label(
            self, "Ringkasan operasional jasa laundry.", 1, 0,
            columnspan=3, gaya={**_ABU, "font": ("Segoe UI", 12)},
            sticky="w", pady=(0, 14))

        self.label_waktu = _label(
            self, "", 1, 3,
            gaya={**_ABU, "anchor": "e", "font": ("Segoe UI", 10)},
            sticky="e", pady=(0, 14))

    def _build_kartu(self) -> None:
        self.frame_kartu = ctk.CTkFrame(self, fg_color="transparent")
        kartu = self.frame_kartu
        kartu.grid(row=2, column=0, columnspan=4, sticky="ew")
        for kolom in range(4):
            kartu.grid_columnconfigure(kolom, weight=1)

        for kolom, judul, keterangan in (
                (0, "Pelanggan", "Jumlah pelanggan terdaftar"),
                (1, "Paket Layanan", "Katalog layanan tersedia"),
                (2, "Transaksi", "Total transaksi laundry"),
                (3, "Total Pendapatan", "Akumulasi seluruh transaksi")):
            label = self._satu_kartu(kolom, judul, keterangan)
            setattr(self, f"label_kartu_{kolom}", label)

    def _satu_kartu(self, kolom, judul, keterangan) -> ctk.CTkLabel:
        """Membuat satu kartu ringkasan dan mengembalikan label nilainya."""
        bingkai = ctk.CTkFrame(self.frame_kartu, corner_radius=14,
                               fg_color=WARNA_KARTU)
        bingkai.grid(row=0, column=kolom, sticky="nsew",
                     padx=(0 if kolom == 0 else 5, 5))
        _label(bingkai, judul, 0, 0,
               gaya={**_ABU, "font": ("Segoe UI", 12)},
               sticky="ew", padx=14, pady=(12, 0))
        nilai = _label(bingkai, "0", 1, 0,
                       gaya={"font": ("Segoe UI", 22, "bold"),
                             "anchor": "w"},
                       sticky="ew", padx=14)
        _label(bingkai, keterangan, 2, 0,
               gaya={**_ABU, "font": ("Segoe UI", 10)},
               sticky="ew", padx=14, pady=(0, 12))
        return nilai

    def _build_panel_kontak(self) -> None:
        _label(self, "Kontak Pelanggan", 3, 0, columnspan=2,
               gaya=_JUDUL, sticky="w", pady=(0, 6))

        self.label_kontak_info = _label(
            self, "", 3, 2, columnspan=2,
            gaya={**_ABU, "anchor": "e", "font": ("Segoe UI", 11)},
            sticky="e", padx=(0, 8), pady=(0, 6))

        self.frame_kontak = ctk.CTkFrame(self, fg_color=WARNA_KARTU,
                                         corner_radius=14)
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
        _label(self, "Status Cucian", 5, 0, columnspan=2, gaya=_JUDUL,
               sticky="w", padx=(0, 12), pady=(18, 6))

        self.frame_status = ctk.CTkFrame(self, fg_color=WARNA_KARTU,
                                          corner_radius=14)
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
        _label(self, "Transaksi Terbaru", 5, 2, gaya=_JUDUL,
               sticky="w", pady=(18, 6))

        self.label_berat = _label(
            self, "", 5, 3,
            gaya={"font": ("Segoe UI", 11), "text_color": "gray",
                  "anchor": "e"},
            sticky="e", padx=(0, 8), pady=(18, 6))

        self.frame_terbaru = ctk.CTkFrame(self, fg_color=WARNA_KARTU,
                                           corner_radius=14)
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
    # PENGISIAN DARI DATA CONTOH
    # ==================================================================
    def muat_data(self) -> None:
        """Mengisi seluruh halaman dari data contoh."""
        ringkasan = self._hitung_ringkasan()
        self._isi_kartu(ringkasan)
        self._isi_subjudul(ringkasan)
        self._isi_kontak_info(ringkasan)
        self._isi_status(ringkasan)
        self._isi_terbaru(ringkasan)
        self._isi_kontak()
        self._tandai_waktu()

    def _hitung_ringkasan(self) -> dict:
        """Menyusun angka ringkasan dari data contoh."""
        status = {kunci: 0 for _nama, kunci in STATUS_BARIS}
        berat = 0
        pendapatan = 0
        for baris in DATA_TRANSAKSI:
            kunci = f"st_{baris['status'].lower()}"
            if kunci in status:
                status[kunci] += 1
            berat += baris["berat"]
            pendapatan += baris["total"]

        total_cucian = sum(status.values())
        return {
            "total_pelanggan": len(DATA_PELANGGAN),
            "total_paket": len(DATA_PAKET),
            "total_transaksi": len(DATA_TRANSAKSI),
            "total_pendapatan": pendapatan,
            "total_cucian": total_cucian,
            "total_berat": berat,
            "rata_berat": round(berat / total_cucian, 1) if total_cucian else 0,
            "pelanggan_kontak": sum(
                1 for o in DATA_PELANGGAN if o["no_telp"]),
            **status,
        }

    def _isi_kartu(self, data: dict) -> None:
        """Menampilkan angka ke dalam empat kartu ringkasan."""
        self.label_kartu_0.configure(text=str(data["total_pelanggan"]))
        self.label_kartu_1.configure(text=str(data["total_paket"]))
        self.label_kartu_2.configure(text=str(data["total_transaksi"]))
        self.label_kartu_3.configure(text=_rp(data["total_pendapatan"]))

    def _isi_subjudul(self, data: dict) -> None:
        """Mengubah kalimat subjudul sesuai jumlah cucian tercatat."""
        self.label_subjudul.configure(
            text="Ringkasan operasional jasa laundry \u00b7 "
                 f"{data['total_cucian']} cucian tercatat di semua status.")

    def _isi_kontak_info(self, data: dict) -> None:
        """Mengubah ringkasan kelengkapan data kontak pelanggan."""
        jumlah = data["total_pelanggan"]
        lengkap = data["pelanggan_kontak"]
        kurang = jumlah - lengkap

        catatan = f"{lengkap}/{jumlah} pelanggan punya nomor telepon"
        catatan += f" \u00b7 {kurang} belum" if kurang else " \u00b7 lengkap"
        self.label_kontak_info.configure(text=catatan)

    def _isi_status(self, data: dict) -> None:
        """Menampilkan jumlah dan panjang batang pada tiap status."""
        total_cucian = data["total_cucian"]
        for _nama, kunci in STATUS_BARIS:
            batang, jumlah = self.bar_status[kunci]
            nilai = data[kunci]
            jumlah.configure(text=str(nilai))
            batang.set(nilai / total_cucian if total_cucian else 0.0)

        self.label_total_cucian.configure(
            text=f"Total {total_cucian} cucian tercatat di semua status."
            if total_cucian else "Belum ada cucian tercatat.")

    def _isi_terbaru(self, data: dict) -> None:
        """Mengisi tabel transaksi terbaru."""
        self.label_berat.configure(
            text=f"{_angka(data['total_berat'])} kg total"
                 f" \u00b7 rata-rata {_angka(data['rata_berat'])} kg")

        for item in self.tree_terbaru.get_children():
            self.tree_terbaru.delete(item)

        for baris in DATA_TRANSAKSI[:5]:
            self.tree_terbaru.insert("", "end", values=(
                baris["id"],
                baris["pelanggan"],
                baris["telp"] or "-",
                baris["paket"],
                _rp(baris["total"]),
                baris["status"],
            ))

    def _isi_kontak(self) -> None:
        """Mengisi tabel kontak pelanggan beserta total belanjanya."""
        for item in self.tree_kontak.get_children():
            self.tree_kontak.delete(item)

        for orang in DATA_PELANGGAN:
            milik = [b for b in DATA_TRANSAKSI
                     if b["pelanggan"] == orang["nama"]]
            self.tree_kontak.insert("", "end", values=(
                orang["nama"],
                orang["no_telp"] or "-",
                orang["alamat"] or "-",
                len(milik),
                _rp(sum(b["total"] for b in milik)),
            ))

    def _tandai_waktu(self) -> None:
        """Menampilkan jam saat tampilan dibuat ulang."""
        if self.label_waktu is not None:
            self.label_waktu.configure(
                text=f"Terakhir diperbarui {datetime.now():%H:%M:%S}")


if __name__ == "__main__":
    # Pengujian antarmuka secara mandiri sesuai langkah pada Modul 5.
    ctk.set_appearance_mode("light")
    jendela = ctk.CTk()
    jendela.title("Halaman Dashboard")
    jendela.geometry("1180x760")
    jendela.grid_rowconfigure(0, weight=1)
    jendela.grid_columnconfigure(0, weight=1)

    tampilan = DashboardView(jendela, "atmin")
    tampilan.grid(row=0, column=0, sticky="nsew")

    jendela.mainloop()