import requests
from config import KIBANA_BASE_URL, KIBANA_API_KEY, CONTRACT_SLUGS

class KibanaClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"ApiKey {KIBANA_API_KEY}",
            "Content-Type": "application/json",
            "kbn-xsrf": "true"
        }
        self.endpoint = f"{KIBANA_BASE_URL}/api/console/proxy?path=container-dante-dante-main/_search"

    def fetch_traffic_data(self, time_from="now-3d", time_to="now"):
        payload = {
            "size": 0,
            "query": {
                "bool": {
                    "filter": [
                        {"range": {"@timestamp": {"gte": time_from, "lte": time_to}}},
                        {"terms": {"fields.contract.keyword": CONTRACT_SLUGS}}
                    ]
                }
            },
            "aggs": {
                "by_endpoint": {
                    "terms": {"field": "fields.endpoint.keyword", "size": 20},
                    "aggs": {
                        "by_contract": {
                            "terms": {"field": "fields.contract.keyword", "size": 50},
                            "aggs": {
                                "by_status": {
                                    "terms": {"field": "fields.http_status", "size": 100}
                                }
                            }
                        }
                    }
                }
            }
        }
        res = requests.post(self.endpoint, headers=self.headers, json=payload, timeout=60)
        res.raise_for_status()
        return res.json()

    def fetch_prebook_error_details(self, time_from="now-3d", time_to="now"):
        payload = {
            "size": 0,
            "query": {
                "bool": {
                    "filter": [
                        {"range": {"@timestamp": {"gte": time_from, "lte": time_to}}},
                        {"terms": {"fields.contract.keyword": CONTRACT_SLUGS}},
                        {"term": {"fields.endpoint.keyword": "prebook"}}
                    ]
                }
            },
            "aggs": {
                "by_contract": {
                    "terms": {"field": "fields.contract.keyword", "size": 50},
                    "aggs": {
                        "by_error": {
                            "terms": {"field": "fields.error.keyword", "size": 20}
                        }
                    }
                }
            }
        }
        res = requests.post(self.endpoint, headers=self.headers, json=payload, timeout=60)
        res.raise_for_status()
        return res.json()
