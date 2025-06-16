import tkinter as tk
from tkinter import messagebox
import mysql.connector
import main_menu


def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            port=3307,
            user="root",
            password="123456",  # BURAYI DÜZENLE
            database="halisaha_db"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Veritabanı Hatası", f"Bağlantı kurulamadı: {err}")
        return None


def check_login():
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showwarning("Giriş Hatası", "Alanlar boş bırakılamaz!")
        return

    conn = get_db_connection()
    if conn is None:
        return

    try:
        cursor = conn.cursor()
        cursor.callproc('spValidateUser', [username, password])
        user_found = False

        for result in cursor.stored_results():
            if result.fetchone():
                user_found = True
                break

        if user_found:
            root.destroy()
            main_window = tk.Tk()
            main_menu.MainMenu(main_window)
            main_window.mainloop()
        else:
            messagebox.showerror("Hata", "Kullanıcı adı veya şifre hatalı!")
    finally:
        if conn.is_connected():
            conn.close()


root = tk.Tk()
root.title("Halı Saha - Giriş")
root.geometry("300x150")

tk.Label(root, text="Kullanıcı Adı:").pack(pady=(10, 0))
username_entry = tk.Entry(root)
username_entry.pack()

tk.Label(root, text="Şifre:").pack(pady=(5, 0))
password_entry = tk.Entry(root, show="*")
password_entry.pack()

tk.Button(root, text="Giriş Yap", command=check_login).pack(pady=10)

root.mainloop()