import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ----------------------------------------------------
# 📌 KONFİGÜRASYON VE GRAFANA INFLUXDB AYARLARI
# ----------------------------------------------------
GRAFANA_URL = "https://grafana.srv.team"
GRAFANA_TOKEN = "glsa_MYk8JCUJ3PUWcAQpiBtKzQmy6FHy9V5X_b32c2833"

INFLUX_DATASOURCE_ID = "299" 
INFLUX_DB_NAME = "partner-ng"

PARTNER_CONTRACT_SLUG = "19527.b2b.a0ae"
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

# 🔴 429 Hata Oranı Eşik Değeri (%10 ve üzeri)
ERROR_429_THRESHOLD_PERCENT = 10.0

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

def run_dynamic_endpoint_check():
    print(f"🔍 InfluxDB ({INFLUX_DB_NAME}) üzerinden [{PARTNER_CONTRACT_SLUG}] için TÜM dinamik URI'ler sorgulanıyor...\n")

    url = f"{GRAFANA_URL}/api/datasources/proxy/{INFLUX_DATASOURCE_ID}/query"

    # 1. Partnerin çağırdığı TÜM URI'ler için toplam istek sayısı (GROUP BY "uri")
    q_total = (
        f'SELECT sum("count") FROM "partner.api.ext.prod.response.time" '
        f'WHERE contract_slug =~ /{PARTNER_CONTRACT_SLUG}/ AND time > now() - 24h '
        f'GROUP BY "uri"'
    )

    # 2. Partnerin çağırdığı TÜM URI'ler için 429 sayısı
    q_429 = (
        f'SELECT sum("count") FROM "partner.api.ext.prod.response.time" '
        f'WHERE status = \'429\' AND contract_slug =~ /{PARTNER_CONTRACT_SLUG}/ AND time > now() - 24h '
        f'GROUP BY "uri"'
    )

    res_total = requests.get(url, params={"q": q_total, "db": INFLUX_DB_NAME}, headers=HEADERS, verify=False)
    res_429 = requests.get(url, params={"q": q_429, "db": INFLUX_DB_NAME}, headers=HEADERS, verify=False)

    total_data = {}
    error_429_data = {}

    # Toplam İstek Verilerini Parse Et
    if res_total.status_code == 200:
        series_list = res_total.json().get("results", [])[0].get("series", [])
        for s in series_list:
            uri = s.get("tags", {}).get("uri", "tanımsız_uri")
            val = s.get("values", [[0, 0]])[0][1] or 0
            total_data[uri] = float(val)

    # 429 Hata Verilerini Parse Et
    if res_429.status_code == 200:
        series_list = res_429.json().get("results", [])[0].get("series", [])
        for s in series_list:
            uri = s.get("tags", {}).get("uri", "tanımsız_uri")
            val = s.get("values", [[0, 0]])[0][1] or 0
            error_429_data[uri] = float(val)

    if not total_data:
        print(f"⚠️ Son 24 saatte [{PARTNER_CONTRACT_SLUG}] partnerine ait hiçbir URI kaydı bulunamadı.")
        return

    flagged_endpoints = []

    print("📊 --- DİNANİK URI ANALİZİ (Son 24 Saat) ---")
    for uri, total_count in total_data.items():
        err_count = error_429_data.get(uri, 0.0)
        rate = (err_count / total_count * 100) if total_count > 0 else 0.0

        print(f"\n🔗 URI: {uri}")
        print(f"   • Toplam İstek : {int(total_count):,}")
        print(f"   • 429 Sayısı   : {int(err_count):,}")
        print(f"   • 429 Oranı    : %{rate:.2f}")

        if rate >= ERROR_429_THRESHOLD_PERCENT:
            msg = (
                f"📌 *Partner:* `{PARTNER_CONTRACT_SLUG}` | *URI:* `{uri}`\n"
                f"  • *Toplam İstek:* `{int(total_count):,}`\n"
                f"  • 🟡 *429 Hata Sayısı:* `{int(err_count):,}`\n"
                f"  • 🚨 *429 Hata Oranı:* %{rate:.2f} (Eşik: %{ERROR_429_THRESHOLD_PERCENT:.1f})"
            )
            flagged_endpoints.append(msg)

    print("\n------------------------------------------------")
    if flagged_endpoints:
        print(f"\n⚠️ %{ERROR_429_THRESHOLD_PERCENT} eşiğini aşan {len(flagged_endpoints)} URI tespit edildi. Slack bildirimi gönderiliyor...")
        alert_text = f"🚨 *Grafana/InfluxDB 429 Hata Uyarısı (Son 24 Saat)*\n\n"
        alert_text += "\n\n----------------------------------------\n\n".join(flagged_endpoints)
        send_slack_message(alert_text)
    else:
        print(f"\n✅ [{PARTNER_CONTRACT_SLUG}] partnerinin çağırdığı hiçbir URI %{ERROR_429_THRESHOLD_PERCENT} 429 hata eşiğini aşmadı.")

if __name__ == "__main__":
    run_dynamic_endpoint_check()
