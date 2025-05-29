"""
Test email search API
"""

import requests
import json

def test_email_search():
    """Test email search API"""
    base_url = "http://localhost:8003"
    
    print("🔍 이메일 검색 API 테스트")
    
    try:
        # Test email search
        search_data = {
            "query": "maritime safety",
            "top_k": 5
        }
        
        response = requests.post(f"{base_url}/emails/search", json=search_data)
        print(f"✅ 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 검색 결과:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ 오류 응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {e}")

if __name__ == "__main__":
    test_email_search()
