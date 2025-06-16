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


class GunlukProgramApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Günlük Program")
        self.root.geometry("800x600")

        # --- Arayüz ---
        top_frame = tk.Frame(root, pady=10, padx=10)
        top_frame.pack(fill='x')
        tree_frame = tk.Frame(root, pady=10, padx=10)
        tree_frame.pack(fill='both', expand=True)

        tk.Label(top_frame, text="Tarih Seç:").pack(side='left')
        self.tarih_entry = tk.Entry(top_frame)
        self.tarih_entry.insert(0, date.today().strftime('%Y-%m-%d'))
        self.tarih_entry.pack(side='left', padx=5)
        tk.Button(top_frame, text="Göster", command=self.load_data).pack(side='left')

        self.tree = ttk.Treeview(
            tree_frame, columns=("Saat", "Saha A", "Saha B"), show='headings'
        )
        self.tree.heading("Saat", text="Saat")
        self.tree.heading("Saha A", text="Kapalı Saha A")
        self.tree.heading("Saha B", text="Açık Saha B")
        self.tree.pack(fill='both', expand=True)

        # Renklendirme için etiketler (tag)
        self.tree.tag_configure('dolu', background='#f8d7da')  # Dolu için açık kırmızı
        self.tree.tag_configure('bos', foreground='green')     # Boş için yeşil yazı

        self.load_data()  # Pencere açıldığında bugünün verilerini yükle

    def load_data(self):
        # Önce mevcut tabloyu temizle
        for i in self.tree.get_children():
            self.tree.delete(i)

        secilen_tarih = self.tarih_entry.get()
        try:
            # Tarih formatının doğru olup olmadığını kontrol et
            datetime.strptime(secilen_tarih, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Hata", "Lütfen YYYY-MM-DD formatında geçerli bir tarih girin.")
            return

        conn = get_db_connection()
        if not conn:
            return
        try:
            cursor = conn.cursor(dictionary=True)
            # Seçilen tarihe ait tüm rezervasyonları çek
            sql_query = (
                "SELECT r.BaslangicSaati, s.SahaAdi, u.AdSoyad "
                "FROM Rezervasyonlar r "
                "JOIN Sahalar s ON r.SahaId = s.SahaId "
                "JOIN Uyeler u ON r.UyeId = u.UyeId "
                "WHERE r.RezervasyonTarihi = %s"
            )
            cursor.execute(sql_query, (secilen_tarih,))
            rez_data = cursor.fetchall()

            # Saatlik planı oluştur (tüm saatler başlangıçta 'BOŞ' olarak ayarlı)
            saatlik_plan = {
                f"{saat:02d}:00": {
                    'Kapalı Saha A': 'BOŞ',
                    'Açık Saha B': 'BOŞ'
                } for saat in range(9, 24) # 09:00'dan 23:00'a kadar
            }

            # Veritabanından gelen rezervasyonlarla planı güncelle
            for rez in rez_data:
                # Veritabanından gelen saat 'timedelta' olabilir, onu string'e çeviriyoruz
                saat_str = str(rez['BaslangicSaati'])[:5]
                saha_adi = rez['SahaAdi']
                if saat_str in saatlik_plan and saha_adi in saatlik_plan[saat_str]:
                    saatlik_plan[saat_str][saha_adi] = rez['AdSoyad']

            # Hazırlanan planı tabloya (Treeview) yazdır
            for saat, sahalar in saatlik_plan.items():
                bitis_saat = f"{int(saat.split(':')[0]) + 1:02d}:00"
                saha_a_durum = sahalar['Kapalı Saha A']
                saha_b_durum = sahalar['Açık Saha B']
                
                # Değerlere göre tag ata
                saha_a_tag = 'dolu' if saha_a_durum != 'BOŞ' else 'bos'
                saha_b_tag = 'dolu' if saha_b_durum != 'BOŞ' else 'bos'
                
                # Her hücre için ayrı renklendirme doğrudan desteklenmiyor,
                # bu yüzden satırı genel bir etiketle ekleyeceğiz.
                # Önemli olan dolu saatlerin belli olması.
                self.tree.insert(
                    "", "end",
                    values=(f"{saat} - {bitis_saat}", saha_a_durum, saha_b_durum),
                    tags=(saha_a_tag if saha_a_durum != 'BOŞ' else saha_b_tag,) # Herhangi biri doluysa satırı işaretle
                )

        except mysql.connector.Error as err:
            messagebox.showerror("Veri Yükleme Hatası", f"Hata: {err}")
        finally:
            if conn.is_connected():
                conn.close()


# Bu dosyanın tek başına test edilmesi için
if __name__ == "__main__":
    root = tk.Tk()
    app = GunlukProgramApp(root)
    root.mainloop()