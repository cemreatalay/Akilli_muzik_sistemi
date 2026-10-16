import "bootstrap/dist/css/bootstrap.min.css";
import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:5000";

function App() {
  const [enerji, setEnerji] = useState(5);
  const [stres, setStres] = useState(5);
  const [saat, setSaat] = useState(12);

  const [sonuc, setSonuc] = useState("");
  const [sanatci, setSanatci] = useState("");
  const [resim, setResim] = useState("");
  const [bgColor, setBgColor] = useState("#1a1a2e");

  const [gecmis, setGecmis] = useState([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(false);

  const gecmisiGetir = async () => {
    try {
      setHistoryLoading(true);

      const response = await fetch(`${API_URL}/history`);
      const data = await response.json();

      if (Array.isArray(data)) {
        setGecmis(data);
      } else {
        setGecmis([]);
      }
    } catch (error) {
      console.error("Geçmiş alınamadı:", error);
      setGecmis([]);
    } finally {
      setHistoryLoading(false);
    }
  };

  const tahminEt = async () => {
    setLoading(true);

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          enerji: Number(enerji),
          stres: Number(stres),
        }),
      });

      const data = await response.json();

      if (data.status === "success") {
        setSonuc(data.sonuc || "");
        setSanatci(data.sanatci || "");
        setResim(data.resim || "");

        if (data.renk) {
          setBgColor(data.renk);
        }

        await gecmisiGetir();
      } else {
        alert("Hata: " + data.message);
      }
    } catch (error) {
      console.error("Bağlantı hatası:", error);
      alert("Backend sunucusuna bağlanılamadı!");
    } finally {
      setLoading(false);
    }
  };

  const gecmisiTemizle = async () => {
    try {
      const response = await fetch(`${API_URL}/clear-history`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (data.status === "success") {
        setGecmis([]);
      } else {
        alert("Hata: " + data.message);
      }
    } catch (error) {
      console.error("Geçmiş temizlenemedi:", error);
      alert("Geçmiş temizlenemedi!");
    }
  };

  useEffect(() => {
    gecmisiGetir();
  }, []);

  return (
    <div className="App" style={{ backgroundColor: bgColor }}>
      <div className="container py-5">
        <h1 className="main-title">🎵 Akıllı Müzik Öneri Sistemi</h1>

        <div className="row justify-content-center">
          <div className="col-lg-7 col-md-9">
            <div className="card p-4 mb-4">
              <div className="mb-4 input-group">
                <label className="form-label">
                  Enerji Seviyesi: <strong>{enerji}</strong>
                </label>
                <input
                  type="range"
                  className="form-range"
                  min="1"
                  max="10"
                  value={enerji}
                  onChange={(e) => setEnerji(Number(e.target.value))}
                />
              </div>

              <div className="mb-4 input-group">
                <label className="form-label">
                  Stres Seviyesi: <strong>{stres}</strong>
                </label>
                <input
                  type="range"
                  className="form-range"
                  min="1"
                  max="10"
                  value={stres}
                  onChange={(e) => setStres(Number(e.target.value))}
                />
              </div>

              <div className="mb-4 input-group">
                <label className="form-label">
                  Saat: <strong>{saat}</strong>
                </label>
                <input
                  type="range"
                  className="form-range"
                  min="0"
                  max="23"
                  value={saat}
                  onChange={(e) => setSaat(Number(e.target.value))}
                />
              </div>

              <button
                className="btn btn-primary w-100"
                onClick={tahminEt}
                disabled={loading}
              >
                {loading ? "Hesaplanıyor..." : "🎧 Müzik Türü Öner"}
              </button>
            </div>

            {sonuc && (
              <div className="result-card text-center">
                <h5 className="text-uppercase fw-bold mb-3">
                  {sonuc} ÖNERİSİ
                </h5>

                {resim && (
                  <img
                    src={resim}
                    alt={sanatci}
                    className="artist-image"
                    onError={(e) => {
                      e.currentTarget.style.display = "none";
                    }}
                  />
                )}

                <h2>
                  Önerilen Tür:{" "}
                  <span className="highlight">{sonuc.toUpperCase()}</span>
                </h2>

                <h3>
                  Önerilen Sanatçı:
                  <span className="artist-name">
                    {sanatci || "Sanatçı bulunamadı"}
                  </span>
                </h3>

                <div className="mt-2" style={{ color: "#d1d5db" }}>
                  Şu an senin için en iyisi bu!
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="row justify-content-center mt-5">
          <div className="col-lg-10">
            <div className="card p-4">
              <h3 className="text-center mb-4">📜 Geçmiş Tahminler</h3>

              <div className="text-center mb-3">
                <button
                  className="btn btn-danger"
                  onClick={gecmisiTemizle}
                  disabled={gecmis.length === 0}
                >
                  🗑️ Geçmişi Temizle
                </button>
              </div>

              <div className="table-responsive">
                <table className="table table-striped table-hover align-middle">
                  <thead className="table-dark">
                    <tr>
                      <th>#</th>
                      <th>Enerji</th>
                      <th>Stres</th>
                      <th>Tür</th>
                      <th>Sanatçı</th>
                    </tr>
                  </thead>

                  <tbody>
                    {historyLoading ? (
                      <tr>
                        <td colSpan="5" className="text-center">
                          Geçmiş yükleniyor...
                        </td>
                      </tr>
                    ) : gecmis.length > 0 ? (
                      gecmis.map((item, index) => (
                        <tr key={item.id || index}>
                          <td>{index + 1}</td>
                          <td>{item.enerji}</td>
                          <td>{item.stres}</td>

                          <td>
                            <span className="badge bg-info text-dark">
                              {item.tahmin_edilen_tur}
                            </span>
                          </td>

                          <td>{item.onerilen_sanatci || "-"}</td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="5" className="text-center">
                          Henüz kayıt bulunmuyor.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;