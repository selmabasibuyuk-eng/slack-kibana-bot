import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ----------------------------------------------------
# 📌 KONFİGÜRASYON VE GRAFANA AYARLARI
# ----------------------------------------------------
GRAFANA_URL = "https://grafana.srv.team"
GRAFANA_TOKEN = "glsa_MYk8JCUJ3PUWcAQpiBtKzQmy6FHy9V5X_b32c2833"  # Aldığınız Token'ı buraya ekleyin
DATASOURCE_ID = "136"                 # VictoriaMetrics ID

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

# 🔴 429 Hata Oranı Eşik Değeri (%10 ve üzeri)
ERROR_429_THRESHOLD_PERCENT = 10.0

# 🎯 Kontrol Edilecek Endpoint'ler
ENDPOINTS = [
    {"name": "Search", "label": "search"},
    {"name": "Hotel Page", "label": "hotel_page"},
    {"name": "Prebook", "label": "prebook"}
]

HEADERS = {
    "Authorization": f"Bearer {GRAFANA_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def send_slack_message(text):
    if not SLACK_WEBHOOK_URL:
        print("⚠️ Slack Webhook URL tanımlanmamış.")
        return
    payload = {"text": text}
    try:
        res = requests.post(SLACK_WEBHOOK_URL, json=payload, headers={'Content-Type': 'application/json'}, verify=False)
        if res.status_code == 200:
            print("💬 Slack bildirimi başarıyla gönderildi.")
        else:
            print(f"❌ Slack bildirimi başarısız ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"❌ Slack bağlantı hatası: {e}")

def query_prometheus_metric(promql_query):
    url = f"{GRAFANA_URL}/api/datasources/proxy/{DATASOURCE_ID}/api/v1/query"
    try:
        response = requests.get(url, params={"query": promql_query}, headers=HEADERS, verify=False)
        if response.status_code == 200:
            data = response.json()
            results = data.get("data", {}).get("result", [])
            if results:
                return float(results[0].get("value", [0, 0])[1])
        else:
            print(f"❌ Grafana Query Hatası ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"❌ Sorgu çalıştırılırken hata oluştu: {e}")
    return 0.0

def run_grafana_429_check():
    flagged_endpoints = []

    print("🔍 VictoriaMetrics/Grafana üzerinden 429 Hata Analizi başlatılıyor...\n")

    for ep in ENDPOINTS:
        endpoint_name = ep["name"]
        endpoint_label = ep["label"]

        # 💡 PromQL Sorguları (Son 24 Saat)
        total_query = f'sum(increase(http_requests_total{{endpoint="{endpoint_label}"}}[24h]))'
        error_429_query = f'sum(increase(http_requests_total{{endpoint="{endpoint_label}", status="429"}}[24h]))'

        total_requests = query_prometheus_metric(total_query)
        error_429_count = query_prometheus_metric(error_429_query)

        if total_requests > 0:
            error_429_rate = (error_429_count / total_requests) * 100

            print(f"📊 [{endpoint_name}]")
            print(f"   • Toplam İstek: {int(total_requests):,}")
            print(f"   • 429 Hata Sayısı: {int(error_429_count):,}")
            print(f"   • 429 Hata Oranı: %{error_429_rate:.2f}\n")

            if error_429_rate >= ERROR_429_THRESHOLD_PERCENT:
                msg = (
                    f"📌 *Endpoint:* `{endpoint_name}`\n"
                    f"  • *Toplam İstek:* `{int(total_requests):,}`\n"
                    f"  • 🟡 *429 Hata Sayısı:* `{int(error_429_count):,}`\n"
                    f"  • 🚨 *429 Hata Oranı:* %{error_429_rate:.2f} (Eşik: %{ERROR_429_THRESHOLD_PERCENT:.1f})"
                )
                flagged_endpoints.append(msg)
        else:
            print(f"⚠️ [{endpoint_name}] Son 24 saatte veri bulunamadı veya metrik ismi eşleşmedi.\n")

    if flagged_endpoints:
        print(f"⚠️ %{ERROR_429_THRESHOLD_PERCENT} 429 hata eşiğini aşan {len(flagged_endpoints)} endpoint tespit edildi. Slack'e gönderiliyor...")
        alert_text = f"🚨 *Grafana 429 (Rate Limit) Hata Uyarısı (Son 24 Saat)*\n"
        alert_text += f"Aşağıdaki endpoint'lerde 429 hata oranı **%{ERROR_429_THRESHOLD_PERCENT} ve üzerinde** çıkmıştır:\n\n"
        alert_text += "\n\n----------------------------------------\n\n".join(flagged_endpoints)
        
        send_slack_message(alert_text)
    else:
        print(f"✅ Son 24 saatte hiçbir endpoint %{ERROR_429_THRESHOLD_PERCENT} 429 hata eşiğini aşmadı.")

if __name__ == "__main__":
    run_grafana_429_check()
