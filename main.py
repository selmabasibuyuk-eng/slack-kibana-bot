import json
import os
from kibana_client import KibanaClient
from analyzer import TrafficAnalyzer

CACHE_FILE = "kibana_cache.json"

def get_kibana_data():
    # Cache dosyası varsa dosyadan oku
    if os.path.exists(CACHE_FILE):
        print("⚡ Önbellek bulundu, veriler 'kibana_cache.json' dosyasından okunuyor...")
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # Cache dosyası yoksa Kibana'dan CANLI veriyi çek ve dosyaya kaydet
    print("🌐 Kibana API'sinden CANLI veri çekiliyor...")
    client = KibanaClient()
    
    current_3d = client.get_traffic_data(days_back=3)
    previous_3d = client.get_previous_traffic_data(days_back=6, days_offset=3)
    prebook_errors = client.get_prebook_errors(days_back=3)
    
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
