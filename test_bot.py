import json
import os
import requests

# --- 1. AYARLAR ---
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"
GEMINI_API_KEY = "AQ.Ab8RN6Jy8v3wPDmPxO3OvVTbdR8I9NJ2USScHfGgnZBfyCyUnA"

# --- 2. SAHTE VERİ (Kibana Simülasyonu) ---
mock_data = {
    "partner_name": "Partner A",
    "metric": "GBB",
    "baseline_30d": 90,
    "avg_14d": 85,
    "current_val": 42,
    "drop_percentage": 50.5
}

# --- 3. GEMINI AI ÖZETİ ---
def generate_ai_summary(data):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"Aşağıdaki Kibana anomali verisini analiz et ve Slack bildirimi için Türkçe 2 kısa cümlelik profesyonel bir özet yaz:\n{json.dumps(data)}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    headers = {"Content-Type": "application/json"}
    try:
        res = requests.post(url, json=payload, headers=headers)
        res_json = res.json()
        return res_json['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Anomali tespiti yapıldı, detaylar Kibana panelinde."

# --- 4. SLACK BİLDİRİMİ GÖNDERME ---
ai_summary = generate_ai_summary(mock_data)

slack_payload = {
    "blocks": [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🚨 Kibana Anomali Alarmı",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Partner:* {mock_data['partner_name']}"},
                {"type": "mrkdwn", "text": f"*Metrik:* {mock_data['metric']}"},
                {"type": "mrkdwn", "text": f"*30 Günlük Baz:* {mock_data['baseline_30d']}"},
                {"type": "mrkdwn", "text": f"*Düşüş Oranı:* %{mock_data['drop_percentage']}"}
            ]
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🤖 AI Analizi:* {ai_summary}"
            }
        }
    ]
}

response = requests.post(SLACK_WEBHOOK_URL, json=slack_payload)
if response.status_code == 200:
    print("✅ Slack bildirimi başarıyla gönderildi!")
else:
    print(f"❌ Hata oluştu: {response.status_code} - {response.text}")
