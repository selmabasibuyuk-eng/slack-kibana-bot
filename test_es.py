import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ----------------------------------------------------
# 📌 KONFİGÜRASYON VE PARTNER TANIMLARI
# ----------------------------------------------------
ES_URL = "https://kibana.srv.team/internal/search/opensearch"
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

# 🏢 Partnerler ve Kontrat ID'leri
PARTNERS = {
    "Partner 1": ["19527.b2b.89cb", "19527.b2b.a0ae"],
    "Partner 2": ["19527.b2b.29f1"],
    "Partner 3": ["19527.b2b.2290"],
    # İhtiyacınıza göre diğer partnerleri ekleyebilirsiniz.
}

headers = {
    'accept': '*/*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'content-type': 'application/json',
    'origin': 'https://kibana.srv.team',
    'osd-version': '3.3.0',
    'osd-xsrf': 'osd-fetch',
    'referer': 'https://kibana.srv.team/app/visualize',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
    'Cookie': 'uid=CkkBIGpPWS9nu1203r4kAg==; security_authentication_oidc1=Fe26.2**eb3b9163beb870fc2256ec948b94f9a641d295431ff821502bb76e9890ff5d50*SGQrVZvqFdLbaC3-R5Bwvg*6YTR21lTpqk8K1MTzoN_S-XPnSkFsO3I1PM7FEQR2zZDjfqKkg17fX8cu-V__QTBwOIuKTtwpxbN6mBNl_khuU-XTuylalICwJXiWQFGTv8iZUp5YsGKjGJ5RUYUgE_SvQ1t4oxKPB4O-eHcqClb6ipQWYnW0k9shhLjmvWEJR3rGbHj3RfPPTUpo0RTSP4RU5DybxivTIhPLTwaXI4XM9NDVgHy4vAny6CR_OlMfgbKScVumGcdFKBZzunIIJqJdlXanWssl5QqnmfHGCAmc3CwbOquVyLszVjcNbP4X4_3CzaIFPjkg4BkRpzi7cYZIwWtxmiCM5b6x6JvidQnnsZK4Nm-5kHxaYLVvhE8St7OfI0-q87l0I8F59Oo9DyPOc5FY4WI5KAIgWTnSFWxuF504h8tnzKzKulEIrYSkFspk_u8Nk5tdugl7SLg01TFwV88i8HqoK05Sy1F07SMV1VmgOEhJYjlGfNdwcStPLArs10KDG2sKyfZnQJ2fMIx7efLy5iU4JwOHPhRrP1PnGQq_14I-du1fgrpR_VxAVsWKW2UzGxHe-ON_oWzUywCYHAgnCRkzcfQQcp5rvQ-ZF5j3XrNofjlt7LjOMawN2lau2geiWx4DNfeMY1BVn8__bJzFUTewKIMWzgXszx_v2mpBTUAUAgVxZQkq69Ia-gpeu8pfytrmF978pzrsuwY15sl-B2GMhiY9ozC7ClAoWMQGbvi1r_1Cw1cE7Ezix6gS72I3iHQ9mSbNTq6AQppldExKa646BKKSh13vzalrUKUJrJAn2qjmWGy65zqlYJMRaIIvby5Ab-IRWqntazMn5YuW6_dLkQe1kHNBMaNkzStcRAZkttcjuKIwClEWBI6SF6rKnEPSbKomFGWepNMGB6vxqIfYhqW962mh9_pf4a7hu-85hTy1g1X6wka5vcJ0sFQFY_NvqoCvp1K540MdlQ6cm6WCPrQRT9moyD3p9A5BgrUirp4lck-neK0L3hQ-CBC4T-42FiXN8k4fw-DtkMpPhA5Z3DarkwKCjdopJ3OZPCBt8H9iD2aDJUbzRvDQBFPIqFeNwuSNvSW6tGbxrmYC7Lrn-qrZNQyx1UWOhi0waIqZAXSVA5gdovbR4Dcij5i84nTxaqSzr1TcCkxBC7QsLfUuYiiPs2Ihy3Pdfw-5y6oapVBIJ7O5kgXXEfHXeCSRyn7Ar1qBRMhTCZRT07Ov3JNHKjispLfav86MFFv5keYU-ty35UNOd90R_QooA8t9qyP24_Xh8lhzpalIN0Al4mR1Y0szBGiCDOH_FTtDIigSEwttFeKbq1CMJ6m3y6GBmcZ8lY65ghvfkmbfewPtQDynbLeWyUOEahijVaf_8s7pIrMB-3-dVwXnVs2jzcRp6ReNs7awL726IRqI9V5ZCEsdmu5kayQhzWVOy7F1COXQr2dOZhQbkFZ3ziZhGn_49etmSx_-nO61gYLMY4oE0EslyDe5Di2htI0-YdBCNydqUluOMQWFPLznBwL5oOqZLc-mgkH6WSHee2PsMcVFu7S3-zcuUX-4ejedfphlcTlxiGR3XMbAW1a78zO42dg8ulyvgYTzEBUGK8nasJg16H0Uidzlw2PWxqAYTwcieW8x1B8Dk2CHB_IzVa7mbN5202XblnregR4mgKayhTKg6eHE0c4Q6538kog8NZi5yQNLMS-DeiP6sn13mZ3PK9CvullO0PBXvZAUHKRq7jyTpW3vLtfZkGqy1C44zALOzfEOGQND9exwIsNG70cpcuhitVYLCF9dT8xVHK6BLN-vT1sTI_f_oXnm8s3nA7PNhaWnphXnpTJ4s2BfGHjVxlLNdFTqGklC2l783Iv**63bf8415e1f11c0242d4b87a51b60fee7ab5fcddad0d5676fa141ae8771b8e9f*C9kTR9XF1w98mJPQwCQB5uaio_q2v9rosZAn4M9lHao; security_authentication=Fe26.2**c3d4fc431bded840ed1f998fdfaa12c51a2639359baafd3617d5ff1facd33b69*g8umX3Z2eCHdPup92KZg-A*visdrqZ4oyhFRvxx5SfzpaJV1p26_M9jK0LOFeDt8PZaiNNOJQkD7UsaYmsqOBL6Z63y5AERDb-YkUQ_bXmTk89-cSZnftgMSOkqg_yl5cE2F9fqXMSp4SC_jZOzeHjDa1R-CplfkPnd8ywrqLzQ7kJ-ekVldlw2bXYZM0pnUuaeyAnLoYWVB39_wEjyJUn0aaoN5J3UB-s1iN_aP0QxoTqSlYNAKKaCChvjJo8y3nRAsEqMENHDjsNYu4f3q9p-YIVb3lekT7OBn2JX98nW_A2r3Rc0cjKqboL1VIepHQx4kOOCSk1L2yIAxsONS9a2B0QhRUU_h1OmLS3zSl8YOKad3mFsMX7BqbQRoi1YlJ9zwwZ-7hS0rwtR5_QhtPJz6jY8a6edEbz-JHvUH09RulZTZRIjC7XF2sdX-9h9mKxHsA3YvFPOe8YTHi84TMr63qN1dMmSlvIMhuUT9JjWearINo6NxRJPFoiNchFxrNQ5Q1U1P83GXzW-7HlccoBa9_xFcI3NV9h-R2q2IfWAdB8Y_48TL8IBXqC-34nKxT9bc7tJyaPVdcrUGfPhbnFVOVh9oujXf7f38HpZgbbf4sBLfaUWuA-U1OeyPy-CDnpIqzg00yYfQFngv2nh6ewsb6bJyhF19NTrNZUyha1qCHGZbc5SCooQuR33uI4pm3dCVfEblNylyLwK6wLofFpsMtPBxJDzip-_l808wKlo1n7BBeX8xds3SDDKmyHeAgCMudMWHug2I0Tc7qIc95ncvjdEOu7s9bROMOhxuT974GU3e_easen3--h_3sAa0mV3NTlZlr_NG3YlM3MQIfrNLXg6AImusZFtVbLmTuUg1HCUQbYZ0M4290YZFWLSeqwCKpdxEkz3ko9cbJRlqdmdLYPWGiK-TgyRzaPZQirVCAiFv0ayZ3LAYYZVQnojTCwRmn_CKvnfC7ODgX7hhJTGB0Ax8uj3cXZJ_RkAQln8Mx0N7a7AAZ-eqdXVFAKYrvzmYttGgtUxTKYkfDcNYLwSxqDK1cu_htm9fbXBasnZSP9c2aq0N0UqDmlwTMIeQjcUGNnnTIv4IyHnS9y8itTkwD-87kQ8GzRWAOFESn4bK9uddFb6_GPRW1crYqmCRWYMbI1X-ilk-8lzGySvvAurLOqkTqZLdQqq63Lk7pvlHvvw9s5cFLE35TkgHhmauyJoIo8eoiGftsWyxvQ4Xdkt**dad56484084493c1bd46deb1b93ca9b59a459c852290ef7b0bced88302b6e50b*y1BnTa_mbFqOrt9Y5wbuuEONMERtO9rdOY17Ajl7hws'
}

def send_slack_message(text):
    if not SLACK_WEBHOOK_URL:
        print("⚠️ Slack Webhook URL tanımlanmamış.")
        return
    payload = {"text": text}
    try:
        res = requests.post(SLACK_WEBHOOK_URL, json=payload, headers={'Content-Type': 'application/json'})
        if res.status_code == 200:
            print("💬 Slack bildirimi başarıyla gönderildi.")
        else:
            print(f"❌ Slack bildirimi başarısız ({res.status_code}): {res.text}")
    except Exception as e:
        print(f"❌ Slack bağlantı hatası: {e}")

def check_partner(partner_name, contracts):
    contract_filters = [{"match_phrase": {"fields.contract": c}} for c in contracts]
    
    # 🎯 `fields.error` alanına göre gruplama yapıyoruz
    query = {
      "params": {
        "index": "container-dante-dante-main-*",
        "body": {
          "aggs": {
            "error_breakdown": {
              "terms": {"field": "fields.error", "order": {"_count": "desc"}, "size": 10}
            }
          },
          "size": 0,
          "query": {
            "bool": {
              "filter": [
                {"match_all": {}},
                {
                  "bool": {
                    "minimum_should_match": 1,
                    "should": [
                      {"match_phrase": {"fields.endpoint": "prebook_from_serp"}},
                      {"match_phrase": {"fields.endpoint": "prebook"}}
                    ]
                  }
                },
                {
                  "bool": {
                    "minimum_should_match": 1,
                    "should": contract_filters
                  }
                },
                {
                  "range": {
                    "@timestamp": {
                      "gte": "now-7d",
                      "lte": "now"
                    }
                  }
                }
              ]
            }
          }
        }
      }
    }
    
    try:
        response = requests.post(ES_URL, json=query, headers=headers, verify=False)
        if response.status_code == 200:
            res_json = response.json()
            raw = res_json.get("rawResponse", res_json)
            buckets = raw.get("aggregations", {}).get("error_breakdown", {}).get("buckets", [])
            
            counts = {}
            total_errors = 0
            for bucket in buckets:
                key = str(bucket.get("key")).lower()
                count = bucket.get("doc_count", 0)
                counts[key] = count
                total_errors += count
                
            if total_errors == 0:
                return None  # Hiç hata yoksa pas geç
                
            rates = {key: (count / total_errors) * 100 for key, count in counts.items()}
            
            # En çok görülen hata türü
            highest_error_type = max(rates, key=rates.get)
            highest_rate = rates[highest_error_type]
            
            # no_avail ile ilgili hata anahtarı
            no_avail_key = next((k for k in rates if "no_avail" in k), None)
            no_avail_rate = rates[no_avail_key] if no_avail_key else 0.0
            no_avail_count = counts[no_avail_key] if no_avail_key else 0
            
            # 🚨 UYARI ŞARITI:
            # no_avail hatası varsa VE diğer tüm hata türlerinden daha yüksekse
            is_problem = (no_avail_key is not None) and (highest_error_type == no_avail_key)
            
            if is_problem:
                details = [f"⚠️ *Partner:* `{partner_name}` (Toplam Hata: `{total_errors}` ad.)"]
                details.append(f"  • 🔴 *Baskın Hata (`{no_avail_key}`):* %{no_avail_rate:.2f} (`{no_avail_count}` adet)")
                
                # Diğer alt hata türlerini ekle
                details.append("  • *Diğer Hatalar:*")
                for err_key, rate in rates.items():
                    if err_key != no_avail_key:
                        details.append(f"    - `{err_key}`: %{rate:.2f} ({counts[err_key]} adet)")
                        
                return "\n".join(details)
                
    except Exception as e:
        print(f"❌ {partner_name} sorgulanırken hata oluştu: {e}")
        
    return None

def main():
    print("🔍 Partner hata analizleri başlatılıyor...")
    flagged_issues = []
    
    for partner_name, contracts in PARTNERS.items():
        issue_msg = check_partner(partner_name, contracts)
        if issue_msg:
            flagged_issues.append(issue_msg)
            
    if flagged_issues:
        print(f"⚠️ {len(flagged_issues)} partnerde 'no_available_rates' en yüksek hata olarak tespit edildi! Slack gönderiliyor...")
        alert_text = "🚨 *Haftalık OpenSearch Hata Analiz Uyarısı (Son 7 Gün)*\n"
        alert_text += "Aşağıdaki partnerlerde `no_available_rates` diğer tüm hata türlerinden baskın çıktı:\n\n"
        alert_text += "\n\n----------------------------------------\n\n".join(flagged_issues)
        
        send_slack_message(alert_text)
    else:
        print("✅ Tüm partnerlerin durumu normal (`no_available_rates` baskın hata değil). Slack bildirimi atılmadı.")

if __name__ == "__main__":
    main()
