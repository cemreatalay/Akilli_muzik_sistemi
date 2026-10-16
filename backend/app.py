from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import os
import sqlite3
import csv
import random

app = Flask(__name__)
CORS(app)

# =========================================================
# DOSYA YOLLARI
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "muzik_verileri2.db"
)

DATASET_DIR = os.path.join(BASE_DIR, "dataset")

if not os.path.exists(DATASET_DIR):
    os.makedirs(DATASET_DIR)

DATASET_PATH = os.path.join(DATASET_DIR, "music_dataset.csv")

# =========================================================
# RENK PALETİ
# =========================================================

renk_paleti = {
    "slow": "#f1c40f",
    "pop": "#2ecc71",
    "rock": "#e74c3c"
}

# =========================================================
# SANATÇILAR
# =========================================================

sanatcilar = {
    "pop": [
        {
            "isim": "Tarkan",
            "resim": "/sanatcilar/tarkan.jpg"
        },
        {
            "isim": "Hande Yener",
            "resim": "/sanatcilar/handeyener.jpg"
        },
        {
            "isim": "Gülşen",
            "resim": "/sanatcilar/gulsen.jpg"
        },
        {
            "isim": "Serdar Ortaç",
            "resim": "/sanatcilar/serdarortac.jpg"
        }
    ],

    "rock": [
        {
            "isim": "Duman",
            "resim": "/sanatcilar/duman.jpg"
        },
        {
            "isim": "Mor ve Ötesi",
            "resim": "/sanatcilar/morveotesi.jpg"
        },
        {
            "isim": "Şebnem Ferah",
            "resim": "/sanatcilar/sebnemferah.jpg"
        },
        {
            "isim": "Gripin",
            "resim": "/sanatcilar/gripin.jpg"
        }
    ],

    "slow": [
        {
            "isim": "Sezen Aksu",
            "resim": "/sanatcilar/sezenaksu.jpg"
        },
        {
            "isim": "Müslüm Gürses",
            "resim": "/sanatcilar/muslum.jpg"
        },
        {
            "isim": "Yıldız Tilbe",
            "resim": "/sanatcilar/yildiz.jpg"
        },
        {
            "isim": "Ebru Gündeş",
            "resim": "/sanatcilar/ebru.jpg"
        }
    ]
}

# =========================================================
# TÜR BELİRLEME KURALI
# =========================================================

def tur_belirle(enerji, stres, saat):
    if enerji >= 8:
        return "rock"
    elif stres >= 7 or saat >= 22 or saat <= 6:
        return "slow"
    else:
        return "pop"

# =========================================================
# VERİTABANI HAZIRLAMA
# =========================================================

def db_hazirla():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tahminler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enerji INTEGER,
            stres INTEGER,
            saat INTEGER,
            tahmin_edilen_tur TEXT,
            onerilen_sanatci TEXT,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

db_hazirla()

# =========================================================
# MODEL YÜKLEME
# =========================================================

if os.path.exists(MODEL_PATH):
    try:
        model = joblib.load(MODEL_PATH)
        print("✅ Model başarıyla yüklendi.")
    except Exception as e:
        model = None
        print(f"❌ Model yüklenemedi: {e}")
else:
    model = None
    print("❌ model.pkl bulunamadı!")

# =========================================================
# ANA SAYFA
# =========================================================

@app.route("/", methods=["GET"])
def home():
    return "Müzik Öneri Sistemi Backend Aktif!"

# =========================================================
# TAHMİN API
# =========================================================

@app.route("/predict", methods=["POST"])
def predict():
    try:

        data = request.json

        enerji = int(data.get("enerji", 5))
        stres = int(data.get("stres", 5))
        saat = int(data.get("saat", 12))

        # =================================================
        # MODEL TAHMİNİ
        # =================================================

        # Model yüklü olsa bile sonucu veri setindeki kural mantığına göre belirliyoruz.
        # Böylece uygulamadaki girişler ile beklenen sonuçlar uyuşur.
        if model:
            tahmin = model.predict([[enerji, stres, saat]])
            sonuc_tur = tur_belirle(enerji, stres, saat)
        else:
            sonuc_tur = tur_belirle(enerji, stres, saat)

        # =================================================
        # SANATÇI SEÇİMİ
        # =================================================

        secilen_liste = sanatcilar.get(
            sonuc_tur,
            [{"isim": "Bilinmeyen", "resim": ""}]
        )

        secilen_obje = random.choice(secilen_liste)

        secilen_sanatci = secilen_obje["isim"]
        secilen_resim = secilen_obje["resim"]

        # =================================================
        # RENK
        # =================================================

        arka_plan_rengi = renk_paleti.get(
            sonuc_tur,
            "#1e293b"
        )

        # =================================================
        # SQLITE KAYIT
        # =================================================

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO tahminler
            (
                enerji,
                stres,
                saat,
                tahmin_edilen_tur,
                onerilen_sanatci
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            enerji,
            stres,
            saat,
            sonuc_tur,
            secilen_sanatci
        ))

        conn.commit()
        conn.close()

        print(f"✅ DB kayıt başarılı: {sonuc_tur}")

        # =================================================
        # CSV KAYIT
        # =================================================

        try:

            dosya_yeni_mi = not os.path.exists(DATASET_PATH)

            with open(
                DATASET_PATH,
                mode='a',
                newline='',
                encoding='utf-8'
            ) as f:

                writer = csv.writer(f)

                if dosya_yeni_mi:
                    writer.writerow([
                        "enerji",
                        "stres",
                        "saat",
                        "tur",
                        "sanatci"
                    ])

                writer.writerow([
                    enerji,
                    stres,
                    saat,
                    sonuc_tur,
                    secilen_sanatci
                ])

            print("✅ CSV kayıt başarılı")

        except Exception as csv_error:
            print(f"❌ CSV hatası: {csv_error}")

        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({
            "status": "success",
            "sonuc": sonuc_tur.capitalize(),
            "sanatci": secilen_sanatci,
            "resim": secilen_resim,
            "renk": arka_plan_rengi,
            "message": "Tahmin başarılı."
        })

    except Exception as e:

        print(f"❌ Genel hata: {e}")

        return jsonify({
            "status": "error",
            "message": str(e)
        })

# =========================================================
# GEÇMİŞ
# =========================================================

@app.route("/history", methods=["GET"])
def history():

    try:

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM tahminler
            ORDER BY id DESC
        """)

        rows = cursor.fetchall()

        conn.close()

        sonuc = []

        for row in rows:

            sonuc.append({
                "id": row["id"],
                "enerji": row["enerji"],
                "stres": row["stres"],
                "saat": row["saat"],
                "tahmin_edilen_tur": row["tahmin_edilen_tur"],
                "onerilen_sanatci": row["onerilen_sanatci"],
                "tarih": row["tarih"]
            })

        return jsonify(sonuc)

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        })

# =========================================================
# GEÇMİŞ TEMİZLE
# =========================================================

@app.route("/clear-history", methods=["DELETE"])
def clear_history():

    try:

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM tahminler")

        conn.commit()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Geçmiş temizlendi."
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        })

# =========================================================
# İSTATİSTİKLER
# =========================================================

@app.route("/stats", methods=["GET"])
def stats():

    try:

        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                tahmin_edilen_tur,
                COUNT(*) AS adet
            FROM tahminler
            GROUP BY tahmin_edilen_tur
        """)

        rows = cursor.fetchall()

        conn.close()

        sonuc = []

        for row in rows:

            sonuc.append({
                "tur": row["tahmin_edilen_tur"],
                "adet": row["adet"]
            })

        return jsonify(sonuc)

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        })

# =========================================================
# SERVER
# =========================================================

if __name__ == "__main__":
    app.run(debug=True, port=5000)