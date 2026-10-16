import pandas as pd
import random
import os

# Dosya yolunu senin klasör yapına göre ayarlıyoruz
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_yolu = os.path.join(BASE_DIR, "..", "dataset", "music_dataset.csv")

# Sanatçı listesini buraya ekliyoruz (Backend ile uyumlu)
sanatcilar = {
    "pop": ["Tarkan", "Hande Yener", "Serdar Ortaç", "Gülşen"],
    "rock": ["Duman", "Mor ve Ötesi", "Şebnem Ferah", "Gripin"],
    "slow": ["Sezen Aksu", "Müslüm Gürses", "Ebru Gündeş", "Yıldız Tilbe"]
}

def sentetik_veri_uret(adet=1000):
    yeni_satirlar = []
    
    for _ in range(adet):
        # Rastgele değerler üretiyoruz
        enerji = random.randint(1, 10)
        stres = random.randint(1, 10)
        saat = random.randint(0, 23)
        
        # Tür belirleme mantığı
        if enerji >= 8:
            etiket = "rock"
        elif stres >= 7 or (saat >= 22 or saat <= 6):
            etiket = "slow"
        else:
            etiket = "pop"
            
        # --- YENİ: Sanatçı seçimi eklendi ---
        sanatci = random.choice(sanatcilar[etiket])
            
        # Listeye sanatçıyı da (5. sütun) ekliyoruz
        yeni_satirlar.append([enerji, stres, saat, etiket, sanatci])
    
    # DataFrame oluştururken sütun isimlerini veriyoruz
    sutunlar = ["enerji", "stres", "saat", "tur", "sanatci"]
    df_yeni = pd.DataFrame(yeni_satirlar, columns=sutunlar)
    
    # DİKKAT: mode='w' yaparak eski sanatçısız verileri siliyoruz, 
    # header=True ile başlıkları en başa bir kez yazıyoruz.
    df_yeni.to_csv(csv_yolu, mode='w', index=False, header=True, encoding='utf-8')
    
    print(f"Başarılı: {adet} adet 5 sütunlu veri '{csv_yolu}' dosyasına sıfırdan yazıldı.")

if __name__ == "__main__":
    sentetik_veri_uret(1000)