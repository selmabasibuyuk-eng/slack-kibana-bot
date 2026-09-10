from kibana_client import KibanaClient
from analyzer import TrafficAnalyzer

def main():
    client = KibanaClient()

    current_3d_data = client.fetch_traffic_data(time_from="now-3d", time_to="now")
    previous_3d_data = client.fetch_traffic_data(time_from="now-6d", time_to="now-3d")
    prebook_error_data = client.fetch_prebook_error_details(time_from="now-3d", time_to="now")

    analyzer = TrafficAnalyzer(current_3d_data, previous_3d_data, prebook_error_data)
    analyzer.analyze()

if __name__ == "__main__":
    main()
