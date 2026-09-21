import json
import os
from kibana_client import KibanaClient
from analyzer import TrafficAnalyzer

CACHE_FILE = "kibana_cache.json"

def get_kibana_data():
    if os.path.exists(CACHE_FILE):
        print("⚡ Önbellek bulundu, veriler 'kibana_cache.json' dosyasından okunuyor...")
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    
    print("🌐 Kibana API'sinden CANLI veri çekiliyor...")
    client = KibanaClient()
    
    # Son 3 günün trafiği
    current_3d = client.fetch_traffic_data(time_from="now-3d", time_to="now")
    
    # Önceki 3 günün trafiği (3 gün öncesinden 6 gün öncesine)
    previous_3d = client.fetch_traffic_data(time_from="now-6d", time_to="now-3d")
    
    # Prebook hata detayları
    prebook_errors = client.fetch_prebook_error_details(time_from="now-3d", time_to="now")
    
    data = {
        "current_3d": current_3d,
        "previous_3d": previous_3d,
        "prebook_errors": prebook_errors
    }
    
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("💾 Gerçek Kibana yanıtı 'kibana_cache.json' olarak kaydedildi.")
    
    return data

def main():
    print("=== KIBANA MONITORING BOT BAŞLATILIYOR ===")
    
    try:
        data = get_kibana_data()
        
        analyzer = TrafficAnalyzer(
            data["current_3d"], 
            data["previous_3d"], 
            data["prebook_errors"]
        )
        analyzer.analyze()
        
        print("=== ANALİZ BİTTİ ===")
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")

if __name__ == "__main__":
    main()
