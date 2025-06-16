import tkinter as tk
import uye_yonetimi
import rezervasyon_yonetimi
import gunluk_program  # Yeni dosyamızı import ediyoruz

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Halı Saha Yönetim Paneli - Ana Menü")
        
        # Pencereyi ortalama kodu...
        window_width, window_height = 800, 600
        screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        
        # Arayüz elemanları...
        left_frame = tk.Frame(root, width=200, bg='gray20')
        left_frame.pack(side='left', fill='y')
        right_frame = tk.Frame(root, bg='gray90')
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Butonlar güncellendi
        menu_buttons = {
            "Üye Yönetimi": self.open_uye_window,
            "Rezervasyon İşlemleri": self.open_rezervasyon_window,
            "Günlük Program": self.open_gunluk_program_window, # YENİ BUTON
        }
        
        for text, command in menu_buttons.items():
            button = tk.Button(
                left_frame, text=text, font=("Arial", 12), bg='gray30', 
                fg='white', command=command, relief='flat', padx=20, pady=10
            )
            button.pack(pady=5, padx=10, fill='x')
            
        tk.Label(
            right_frame, text="Halısaha Yönetim Paneline Hoş Geldiniz!",
            font=("Arial", 24), bg='gray90'
        ).pack(expand=True)

    def open_uye_window(self):
        new_window = tk.Toplevel(self.root)
        uye_yonetimi.UyeApp(new_window)

    def open_rezervasyon_window(self):
        new_window = tk.Toplevel(self.root)
        rezervasyon_yonetimi.RezervasyonApp(new_window)

    # Yeni fonksiyon
    def open_gunluk_program_window(self):
        new_window = tk.Toplevel(self.root)
        gunluk_program.GunlukProgramApp(new_window)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()