import pandas as pd
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import joblib
import os

# Dosya yolları
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "dataset", "music_dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")

# Dataset oku
data = pd.read_csv(DATA_PATH)

# Sütun isimlerinde boşluk varsa temizle
data.columns = data.columns.str.strip()

# Sayısal sütunları kesin olarak sayıya çevir
data["enerji"] = pd.to_numeric(data["enerji"], errors="coerce")
data["stres"] = pd.to_numeric(data["stres"], errors="coerce")
data["saat"] = pd.to_numeric(data["saat"], errors="coerce")

# Tür sütununu temizle
data["tur"] = data["tur"].astype(str).str.strip().str.lower()

# Hatalı / boş satırları sil
data = data.dropna(subset=["enerji", "stres", "saat", "tur"])

# Girdi ve çıktı ayır
X = data[["enerji", "stres", "saat"]]
y = data["tur"]

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Model oluştur ve eğit
model = GaussianNB()
model.fit(X_train, y_train)

# Test tahmini
y_pred = model.predict(X_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)
print("\nAccuracy:")
print(f"%{accuracy * 100:.2f}")

# Confusion Matrix
print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(cm)

# Classification Report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Görsel Confusion Matrix
ConfusionMatrixDisplay.from_predictions(y_test, y_pred)
plt.title("Confusion Matrix")
plt.show()

# Model klasörü yoksa oluştur
os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

# Modeli kaydet
joblib.dump(model, MODEL_PATH)

print("\nModel başarıyla eğitildi ve model/model.pkl olarak kaydedildi.")