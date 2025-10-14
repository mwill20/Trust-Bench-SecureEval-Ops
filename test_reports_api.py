"""Test script for Reports API endpoints"""
import requests
import json

API_BASE = "http://127.0.0.1:8000"

def test_reports_list():
    """Test GET /api/reports/list"""
    print("=" * 60)
    print("Testing GET /api/reports/list")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE}/api/reports/list")
        print(f"Status Code: {response.status_code}")
        
        if response.ok:
            data = response.json()
            print(f"✅ Success!")
            print(f"Number of reports: {len(data.get('reports', []))}")
            print("\nReports:")
            for report in data.get('reports', []):
                print(f"  - {report['id']}: {report['verdict']} ({report['repository']})")
                print(f"    Pillars: {report.get('pillars', {})}")
                print(f"    Has HTML: {report.get('hasHtmlReport', False)}")
            return data.get('reports', [])
        else:
            print(f"❌ Failed: {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_report_view(report_id):
    """Test GET /api/reports/view/{report_id}"""
    print("\n" + "=" * 60)
    print(f"Testing GET /api/reports/view/{report_id}")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_BASE}/api/reports/view/{report_id}")
        print(f"Status Code: {response.status_code}")
        
        if response.ok:
            data = response.json()
            print(f"✅ Success!")
            print(f"Metadata: {data.get('metadata', {})}")
            html = data.get('html', '')
            print(f"HTML Length: {len(html)} characters")
            print(f"HTML Preview (first 200 chars): {html[:200]}")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    # Test reports list
    reports = test_reports_list()
    
    # Test report viewer for first report with HTML
    if reports:
        for report in reports:
            if report.get('hasHtmlReport'):
                test_report_view(report['id'])
                break
        else:
            print("\n⚠️  No reports with HTML found to test viewer")
    else:
        print("\n⚠️  No reports found")
