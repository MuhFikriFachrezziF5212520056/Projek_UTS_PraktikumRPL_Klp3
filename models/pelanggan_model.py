import mysql.connector
from config.database import Database

class PelangganModel:
    def __init__(self):
        self.db = Database()
        self.conn = self.db.get_connection()
        self.table_name = "pelanggan"

    def get_all_pelanggan(self):
        if self.conn:
            try:
                cursor = self.conn.cursor(dictionary=True)
                query = f"SELECT * FROM {self.table_name}"
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                return result
            except mysql.connector.Error as e:
                print(f"Error Read Pelanggan: {e}")
                return []
        return []

    def create_pelanggan(self, nama, no_telp, alamat):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                query = f"INSERT INTO {self.table_name} (nama, no_telp, alamat) VALUES (%s, %s, %s)"
                val = (nama, no_telp, alamat)
                cursor.execute(query, val)
                self.conn.commit()
                cursor.close()
                return True
            except mysql.connector.Error as e:
                self.conn.rollback()
                print(f"Error Create Pelanggan: {e}")
                return False
        return False

    def update_pelanggan(self, id_pelanggan, nama, no_telp, alamat):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                query = f"UPDATE {self.table_name} SET nama = %s, no_telp = %s, alamat = %s WHERE id_pelanggan = %s"
                val = (nama, no_telp, alamat, id_pelanggan)
                cursor.execute(query, val)
                self.conn.commit()
                cursor.close()
                return True
            except mysql.connector.Error as e:
                self.conn.rollback()
                print(f"Error Update Pelanggan: {e}")
                return False
        return False

    def delete_pelanggan(self, id_pelanggan):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                query = f"DELETE FROM {self.table_name} WHERE id_pelanggan = %s"
                cursor.execute(query, (id_pelanggan,))
                self.conn.commit()
                cursor.close()
                return True
            except mysql.connector.Error as e:
                self.conn.rollback()
                print(f"Error Delete Pelanggan: {e}")
                return False
        return False