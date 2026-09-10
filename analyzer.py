import requests
from config import SLACK_WEBHOOK_URL, THRESHOLDS

class TrafficAnalyzer:
    def __init__(self, current_data, previous_data, prebook_error_data):
        self.current_data = current_data
        self.previous_data = previous_data
        self.prebook_error_data = prebook_error_data

    def send_slack_alert(self, text):
        if SLACK_WEBHOOK_URL:
            requests.post(SLACK_WEBHOOK_URL, json={"text": text})
        else:
            print(f"[SLACK ALERT]\n{text}\n")

    def analyze(self):
        endpoints = self.current_data.get("aggregations", {}).get("by_endpoint", {}).get("buckets", [])
        
        for ep in endpoints:
            endpoint_name = ep["key"]
            for contract in ep.get("by_contract", {}).get("buckets", []):
                slug = contract["key"]
                total_requests = contract["doc_count"]
                if total_requests == 0:
                    continue

                status_counts = {str(b["key"]): b["doc_count"] for b in contract.get("by_status", {}).get("buckets", [])}
                
                count_400 = status_counts.get("400", 0)
                count_429 = status_counts.get("429", 0)
                pct_400 = (count_400 / total_requests) * 100
                pct_429 = (count_429 / total_requests) * 100

                if pct_400 > THRESHOLDS["HTTP_400_MAX_PERCENT"]:
                    self.send_slack_alert(f"⚠️ *High 400 Errors Detected*\n• *Partner:* `{slug}`\n• *Endpoint:* `{endpoint_name}`\n• *Ratio:* %{pct_400:.1f} ({count_400}/{total_requests})")

                if pct_429 > THRESHOLDS["HTTP_429_MAX_PERCENT"]:
                    self.send_slack_alert(f"⚠️ *High 429 Rate Limits Detected*\n• *Partner:* `{slug}`\n• *Endpoint:* `{endpoint_name}`\n• *Ratio:* %{pct_429:.1f} ({count_429}/{total_requests})")

                if endpoint_name == "prebook":
                    non_200_count = total_requests - status_counts.get("200", 0)
                    pct_error = (non_200_count / total_requests) * 100
                    
                    if pct_error > THRESHOLDS["PREBOOK_ERROR_MAX_PERCENT"]:
                        error_details = self._get_prebook_error_breakdown(slug)
                        self.send_slack_alert(
                            f"🚨 *Prebook Error Threshold Exceeded*\n"
                            f"• *Partner:* `{slug}`\n"
                            f"• *Total Error Ratio:* %{pct_error:.1f}\n"
                            f"• *Error Breakdown:*\n{error_details}"
                        )

        self._analyze_search_growth()

    def _get_prebook_error_breakdown(self, target_slug):
        contracts = self.prebook_error_data.get("aggregations", {}).get("by_contract", {}).get("buckets", [])
        for c in contracts:
            if c["key"] == target_slug:
                total = c["doc_count"]
                if total == 0:
                    return "No detail available."
                errors = c.get("by_error", {}).get("buckets", [])
                breakdown = []
                for err in errors:
                    pct = (err['doc_count'] / total) * 100
                    breakdown.append(f"  - `{err['key']}`: %{pct:.1f} ({err['doc_count']})")
                return "\n".join(breakdown)
        return "No error breakdown data."

    def _analyze_search_growth(self):
        curr_searches = self._extract_search_counts(self.current_data)
        prev_searches = self._extract_search_counts(self.previous_data)

        for slug, curr_count in curr_searches.items():
            prev_count = prev_searches.get(slug, 0)
            if prev_count > 0:
                growth = ((curr_count - prev_count) / prev_count) * 100
                if growth >= THRESHOLDS["SEARCH_GROWTH_PERCENT"]:
                    self.send_slack_alert(
                        f"📈 *Search Volume Increase Detected*\n"
                        f"• *Partner:* `{slug}`\n"
                        f"• *Previous 3 Days:* {prev_count}\n"
                        f"• *Current 3 Days:* {curr_count}\n"
                        f"• *Growth:* +%{growth:.1f}"
                    )
            elif curr_count > 100:
                self.send_slack_alert(
                    f"📈 *New Search Volume Detected*\n"
                    f"• *Partner:* `{slug}`\n"
                    f"• *Current 3 Days:* {curr_count}"
                )

    def _extract_search_counts(self, raw_data):
        counts = {}
        endpoints = raw_data.get("aggregations", {}).get("by_endpoint", {}).get("buckets", [])
        for ep in endpoints:
            if ep["key"] == "search":
                for contract in ep.get("by_contract", {}).get("buckets", []):
                    counts[contract["key"]] = contract["doc_count"]
        return counts
