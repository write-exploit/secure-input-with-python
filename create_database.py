import sqlite3

baglan = sqlite3.connect("users.db")
cursor = baglan.cursor()

tablo_oluştur = "CREATE TABLE IF NOT EXISTS users(name,password);"
cursor.execute(tablo_oluştur)
cursor.close()
baglan.close()
