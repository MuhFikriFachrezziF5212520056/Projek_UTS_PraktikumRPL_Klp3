import mysql.connector
from config.database import Database

class PaketModel:
    def __init__(self):
        self.db = Database()
        self.conn = self.db.get_connection()
        self.table_name = "paket_layanan"

    def get_all_paket(self):
        if self.conn:
            try:
                cursor = self.conn.cursor(dictionary=True)
                query = f"SELECT * FROM {self.table_name}"
                cursor.execute(query)
                result = cursor.fetchall()
                cursor.close()
                return result
            except mysql.connector.Error as e:
                print(f"Error Read Paket: {e}")
                return []
        return []

    def create_paket(self, nama_paket, jenis, harga_per_kg):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                query = f"INSERT INTO {self.table_name} (nama_paket, jenis, harga_per_kg) VALUES (%s, %s, %s)"
                val = (nama_paket, jenis, harga_per_kg)
                cursor.execute(query, val)
                self.conn.commit()
                cursor.close()
                return True
            except mysql.connector.Error as e:
                self.conn.rollback()
                print(f"Error Create Paket: {e}")
                return False
        return False

    def update_paket(self, id_paket, nama_paket, jenis, harga_per_kg):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                query = f"UPDATE {self.table_name} SET nama_paket = %s, jenis = %s, harga_per_kg = %s WHERE id_paket = %s"
                val = (nama_paket, jenis, harga_per_kg, id_paket)
                cursor.execute(query, val)
                self.conn.commit()
                cursor.close()
                return True
            except mysql.connector.Error as e:
                self.conn.rollback()
                print(f"Error Update Paket: {e}")
                return False
        return False

    def delete_paket(self, id_paket):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                query = f"DELETE FROM {self.table_name} WHERE id_paket = %s"
                cursor.execute(query, (id_paket,))
                self.conn.commit()
                cursor.close()
                return True
            except mysql.connector.Error as e:
                self.conn.rollback()
                print(f"Error Delete Paket: {e}")
                return False
        return False