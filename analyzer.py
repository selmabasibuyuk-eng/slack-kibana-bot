import requests
from config import SLACK_WEBHOOK_URL, ERROR_THRESHOLD

def send_slack_alert(message: str):
    if not SLACK_WEBHOOK_URL:
        print("[MOCK SLACK ALERT]:", message)
        return

    payload = {"text": message}
    requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)

def analyze_and_report(kibana_client):
    print("1. Aşama: Search sayıları ve HTTP statüleri analiz ediliyor...")
    data_stage1 = kibana_client.fetch_search_and_status_counts()
    
    total_searches = 0
    total_errors = 0
    
    buckets = data_stage1.get("aggregations", {}).get("by_endpoint", {}).get("buckets", [])
    for bucket in buckets:
        total_searches += bucket.get("doc_count", 0)
        status_buckets = bucket.get("by_http_status", {}).get("buckets", [])
        for st in status_buckets:
            if str(st.get("key")).startswith(("4", "5")):
                total_errors += st.get("doc_count", 0)

    error_rate = (total_errors / total_searches * 100) if total_searches > 0 else 0.0
    print(f"Toplam Arama: {total_searches}, Toplam Hata: {total_errors}, Hata Oranı: %{error_rate:.2f}")

    if error_rate >= ERROR_THRESHOLD:
        print(f"Eşik değer (%{ERROR_THRESHOLD}) aşıldı! 2. Aşamaya geçiliyor...")
        
        data_stage2 = kibana_client.fetch_prebook_errors()
        error_buckets = data_stage2.get("aggregations", {}).get("by_error", {}).get("buckets", [])
        
        top_errors = []
        for err in error_buckets[:3]:
            top_errors.append(f"- *{err.get('key')}*: {err.get('doc_count')} adet")
            
        error_detail_str = "\n".join(top_errors) if top_errors else "Detaylı hata kaydı bulunamadı."
        
        alert_msg = (
            f"🚨 *KIBANA KRİTİK HATA UYARISI*\n"
            f"• *Hata Oranı:* %{error_rate:.2f}\n"
            f"• *Toplam Arama:* {total_searches}\n"
            f"• *Hata Sayısı:* {total_errors}\n\n"
            f"🔍 *En Çok Alınan Prebook Hataları (Son 14 Gün):*\n{error_detail_str}"
        )
        
        send_slack_alert(alert_msg)
    else:
        print("Sistem sağlıklı, threshold aşılmadı.")
