import os
from dotenv import load_dotenv

load_dotenv()

KIBANA_BASE_URL = os.getenv("KIBANA_BASE_URL", "https://kibana.srv.team")
KIBANA_API_KEY = os.getenv("KIBANA_API_KEY")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
ERROR_THRESHOLD = float(os.getenv("ERROR_THRESHOLD_PERCENT", "20.0"))

# Virgülle ayrılmış contract slug listesini ayrıştırır
CONTRACT_SLUGS = [
    s.strip() for s in os.getenv("CONTRACT_SLUGS", "").split(",") if s.strip()
]
