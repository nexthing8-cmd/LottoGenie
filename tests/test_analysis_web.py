from fastapi.testclient import TestClient
from src.web_app import app
import json

client = TestClient(app)

def test_analysis_page():
    print("Testing /analysis ...")
    resp = client.get("/analysis")
    assert resp.status_code == 200
    
    # Check for scripts
    if "chartjs-plugin-zoom" in resp.text:
        print("PASSED: Zoom plugin script found")
    else:
        print("FAILED: Zoom plugin script not found")
        
    # Check for new canvas
    if 'id="pieChart"' in resp.text:
        print("PASSED: Pie chart canvas found")
    else:
        print("FAILED: Pie chart canvas not found")
        
    # Check for data injection
    # We look for: data-recent='{...}'
    # It might be HTML escaped, but let's check basic presence
    if 'data-recent=' in resp.text:
        print("PASSED: Recent data injected")
    else:
        print("FAILED: Recent data not found")

if __name__ == "__main__":
    test_analysis_page()

