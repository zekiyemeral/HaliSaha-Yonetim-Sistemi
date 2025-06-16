import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector


# Veritabanı bağlantısı için fonksiyon
def get_db_connection():
    try:
        # Şifreni ve port numaranı kontrol etmeyi unutma
        return mysql.connector.connect(
            host="localhost",
            port=3307,
            user="root",
            password="123456",  # BURAYI DÜZENLE
            database="halisaha_db"
        )
    except mysql.connector.Error as err:
        messagebox.showerror("Bağlantı Hatası", str(err))
        return None


class UyeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Üye Yönetimi")
        self.root.geometry("800x400")

        # Arayüz kodları...
        input_frame = tk.Frame(root, padx=10, pady=10)
        input_frame.pack(side='left', fill='y', anchor='nw')
        tree_frame = tk.Frame(root, padx=10, pady=10)
        tree_frame.pack(side='right', fill='both', expand=True)

        tk.Label(input_frame, text="Üye ID:").grid(
            row=0, column=0, sticky='w', pady=2
        )
        self.id_entry = tk.Entry(input_frame, state='readonly')
        self.id_entry.grid(row=0, column=1, pady=2, padx=5)

        tk.Label(input_frame, text="Ad Soyad:").grid(
            row=1, column=0, sticky='w', pady=2
        )
        self.ad_entry = tk.Entry(input_frame)
        self.ad_entry.grid(row=1, column=1, pady=2, padx=5)

        tk.Label(input_frame, text="Telefon:").grid(
            row=2, column=0, sticky='w', pady=2
        )
        self.telefon_entry = tk.Entry(input_frame)
        self.telefon_entry.grid(row=2, column=1, pady=2, padx=5)

        button_frame = tk.Frame(input_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(
            button_frame, text="Ekle", command=self.add_uye
        ).pack(side='left', padx=5)
        tk.Button(
            button_frame, text="Güncelle", command=self.update_uye
        ).pack(side='left', padx=5)
        tk.Button(
            button_frame, text="Sil", command=self.delete_uye
        ).pack(side='left', padx=5)
        tk.Button(
            button_frame, text="Temizle", command=self.clear_entries
        ).pack(side='left', padx=5)

        self.tree = ttk.Treeview(
            tree_frame, columns=("ID", "Ad Soyad", "Telefon"), show='headings'
        )
        self.tree.heading("ID", text="ID")
        self.tree.heading("Ad Soyad", text="Adı Soyadı")
        self.tree.heading("Telefon", text="Telefon")
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_item_select)
        self.load_data()


    def db_interaction(self, procedure_name, params=None, fetch=None):
        conn = get_db_connection()
        if not conn:
            return None if fetch else False
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.callproc(procedure_name, params or [])
            if fetch:
                for result in cursor.stored_results():
                    return result.fetchall()
            conn.commit()
            return True
        except mysql.connector.Error as err:
            messagebox.showerror("Veritabanı Hatası", f"İşlem başarısız: {err}")
            return None if fetch else False
        finally:
            if conn.is_connected():
                conn.close()


    def load_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        uye_listesi = self.db_interaction('spGetAllUyeler', fetch='all')
        if uye_listesi:
            for uye in uye_listesi:
                self.tree.insert(
                    "", "end", values=(uye['UyeId'], uye['AdSoyad'], uye['Telefon'])
                )


    def add_uye(self):
        ad_soyad = self.ad_entry.get()
        telefon = self.telefon_entry.get()
        if not ad_soyad or not telefon:
            messagebox.showwarning(
                "Uyarı", "Ad soyad ve telefon boş bırakılamaz."
            )
            return
        if self.db_interaction('spInsertUye', [ad_soyad, telefon]):
            messagebox.showinfo("Başarılı", "Üye eklendi.")
            self.load_data()
            self.clear_entries()


    def update_uye(self):
        if not self.id_entry.get():
            messagebox.showwarning(
                "Uyarı", "Lütfen güncellenecek üyeyi seçin."
            )
            return
        params = [
            int(self.id_entry.get()), self.ad_entry.get(), self.telefon_entry.get()
        ]
        if self.db_interaction('spUpdateUye', params):
            messagebox.showinfo("Başarılı", "Üye güncellendi.")
            self.load_data()
            self.clear_entries()


    def delete_uye(self):
        if not self.id_entry.get():
            messagebox.showwarning("Uyarı", "Lütfen silinecek üyeyi seçin.")
            return
        if messagebox.askyesno("Onay", "Bu üyeyi silmek istediğinizden emin misiniz?"):
            if self.db_interaction('spDeleteUye', [int(self.id_entry.get())]):
                messagebox.showinfo("Başarılı", "Üye silindi.")
                self.load_data()
                self.clear_entries()


    def clear_entries(self):
        for entry in [self.ad_entry, self.telefon_entry]:
            entry.delete(0, 'end')
        self.id_entry.config(state='normal')
        self.id_entry.delete(0, 'end')
        self.id_entry.config(state='readonly')
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])


    def on_item_select(self, event):
        if not self.tree.selection():
            return
        item = self.tree.item(self.tree.selection()[0], 'values')
        self.clear_entries()
        self.id_entry.config(state='normal')
        self.id_entry.insert(0, item[0])
        self.id_entry.config(state='readonly')
        self.ad_entry.insert(0, item[1])
        self.telefon_entry.insert(0, item[2])