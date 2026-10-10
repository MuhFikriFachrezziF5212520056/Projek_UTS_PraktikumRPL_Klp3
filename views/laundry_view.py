from datetime import date
import customtkinter as ctk
from tkinter import ttk, messagebox

# Palet tabel agar senada dengan tema customtkinter.
_GELAP = {"bg": "#2b2b2b", "fg": "#e8e8e8", "head_bg": "#3a3a3a",
          "head_fg": "#ffffff", "sel_bg": "#1f6aa5"}
_TERANG = {"bg": "#ffffff", "fg": "#1a1a1a", "head_bg": "#e6e6e6",
           "head_fg": "#1a1a1a", "sel_bg": "#1f6aa5"}

def _gaya_tabel(mode) -> ttk.Style:
    p = _GELAP if str(mode).strip().lower().startswith("dark") else _TERANG
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
    return gaya

# Nilai yang disediakan untuk kolom jenis layanan.
DAFTAR_JENIS = ["Cuci Kering", "Cuci Basah", "Setrika",
                "Pembersihan Karpet", "Lipat"]

def bind_event(widget, event: str, fungsi) -> None:
    internal = getattr(widget, "_entry", None)
    if internal is not None:
        internal.bind(event, fungsi)

def _tanggal_hari_ini() -> str:
    return date.today().isoformat()

def _label(bapak, teks, baris=0, kolom=0, *, gaya=None, **tempat):
    """Menempatkan satu label ke dalam wadah."""
    label = ctk.CTkLabel(bapak, text=teks, **(gaya or {}))
    label.grid(row=baris, column=kolom, **tempat)
    return label

def _input(bapak, kelas, baris=0, kolom=0, *, gaya=None, **tempat):
    """Menempatkan widget isian, yaitu CTkEntry atau CTkComboBox."""
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
    kolom.delete(0, "end")
    if teks not in (None, ""):
        kolom.insert(0, str(teks))

class LaundryView(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.id_terpilih = None
        self._paket = []        # daftar paket untuk mencari harga
        self._pelanggan = []    # daftar pelanggan untuk mengenali nama

        _gaya_tabel(ctk.get_appearance_mode())
        self._build_form()
        self._build_tabel()
        self._isi_tanggal_default()

        self.muat_data_pendukung()
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

        # Frame disimpan sebagai atribut agar warna tema dapat
        # disesuaikan dari main.py.
        self.frame_form = ctk.CTkFrame(self)
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
            form, "Hapus", self._aksi_hapus_pelanggan, 1, 1,
            gaya={**kecil, **merah}, padx=(0, 12), pady=2)

        self.combo_paket = _input(
            form, ctk.CTkComboBox, 1, 2,
            gaya={"state": "readonly", "values": ["-"]},
            sticky="ew", padx=(12, 4), pady=2)

        self.btn_tambah_paket = _tombol(
            form, "+ Paket", self._buka_dialog_paket, 1, 3,
            gaya=kecil, padx=4, pady=2)

        self.btn_hapus_paket = _tombol(
            form, "Hapus", self._aksi_hapus_paket, 1, 4,
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
                  lambda _e: self._hitung_otomatis())
        self.combo_status = _input(form, ctk.CTkComboBox, 5, 2, columnspan=3,
                                   gaya={"state": "readonly",
                                         "values": ["Antrean"]},
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

        # Ringkasan total - dihitung Controller, hanya ditampilkan di sini.
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
        _tombol(tombol, "Simpan Data", self._aksi_simpan, 0, 0,
                gaya=aksi, sticky="ew", padx=(0, 4))
        _tombol(tombol, "Perbarui", self._aksi_perbarui, 0, 1,
                gaya={**aksi, "fg_color": "#1f6aa5"}, sticky="ew", padx=4)
        _tombol(tombol, "Hapus", self._aksi_hapus, 0, 2,
                gaya={**aksi, **merah}, sticky="ew", padx=(4, 0))

    def _build_tabel(self) -> None:
        judul = {"font": ("Segoe UI", 14, "bold"), "anchor": "w"}
        _label(self, "Daftar Transaksi", 0, 1, gaya=judul,
               sticky="w", pady=(0, 6))

        # Petunjuk hanya muncul bila paket layanan belum tersedia.
        self.label_petunjuk = _label(self, "", 2, 1,
                                     gaya={"text_color": "#e8a33d",
                                           "anchor": "w"})

        self.frame_tabel = ctk.CTkFrame(self)
        bingkai = self.frame_tabel
        bingkai.grid(row=1, column=1, sticky="nsew")
        bingkai.grid_rowconfigure(1, weight=1)
        bingkai.grid_columnconfigure(0, weight=1)

        kolom = (("id", "ID", 45, "center"), ("pelanggan", "Pelanggan",
                                               150, "w"),
                 ("paket", "Paket", 120, "w"), ("berat", "Berat", 70, "e"),
                 ("total", "Total Biaya", 110, "e"),
                 ("status", "Status", 90, "center"))
        self.tree = _tabel(bingkai, kolom, tinggi=14)
        self.tree.grid_configure(pady=(4, 6))
        self.tree.bind("<<TreeviewSelect>>", self._baris_dipilih)

        scroll = ttk.Scrollbar(bingkai, orient="vertical",
                               command=self.tree.yview,
                               style="Laundry.Vertical.TScrollbar")
        scroll.grid(row=1, column=1, sticky="ns", padx=(0, 10), pady=(4, 6))
        self.tree.configure(yscrollcommand=scroll.set)

        _tombol(bingkai, "Muat Ulang Data", self.muat_daftar, 2, 0,
                columnspan=2, gaya={"height": 28, "fg_color": "transparent",
                                    "border_width": 1,
                                    "text_color": "gray"},
                sticky="ew", padx=10, pady=(0, 10))

    # ==================================================================
    # TANGGAL TERIMA OTOMATIS
    # ==================================================================
    def _isi_tanggal_default(self) -> None:
        if not self.entry_terima.get().strip():
            _isi(self.entry_terima, _tanggal_hari_ini())

    def _pelanggan_diubah(self, _event=None) -> None:
        self._isi_tanggal_default()
        self._isi_kontak_pelanggan()
        self._hitung_otomatis()

    def _isi_kontak_pelanggan(self) -> None:
        data = self.controller.detail_pelanggan(self.combo_pelanggan.get().strip())
        _isi(self.entry_telp, data and data.get("no_telp"))
        _isi(self.entry_alamat, data and data.get("alamat"))

    # ==================================================================
    # DATA PENDUKUNG
    # ==================================================================
    def muat_data_pendukung(self) -> None:
        self._pelanggan = self.controller.ambil_pelanggan()
        nama = [d["nama"] for d in self._pelanggan] or ["-"]
        self.combo_pelanggan.configure(values=nama)
        self.combo_pelanggan.set(nama[0])

        self._paket = self.controller.ambil_paket()
        paket = [d["nama_paket"] for d in self._paket] or ["-"]
        self.combo_paket.configure(values=paket)
        self.combo_paket.set(paket[0])

        status = list(self.controller.ambil_status())
        self.combo_status.configure(values=status)
        self.combo_status.set(status[0])

        self._perbarui_petunjuk()

    def _perbarui_petunjuk(self) -> None:
        if self._paket:
            self.label_petunjuk.configure(text="")
            self.label_petunjuk.grid_remove()
        else:
            self.label_petunjuk.configure(
                text="Katalog paket masih kosong. Tekan tombol "
                     "'+ Paket' untuk menambah layanan pertama.")
            self.label_petunjuk.grid(row=2, column=1, sticky="w",
                                     pady=(6, 0))

    def _id_paket_terpilih(self):
        if self.controller.cari_id_paket:
            return self.controller.cari_id_paket(self.combo_paket.get())
        for item in self._paket:
            if item["nama_paket"] == self.combo_paket.get():
                return item["id_paket"]
        return None

    def _selesai_pelanggan(self):

        nama = self.combo_pelanggan.get().strip()
        berhasil, pesan, id_pelanggan = self.controller.pastikan_pelanggan(
            nama,
            self.entry_telp.get().strip(),
            self.entry_alamat.get().strip(),
        )
        return (id_pelanggan if berhasil else None), pesan

    # ==================================================================
    # DIALOG TAMBAH PAKET
    # ==================================================================
    def _buka_dialog_paket(self) -> None:
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

        entry_nama = _input(frame, ctk.CTkEntry, 1, 0, columnspan=2,
                            gaya={"placeholder_text": "Contoh: Cuci Kilat"},
                            sticky="ew", pady=(0, 10))

        combo_jenis = _input(frame, ctk.CTkComboBox, 3, 0, columnspan=2,
                             gaya={"state": "normal",
                                   "values": DAFTAR_JENIS},
                             sticky="ew", pady=(0, 10))
        combo_jenis.set(DAFTAR_JENIS[0])

        entry_harga = _input(frame, ctk.CTkEntry, 5, 0, columnspan=2,
                             gaya={"placeholder_text": "Contoh: 7500"},
                             sticky="ew", pady=(0, 14))

        label("Nama Paket", 0)
        label("Jenis Layanan", 2)
        label("Harga per Kg (Rp)", 4)

        def simpan(_event=None):
            ok, pesan = self.controller.tambah_paket(
                entry_nama.get().strip(),
                combo_jenis.get().strip(),
                entry_harga.get().strip(),
            )
            if not ok:
                messagebox.showerror("Gagal", pesan, parent=dialog)
                return

            self.muat_data_pendukung()
            # Pilih paket yang baru saja dibuat.
            self.combo_paket.set(entry_nama.get().strip())
            self._hitung_otomatis()
            messagebox.showinfo("Informasi", pesan, parent=dialog)
            dialog.destroy()

        tombol = ctk.CTkFrame(frame, fg_color="transparent")
        tombol.grid(row=6, column=0, columnspan=2, sticky="ew")
        tombol.grid_columnconfigure((0, 1), weight=1)
        _tombol(tombol, "Batal", dialog.destroy, 0, 0,
                gaya={"height": 32, "fg_color": "transparent",
                      "border_width": 1, "text_color": "gray"},
                sticky="ew", padx=(0, 4))
        _tombol(tombol, "Simpan Paket", simpan, 0, 1,
                gaya={"height": 32}, sticky="ew", padx=(4, 0))

        entry_nama.focus_set()
        bind_event(entry_nama, "<Return>", simpan)
        bind_event(entry_harga, "<Return>", simpan)

    # ==================================================================
    # AKSI
    # ==================================================================
    def _hitung_otomatis(self, _event=None) -> None:
        total = self.controller.hitung_total(self.entry_berat.get().strip(),
                                    self._id_paket_terpilih())
        self.label_total.configure(
            text=f"Total Biaya: Rp {total:,.0f}".replace(",", "."))

    def _data_form(self) -> tuple:
        return (
            self._id_paket_terpilih(),
            self.entry_berat.get().strip(),
            self.entry_terima.get().strip(),
            self.entry_selesai.get().strip(),
            self.combo_status.get().strip(),
        )

    def _aksi_simpan(self, perbarui: bool = False) -> None:
        if perbarui:
            if not self.id_terpilih:
                messagebox.showwarning(
                    "Peringatan", "Pilih baris pada tabel terlebih dahulu.")
                return
        elif self._id_paket_terpilih() is None:
            messagebox.showwarning(
                "Peringatan", "Pilih paket layanan terlebih dahulu.")
            return

        id_pelanggan, pesan = self._selesai_pelanggan()
        if id_pelanggan is None:
            messagebox.showerror("Gagal", pesan)
            return

        isi = self._data_form()
        if perbarui:
            ok, pesan = self.controller.perbarui(self.id_terpilih, id_pelanggan, *isi)
        else:
            ok, pesan = self.controller.simpan(None, id_pelanggan, *isi)

        if not ok:
            messagebox.showerror("Gagal", pesan)
            return
        if "ditambahkan otomatis" in pesan:
            self.muat_data_pendukung()
        messagebox.showinfo("Informasi", pesan)
        self.reset_form()
        self.muat_daftar()

    def _aksi_perbarui(self) -> None:
        self._aksi_simpan(perbarui=True)

    def _hapus(self, kunci, pesan_konfirmasi: str, isi_form: bool = False) -> None:
        if kunci is None:
            return
        if not messagebox.askyesno("Konfirmasi", pesan_konfirmasi,
                                   icon="warning"):
            return

        ok, pesan = kunci()
        if ok:
            self.muat_data_pendukung()
            self.muat_daftar()
            if isi_form:
                self.reset_form()
        messagebox.showinfo("Informasi", pesan) if ok else \
            messagebox.showerror("Gagal", pesan)

    def _aksi_hapus(self) -> None:
        if not self.id_terpilih:
            messagebox.showwarning(
                "Peringatan", "Pilih baris pada tabel terlebih dahulu.")
            return
        self._hapus(lambda: self.controller.hapus(self.id_terpilih),
                    "Hapus transaksi ini?", isi_form=True)

    def _aksi_hapus_pelanggan(self) -> None:
        nama = self.combo_pelanggan.get().strip()
        id_pelanggan = next((p["id_pelanggan"] for p in self._pelanggan
                             if p["nama"].lower() == nama.lower()), None)
        if id_pelanggan is None:
            messagebox.showwarning(
                "Peringatan",
                "Pilih pelanggan yang sudah terdaftar terlebih dahulu.")
            return

        self._hapus(
            lambda: self.controller.hapus_pelanggan(id_pelanggan),
            f"Hapus pelanggan '{nama}'?\n\n"
            "Semua transaksi milik pelanggan ini juga akan terhapus.")

    def _aksi_hapus_paket(self) -> None:
        id_paket = self._id_paket_terpilih()
        if id_paket is None:
            messagebox.showwarning(
                "Peringatan", "Pilih paket layanan terlebih dahulu.")
            return

        nama = self.combo_paket.get().strip()
        self._hapus(
            lambda: self.controller.hapus_paket(id_paket),
            f"Hapus paket '{nama}'?\n\n"
            "Semua transaksi yang memakai paket ini juga akan terhapus.")

    # ==================================================================
    # TABEL
    # ==================================================================
    def _baris_dipilih(self, _event=None) -> None:
        pilihan = self.tree.selection()
        if not pilihan or not self.controller.ambil_transaksi:
            return
        self.id_terpilih = self.tree.item(pilihan[0], "values")[0]

        for b in self.controller.ambil_transaksi():
            if str(b["id_transaksi"]) != str(self.id_terpilih):
                continue
            self.combo_pelanggan.set(b["nama_pelanggan"])
            self._isi_kontak_pelanggan()
            self.combo_paket.set(b["nama_paket"])
            _isi(self.entry_berat, f"{float(b['berat_kg']):g}")
            _isi(self.entry_terima, b["tgl_terima"])
            _isi(self.entry_selesai, b["tgl_selesai"])
            self.combo_status.set(b["status_cucian"])
            self._hitung_otomatis()
            break

    def muat_daftar(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)
        for baris in self.controller.ambil_transaksi():
            total = float(baris["total_biaya"] or 0)
            self.tree.insert("", "end", values=(
                baris["id_transaksi"],
                baris["nama_pelanggan"],
                baris["nama_paket"],
                f"{float(baris['berat_kg']):g} kg",
                f"Rp {total:,.0f}".replace(",", "."),
                baris["status_cucian"],
            ))

    def reset_form(self) -> None:
        self.id_terpilih = None
        for kolom in (self.entry_telp, self.entry_alamat, self.entry_berat,
                      self.entry_selesai):
            _isi(kolom, "")
        _isi(self.entry_terima, "")
        self._isi_tanggal_default()
        self.label_total.configure(text="Total Biaya: Rp 0")
        self.tree.selection_remove(*self.tree.selection())
        # Kembalikan kolom pelanggan ke pilihan pertama beserta kontaknya.
        if self._pelanggan:
            self.combo_pelanggan.set(self._pelanggan[0]["nama"])
            self._isi_kontak_pelanggan()
