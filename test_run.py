from analyzer import TrafficAnalyzer

# 1. Kibana'dan Dönmüş Gibi Davranan Sahte Veri (Son 3 Gün)
mock_current_3d = {
    "aggregations": {
        "by_endpoint": {
            "buckets": [
                {
                    "key": "search",
                    "by_contract": {
                        "buckets": [
                            {"key": "43605.b2b.5f2b", "doc_count": 1500, "by_status": {"buckets": [{"key": 200, "doc_count": 1500}]}}
                        ]
                    }
                },
                {
                    "key": "prebook",
                    "by_contract": {
                        "buckets": [
                            {
                                "key": "43605.b2b.5f2b",
                                "doc_count": 1000,
                                "by_status": {
                                    "buckets": [
                                        {"key": 200, "doc_count": 700},
                                        {"key": 400, "doc_count": 250}, # %25 Error (>%20 Threshold)
                                        {"key": 429, "doc_count": 50}   # %5 Rate limit
                                    ]
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }
}

# 2. Sahte Veri (Önceki 3 Gün - Search Artışını Test Etmek İçin)
mock_previous_3d = {
    "aggregations": {
        "by_endpoint": {
            "buckets": [
                {
                    "key": "search",
                    "by_contract": {
                        "buckets": [
                            {"key": "43605.b2b.5f2b", "doc_count": 1000} # 1000'den 1500'e çıktı (%50 Artış > %10 Threshold)
                        ]
                    }
                }
            ]
        }
    }
}

# 3. Sahte Prebook Hata Detay Verisi
mock_prebook_errors = {
    "aggregations": {
        "by_contract": {
            "buckets": [
                {
                    "key": "43605.b2b.5f2b",
                    "doc_count": 300,
                    "by_error": {
                        "buckets": [
                            {"key": "rate_not_found", "doc_count": 200}, # %66.7
                            {"key": "no_available_rate", "doc_count": 100} # %33.3
                        ]
                    }
                }
            ]
        }
    }
}

print("=== MOCK TEST BAŞLATILIYOR ===\n")
analyzer = TrafficAnalyzer(mock_current_3d, mock_previous_3d, mock_prebook_errors)
analyzer.analyze()
print("\n=== TEST TAMAMLANDI ===")
