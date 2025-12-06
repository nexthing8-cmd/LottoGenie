from fastapi.testclient import TestClient
from src.web_app import app
import os

# Mock DB env if needed, but it should connect to real DB based on .env
# We are testing read-only routes mostly.

client = TestClient(app)

def test_routes():
    print("Testing / ...")
    resp = client.get("/")
    assert resp.status_code == 200
    
    print("Testing /history ...")
    resp = client.get("/history")
    assert resp.status_code == 200
    if "당첨정보" not in resp.text:
        print("FAILED: Title '당첨정보' not found in /history")
    else:
        print("PASSED: Title found")
        
    print("Testing /history/1160 ...")
    resp = client.get("/history/1160")
    if resp.status_code != 200:
        print(f"FAILED: Status code {resp.status_code}")
        print(resp.text)
    else:
        if "1160회 당첨 상세정보" in resp.text:
            print("PASSED: Detail title found")
        else:
            print("FAILED: Detail title not found")
            
        if "등위별 당첨금 정보" in resp.text:
            print("PASSED: Prize table found")
        else:
            print("FAILED: Prize table not found")

        if "1등 배출점" in resp.text:
            print("PASSED: Stores table found")
        else:
            print("FAILED: Stores table not found")

if __name__ == "__main__":
    test_routes()

