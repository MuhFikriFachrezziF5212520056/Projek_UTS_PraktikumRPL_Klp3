from models.pelanggan_model import PelangganModel
from models.paket_model import PaketModel
from models.transaksi_model import TransaksiModel

# Inisialisasi Model
pelanggan_model = PelangganModel()
paket_model = PaketModel()
transaksi_model = TransaksiModel()

# Pengujian Read Data
print("Pelanggan:", pelanggan_model.get_all_pelanggan())
print("Paket:", paket_model.get_all_paket())
print("Transaksi:", transaksi_model.get_all_transaksi())