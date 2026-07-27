import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GRAFANA_URL = "https://grafana.srv.team"
GRAFANA_TOKEN = "glsa_MYk8JCUJ3PUWcAQpiBtKzQmy6FHy9V5X_b32c2833"
HEADERS = {"Authorization": f"Bearer {GRAFANA_TOKEN}"}

# Test Edilecek Potansiyel Datasource ID ve DB İsimleri
CANDIDATES = [
    {"id": "280", "name": "influx-hotcore-ovh", "db": "hotcore"},
    {"id": "17",  "name": "influx-ng-hotcore",  "db": "hotcore"},
    {"id": "297", "name": "influx-partner-ovh",  "db": "partner"},
    {"id": "299", "name": "influx-partner-ng-ovh", "db": "partner-ng"},
    {"id": "59",  "name": "partner",            "db": "partner-ng"}
]

SLUG_PATTERN = "19527"

print(f"🔍 [{SLUG_PATTERN}] için Datasource Taraması Başlatılıyor...\n")

for ds in CANDIDATES:
    ds_id = ds["id"]
    ds_name = ds["name"]
    db_name = ds["db"]
    
    # 1. Partner verisi sorgusu (Son 24 saat)
    q = f'SELECT count("count") FROM "partner.api.ext.prod.response.time" WHERE contract_slug =~ /{SLUG_PATTERN}/ AND time > now() - 24h'
    
    try:
        res = requests.get(
            f"{GRAFANA_URL}/api/datasources/proxy/{ds_id}/query",
            params={"q": q, "db": db_name},
            headers=HEADERS,
            verify=False,
            timeout=10
        )
        if res.status_code == 200:
            data = res.json()
            results = data.get("results", [])[0].get("series", [])
            if results and "values" in results[0]:
                cnt = results[0]["values"][0][1]
                print(f"✅ BULDUT! -> ID: {ds_id} | Name: {ds_name} | DB: {db_name}")
                print(f"   📊 Son 24 Saatlik Kayıt Sayısı: {int(cnt):,}\n")
            else:
                print(f"❌ ID: {ds_id} ({ds_name}) -> Bu kaynakta [{SLUG_PATTERN}] verisi bulunamadı.")
        else:
            print(f"⚠️ ID: {ds_id} ({ds_name}) -> Hata ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"❌ ID: {ds_id} ({ds_name}) -> Bağlantı hatası: {e}")

