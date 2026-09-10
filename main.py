import sys
from kibana_client import KibanaClient
from analyzer import analyze_and_report

def main():
    try:
        client = KibanaClient()
        analyze_and_report(client)
    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
