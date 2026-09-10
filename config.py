import os
from dotenv import load_dotenv

load_dotenv()

KIBANA_BASE_URL = os.getenv("KIBANA_BASE_URL", "https://kibana.srv.team")
KIBANA_API_KEY = os.getenv("KIBANA_API_KEY")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Ekibinizdeki herkes buraya kendi partner slug'ını ekleyebilir
CONTRACT_SLUGS = [
    "43605.b2b.5f2b",
    "43605.b2b.ad97",
    "43605.b2b.554f",
    "43605.b2b.a79e",
    "43605.b2b.3626"
]

THRESHOLDS = {
    "HTTP_400_MAX_PERCENT": 20.0,
    "HTTP_429_MAX_PERCENT": 15.0,
    "PREBOOK_ERROR_MAX_PERCENT": 20.0,
    "SEARCH_GROWTH_PERCENT": 10.0
}
