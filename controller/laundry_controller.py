from models.pelanggan_model import PelangganModel
from models.paket_model import PaketModel
from models.transaksi_model import TransaksiModel

# Nilai yang diizinkan kolom enum status_cucian
STATUS_CUCIAN = ("Antrean", "Proses", "Selesai", "Diambil")

# Akun demo
AKUN = {"atmin": "atmin123"}


class LaundryController:
    def __init__(self):
        self.pelanggan_model = PelangganModel()
        self.paket_model = PaketModel()
        self.transaksi_model = TransaksiModel()

    # ==================== MENGAMBIL DATA ====================
    def ambil_pelanggan(self):
        """Daftar pelanggan urut nama."""
        data = self.pelanggan_model.get_all_pelanggan()
        return sorted(data, key=lambda d: str(d["nama"]).lower())

    def ambil_paket(self):
        """Daftar paket layanan urut nama."""
        data = self.paket_model.get_all_paket()
        return sorted(data, key=lambda d: str(d["nama_paket"]).lower())

    def ambil_status(self):
        return STATUS_CUCIAN

    def ambil_transaksi(self):
        nomor = {p["id_pelanggan"]: p.get("no_telp")
                 for p in self.pelanggan_model.get_all_pelanggan()}
        data = self.transaksi_model.get_all_transaksi()
        for t in data:
            t["no_telp_pelanggan"] = nomor.get(t["id_pelanggan"])
        return sorted(data, key=lambda d: d["id_transaksi"], reverse=True)

    def ambil_kontak_pelanggan(self):
        """Daftar pelanggan beserta telepon, alamat, dan total belanjanya."""
        transaksi = self.transaksi_model.get_all_transaksi()
        hasil = []
        for p in self.pelanggan_model.get_all_pelanggan():
            milik = [t for t in transaksi
                     if t["id_pelanggan"] == p["id_pelanggan"]]
            hasil.append({
                "id_pelanggan": p["id_pelanggan"],
                "nama": p["nama"],
                "no_telp": p.get("no_telp"),
                "alamat": p.get("alamat"),
                "jumlah_transaksi": len(milik),
                "total_belanja": sum(float(t["total_biaya"] or 0)
                                     for t in milik),
            })
        return sorted(hasil, key=lambda d: str(d["nama"]).lower())

    def ringkasan(self):
        """Angka ringkasan untuk halaman dashboard."""
        pelanggan = self.pelanggan_model.get_all_pelanggan()
        paket = self.paket_model.get_all_paket()
        transaksi = self.transaksi_model.get_all_transaksi()

        status = {s: 0 for s in STATUS_CUCIAN}
        berat = 0.0
        pendapatan = 0.0
        hari_ini = 0
        pendapatan_hari_ini = 0.0
        from datetime import date
        hari = date.today().isoformat()

        for t in transaksi:
            if t["status_cucian"] in status:
                status[t["status_cucian"]] += 1
            nilai = float(t["total_biaya"] or 0)
            berat += float(t["berat_kg"] or 0)
            pendapatan += nilai
            if str(t["tgl_terima"]) == hari:
                hari_ini += 1
                pendapatan_hari_ini += nilai

        return {
            "total_pelanggan": len(pelanggan),
            "total_paket": len(paket),
            "total_transaksi": len(transaksi),
            "total_pendapatan": pendapatan,
            "st_antrean": status["Antrean"],
            "st_proses": status["Proses"],
            "st_selesai": status["Selesai"],
            "st_diambil": status["Diambil"],
            "trx_hari_ini": hari_ini,
            "pendapatan_hari_ini": pendapatan_hari_ini,
            "total_berat": berat,
            "rata_berat": round(berat / len(transaksi), 1) if transaksi else 0,
            "pelanggan_kontak": sum(1 for p in pelanggan if p.get("no_telp")),
        }

    # ==================== MENCARI ====================
    def detail_pelanggan(self, nama):
        """Cari pelanggan berdasarkan nama, tidak membedakan huruf besar-kecil."""
        target = str(nama or "").strip().lower()
        for p in self.pelanggan_model.get_all_pelanggan():
            if str(p["nama"]).strip().lower() == target:
                return p
        return None

    def cari_id_paket(self, nama):
        """Cari id paket berdasarkan nama."""
        target = str(nama or "").strip().lower()
        for k in self.paket_model.get_all_paket():
            if str(k["nama_paket"]).strip().lower() == target:
                return k["id_paket"]
        return None

    def harga_paket(self, id_paket):
        for k in self.paket_model.get_all_paket():
            if k["id_paket"] == id_paket:
                return float(k["harga_per_kg"] or 0)
        return 0.0

    def hitung_total(self, berat_kg, id_paket):
        """Total biaya = berat dikali harga per kg paket."""
        if not id_paket:
            return 0.0
        try:
            return round(float(berat_kg) * self.harga_paket(id_paket), 2)
        except (TypeError, ValueError):
            return 0.0

    # ==================== TRANSAKSI ====================
    def simpan(self, id_transaksi, id_pelanggan, id_paket, berat_kg,
               tgl_terima, tgl_selesai, status_cucian):
        if not id_pelanggan:
            return False, "Pelanggan wajib dipilih."
        if not id_paket:
            return False, "Paket layanan wajib dipilih."
        if status_cucian not in STATUS_CUCIAN:
            return False, "Status cucian tidak valid."
        try:
            if float(berat_kg) <= 0:
                return False, "Berat cucian harus lebih besar dari nol."
        except (TypeError, ValueError):
            return False, "Berat cucian harus berupa angka."
        if not (tgl_terima or "").strip():
            return False, "Tanggal terima wajib diisi."

        total_biaya = self.hitung_total(berat_kg, id_paket)
        tgl_selesai = str(tgl_selesai or "").strip() or None

        if id_transaksi:
            if not self.transaksi_model.delete_transaksi(int(id_transaksi)):
                return False, "Transaksi tidak ditemukan."

        ok = self.transaksi_model.create_transaksi(
            int(id_pelanggan), int(id_paket), float(berat_kg), tgl_terima,
            tgl_selesai, total_biaya, status_cucian)
        if not ok:
            return False, "Transaksi gagal disimpan."

        if id_transaksi:
            return True, "Transaksi berhasil diperbarui."
        return True, "Transaksi berhasil disimpan."

    def perbarui(self, id_transaksi, id_pelanggan, id_paket, berat_kg,
                 tgl_terima, tgl_selesai, status_cucian):
        return self.simpan(id_transaksi, id_pelanggan, id_paket, berat_kg,
                           tgl_terima, tgl_selesai, status_cucian)

    def hapus(self, id_transaksi):
        if self.transaksi_model.delete_transaksi(int(id_transaksi)):
            return True, "Transaksi berhasil dihapus."
        return False, "Transaksi tidak ditemukan."

    # ==================== PELANGGAN ====================
    def pastikan_pelanggan(self, nama, no_telp="", alamat=""):
        """Pastikan pelanggan ada, lalu kembalikan id-nya."""
        nama = str(nama or "").strip()
        if not nama:
            return False, "Pelanggan wajib dipilih atau diketik.", None

        ada = self.detail_pelanggan(nama)
        if ada is None:
            if not self.pelanggan_model.create_pelanggan(
                    nama, str(no_telp or "").strip(), str(alamat or "").strip()):
                return False, "Pelanggan gagal disimpan.", None
            ada = self.detail_pelanggan(nama)
            if ada is None:
                return False, "Pelanggan gagal disimpan.", None
            return True, f"Pelanggan '{nama}' ditambahkan otomatis.", \
                ada["id_pelanggan"]

        # Sudah ada: lengkapi kontak yang masih kosong.
        if (no_telp or alamat) and not (ada.get("no_telp") and ada.get("alamat")):
            self.pelanggan_model.update_pelanggan(
                ada["id_pelanggan"], ada["nama"],
                ada.get("no_telp") or str(no_telp).strip(),
                ada.get("alamat") or str(alamat).strip())
        return True, "Pelanggan ditemukan.", ada["id_pelanggan"]

    def hapus_pelanggan(self, id_pelanggan):
        target = None
        for p in self.pelanggan_model.get_all_pelanggan():
            if p["id_pelanggan"] == int(id_pelanggan):
                target = p
        if target is None:
            return False, "Pelanggan tidak ditemukan."

        jumlah = sum(1 for t in self.transaksi_model.get_all_transaksi()
                     if t["id_pelanggan"] == int(id_pelanggan))
        if not self.pelanggan_model.delete_pelanggan(int(id_pelanggan)):
            return False, "Gagal menghapus pelanggan."

        pesan = f"Pelanggan '{target['nama']}' berhasil dihapus."
        if jumlah:
            pesan += f" {jumlah} transaksi ikut terhapus."
        return True, pesan

    # ==================== PAKET LAYANAN ====================
    def tambah_paket(self, nama_paket, jenis, harga_per_kg):
        if not (nama_paket or "").strip():
            return False, "Nama paket wajib diisi."
        if not (jenis or "").strip():
            return False, "Jenis layanan wajib diisi."
        try:
            if float(harga_per_kg) <= 0:
                return False, "Harga per kg harus lebih besar dari nol."
        except (TypeError, ValueError):
            return False, "Harga per kg harus berupa angka."

        if self.paket_model.create_paket(str(nama_paket).strip(),
                                          str(jenis).strip(), harga_per_kg):
            return True, "Paket berhasil ditambahkan."
        return False, "Paket gagal disimpan."

    def hapus_paket(self, id_paket):
        target = None
        for k in self.paket_model.get_all_paket():
            if k["id_paket"] == int(id_paket):
                target = k
        if target is None:
            return False, "Paket layanan tidak ditemukan."

        jumlah = sum(1 for t in self.transaksi_model.get_all_transaksi()
                     if t["id_paket"] == int(id_paket))
        if not self.paket_model.delete_paket(int(id_paket)):
            return False, "Gagal menghapus paket."

        pesan = f"Paket '{target['nama_paket']}' berhasil dihapus."
        if jumlah:
            pesan += f" {jumlah} transaksi ikut terhapus."
        return True, pesan

    # ==================== LOGIN ====================
    def login(self, username, password):
        username = str(username or "").strip()
        password = password or ""

        if not username or not password:
            return False, "Username dan password wajib diisi.", None

        if AKUN.get(username) == password:
            return True, f"Selamat datang, {username}!", username

        return False, "Username atau password salah.", None