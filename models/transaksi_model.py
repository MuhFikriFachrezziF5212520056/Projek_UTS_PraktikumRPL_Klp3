import mysql.connector
from config.database import Database

class TransaksiModel:
    def __init__(self):
        self.db = Database()
        self.conn = self.db.get_connection()
        self.table_name = "transaksi_laundry"

    def get_all_transaksi(self):
        if self.conn:
            try:
                cursor = self.conn.cursor(dictionary=True)
                # Menggunakan JOIN agar nama pelanggan dan nama paket juga bisa terbaca
                query = f"""
                    SELECT t.*, p.nama AS nama_pelanggan, pk.nama_paket 
                    FROM {self.table_name} t
                    JOIN pelanggan p ON t.id_pelanggan = p.id_pelanggan
                    JOIN paket_layanan pk ON t.id_paket = pk.id_paket
                """
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                return result
            except mysql.connector.Error as e:
                print(f"Error Read Transaksi: {e}")
                return []
        return []

    def create_transaksi(self, id_pelanggan, id_paket, berat_kg, tgl_terima, tgl_selesai, total_biaya, status_cucian):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                query = f"""
                    INSERT INTO {self.table_name} 
                    (id_pelanggan, id_paket, berat_kg, tgl_terima, tgl_selesai, total_biaya, status_cucian) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                val = (id_pelanggan, id_paket, berat_kg, tgl_terima, tgl_selesai, total_biaya, status_cucian)
                cursor.execute(query, val)
                self.conn.commit()
                cursor.close()
                return True
            except mysql.connector.Error as e:
                self.conn.rollback()
                print(f"Error Create Transaksi: {e}")
                return False
        return False

    def update_status(self, id_transaksi, status_cucian):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                query = f"UPDATE {self.table_name} SET status_cucian = %s WHERE id_transaksi = %s"
                val = (status_cucian, id_transaksi)
                cursor.execute(query, val)
                self.conn.commit()
                cursor.close()
                return True
            except mysql.connector.Error as e:
                self.conn.rollback()
                print(f"Error Update Status Transaksi: {e}")
                return False
        return False

    def delete_transaksi(self, id_transaksi):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                query = f"DELETE FROM {self.table_name} WHERE id_transaksi = %s"
                cursor.execute(query, (id_transaksi,))
                self.conn.commit()
                cursor.close()
                return True
            except mysql.connector.Error as e:
                self.conn.rollback()
                print(f"Error Delete Transaksi: {e}")
                return False
        return False