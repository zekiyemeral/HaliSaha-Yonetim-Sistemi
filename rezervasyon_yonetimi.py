import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import date, datetime


# Veritabanı bağlantı fonksiyonu
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
        messagebox.showerror("Bağlantı Hatası", str(err))
        return None


# Ödeme Penceresi Sınıfı
class PaymentWindow:
    def __init__(self, parent, rez_info, callback):
        self.callback = callback
        self.rez_info = rez_info
        self.win = tk.Toplevel(parent)
        self.win.title("Ödeme Ekranı")

        tk.Label(self.win, text="Rezervasyon ID:", padx=10, pady=5)\
            .grid(row=0, column=0, sticky="w")
        tk.Label(self.win, text=self.rez_info['id'],
                 font=("Arial", 10, "bold"))\
            .grid(row=0, column=1, sticky="w")

        tk.Label(self.win, text="Müşteri:", padx=10, pady=5)\
            .grid(row=1, column=0, sticky="w")
        tk.Label(self.win, text=self.rez_info['uye'])\
            .grid(row=1, column=1, sticky="w")

        tk.Label(self.win, text="Tutar:", padx=10, pady=5)\
            .grid(row=2, column=0, sticky="w")
        tk.Label(self.win, text=f"{self.rez_info['tutar']:.2f} TL",
                 font=("Arial", 10, "bold"))\
            .grid(row=2, column=1, sticky="w")

        tk.Label(self.win, text="Ödeme Türü:", padx=10, pady=5)\
            .grid(row=3, column=0, sticky="w")
        self.odeme_turu_combo = ttk.Combobox(
            self.win, state="readonly", values=["Nakit", "Kredi Kartı"]
        )
        self.odeme_turu_combo.grid(row=3, column=1, padx=5, pady=5)
        self.odeme_turu_combo.current(0)

        tk.Button(
            self.win, text="Ödemeyi Onayla", command=self.make_payment,
            bg="blue", fg="white"
        ).grid(row=4, column=1, padx=5, pady=10, sticky="e")

    def make_payment(self):
        odeme_turu = self.odeme_turu_combo.get()
        if not odeme_turu:
            messagebox.showwarning("Uyarı", "Lütfen bir ödeme türü seçin.")
            return

        conn = get_db_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            args = (self.rez_info['id'], self.rez_info['tutar'], odeme_turu)
            cursor.callproc('spInsertOdeme', args)
            conn.commit()
            messagebox.showinfo("Başarılı", "Ödeme alındı.")
            self.callback()
            self.win.destroy()
        except mysql.connector.Error as err:
            messagebox.showerror("Hata", f"Ödeme kaydedilemedi: {err}")
        finally:
            if conn.is_connected():
                conn.close()


# Ana Rezervasyon Penceresi Sınıfı
class RezervasyonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rezervasyon Yönetimi")
        self.root.geometry("1100x600")

        self.saha_sozluk, self.uye_sozluk = {}, {}

        # Arayüz artık daha basit, tek bir ekrandan oluşuyor
        left_panel = tk.Frame(root, padx=10, pady=10)
        left_panel.pack(side='left', fill='y', anchor='nw')
        right_panel = tk.Frame(root, padx=10, pady=10)
        right_panel.pack(side='right', fill='both', expand=True)

        rez_frame = tk.LabelFrame(
            left_panel, text="Yeni Rezervasyon", padx=10, pady=10
        )
        rez_frame.pack(fill='x')

        # Giriş alanları...
        tk.Label(rez_frame, text="Saha:")\
            .grid(row=0, column=0, pady=2, sticky="w")
        self.saha_combo = ttk.Combobox(
            rez_frame, state="readonly", width=30
        )
        self.saha_combo.grid(row=0, column=1, padx=5, pady=2)
        tk.Label(rez_frame, text="Üye:")\
            .grid(row=1, column=0, pady=2, sticky="w")
        self.uye_combo = ttk.Combobox(
            rez_frame, state="readonly", width=30
        )
        self.uye_combo.grid(row=1, column=1, padx=5, pady=2)
        tk.Label(rez_frame, text="Tarih:")\
            .grid(row=2, column=0, pady=2, sticky="w")
        self.tarih_entry = tk.Entry(rez_frame, width=33)
        self.tarih_entry.insert(0, date.today().strftime('%Y-%m-%d'))
        self.tarih_entry.grid(row=2, column=1, padx=5, pady=2)
        tk.Label(rez_frame, text="Saat:")\
            .grid(row=3, column=0, pady=2, sticky="w")
        saatler = [f"{saat:02d}:00" for saat in range(9, 24)]
        self.saat_combo = ttk.Combobox(
            rez_frame, state="readonly", values=saatler, width=30
        )
        self.saat_combo.grid(row=3, column=1, padx=5, pady=2)
        tk.Button(
            rez_frame, text="Rezervasyon Yap", command=self.add_rezervasyon
        ).grid(row=4, column=1, pady=10, sticky='e')

        # Rezervasyon listesi tablosu...
        columns = ("ID", "Saha", "Uye", "Tarih", "Saat", "Ucret", "Durum")
        self.tree = ttk.Treeview(right_panel, columns=columns, show='headings')
        headings = {
            "ID": "ID", "Saha": "Saha", "Uye": "Üye", "Tarih": "Tarih",
            "Saat": "Saat", "Ucret": "Ücret", "Durum": "Ödeme Durumu"
        }
        for col, text in headings.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, anchor='center', width=120)
        self.tree.pack(fill='both', expand=True)
        self.tree.bind('<Double-1>', self.on_double_click)

        # Renklendirme için etiketler (tag)
        self.tree.tag_configure(
            'odendi', background='#d4edda', foreground='#155724'
        )
        self.tree.tag_configure(
            'odenmedi', background='#f8d7da', foreground='#721c24'
        )

        self.load_combos()
        self.load_rezervasyonlar()

    def db_interaction(self, proc_name, params=None, fetch=None):
        conn = get_db_connection()
        if not conn:
            return None if fetch else False
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.callproc(proc_name, params or [])
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

    def load_combos(self):
        sahalar = self.db_interaction('spGetAllSahalar', fetch='all')
        uyeler = self.db_interaction('spGetAllUyeler', fetch='all')
        if sahalar:
            self.saha_sozluk = {s['SahaAdi']: s for s in sahalar}
            self.saha_combo['values'] = list(self.saha_sozluk.keys())
            if self.saha_combo['values']:
                self.saha_combo.current(0)
        if uyeler:
            self.uye_sozluk = {u['AdSoyad']: u['UyeId'] for u in uyeler}
            self.uye_combo['values'] = list(self.uye_sozluk.keys())
            if self.uye_combo['values']:
                self.uye_combo.current(0)

    def load_rezervasyonlar(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rez_list = self.db_interaction('spGetAllRezervasyonlar', fetch='all')
        if rez_list:
            for r in rez_list:
                saat = f"{r['BaslangicSaati']} - {r['BitisSaati']}"
                tarih = r['RezervasyonTarihi'].strftime('%d-%m-%Y')
                ucret = f"{r['ToplamUcret']:.2f} TL"
                odeme_durumu = r['OdemeDurumu']
                tag = 'odendi' if odeme_durumu == 'Ödendi' else 'odenmedi'
                values = (
                    r['RezervasyonId'], r['SahaAdi'], r['AdSoyad'],
                    tarih, saat, ucret, odeme_durumu
                )
                self.tree.insert("", "end", values=values, tags=(tag,))

    def add_rezervasyon(self):
        saha_adi = self.saha_combo.get()
        uye_adi = self.uye_combo.get()
        tarih_str = self.tarih_entry.get()
        saat = self.saat_combo.get()
        if not all([saha_adi, uye_adi, tarih_str, saat]):
            messagebox.showwarning("Uyarı", "Tüm alanlar doldurulmalıdır.")
            return

        # Çakışma Kontrolü
        conn = get_db_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            query = ("SELECT COUNT(*) FROM Rezervasyonlar WHERE SahaId = %s "
                     "AND RezervasyonTarihi = %s AND BaslangicSaati = %s")
            saha_id = self.saha_sozluk[saha_adi]['SahaId']
            baslangic_saati = f"{saat}"
            cursor.execute(query, (saha_id, tarih_str, baslangic_saati))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror(
                    "Hata", "Seçtiğiniz tarih ve saatte bu saha zaten dolu!"
                )
                return
        finally:
            if conn.is_connected():
                conn.close()

        # Rezervasyon ekleme işlemi
        uye_id = self.uye_sozluk[uye_adi]
        ucret = self.saha_sozluk[saha_adi]['SaatlikUcret']
        bitis_saati = f"{int(saat.split(':')[0]) + 1:02d}:00:00"
        params = [
            saha_id, uye_id, tarih_str, baslangic_saati, bitis_saati, ucret
        ]
        if self.db_interaction('spInsertRezervasyon', params):
            messagebox.showinfo("Başarılı", "Rezervasyon oluşturuldu.")
            self.load_rezervasyonlar()

    def on_double_click(self, event):
        if not self.tree.selection():
            return
        item_values = self.tree.item(self.tree.selection()[0], 'values')
        rez_id, uye_adi, ucret_str, durum = \
            item_values[0], item_values[2], item_values[5], item_values[6]
        if durum == 'Ödendi':
            messagebox.showinfo(
                "Bilgi", "Bu rezervasyonun ödemesi zaten yapılmış."
            )
            return
        rez_info = {
            'id': int(rez_id),
            'uye': uye_adi,
            'tutar': float(ucret_str.replace(' TL', ''))
        }
        PaymentWindow(self.root, rez_info, self.load_rezervasyonlar)


if __name__ == "__main__":
    root = tk.Tk()
    app = RezervasyonApp(root)
    root.mainloop()