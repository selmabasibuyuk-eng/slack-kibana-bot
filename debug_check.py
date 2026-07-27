import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

GRAFANA_URL = "https://grafana.srv.team"
GRAFANA_TOKEN = "glsa_MYk8JCUJ3PUWcAQpiBtKzQmy6FHy9V5X_b32c2833"
HEADERS = {"Authorization": f"Bearer {GRAFANA_TOKEN}"}

# 1. Datasource Listesini Al
ds_res = requests.get(f"{GRAFANA_URL}/api/datasources", headers=HEADERS, verify=False)
if ds_res.status_code == 200:
    influx_ds = [d for d in ds_res.json() if d.get('type') == 'influxdb']
    print("📌 Bulunan InfluxDB Kaynakları:")
    for ds in influx_ds:
        print(f"  • ID: {ds['id']} | UID: {ds.get('uid')} | Name: {ds['name']} | DB: {ds.get('database')}")
    
    # İlk bulduğu InfluxDB üzerinden test sorgusu yap
    if influx_ds:
        test_ds = influx_ds[0]
        ds_id = test_ds['id']
        print(f"\n🧪 [{test_ds['name']}] (ID: {ds_id}) Üzerinden Test Sorgusu Atılıyor...")
        
        q = 'SELECT "count", "contract_slug", "uri" FROM "partner.api.ext.prod.response.time" WHERE time > now() - 1h LIMIT 5'
        query_res = requests.get(
            f"{GRAFANA_URL}/api/datasources/proxy/{ds_id}/query",
            params={"q": q},
            headers=HEADERS,
            verify=False
        )
        print("📊 Yanıt:")
        print(query_res.text)
else:
    print(f"❌ Datasource listesi alınamadı ({ds_res.status_code}): {ds_res.text}")
