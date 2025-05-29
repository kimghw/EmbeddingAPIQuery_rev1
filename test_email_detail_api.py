"""
Test email detail API
"""

import requests
import json

def test_email_detail():
    """Test email detail API"""
    base_url = "http://localhost:8002"
    email_id = "bb9a9349-fb23-4810-b04a-35b61d795d8a"
    
    print(f"🔍 이메일 상세 API 테스트: {email_id}")
    
    try:
        # Test email detail
        response = requests.get(f"{base_url}/emails/detail/{email_id}")
        print(f"✅ 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 응답 데이터:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ 오류 응답: {response.text}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {e}")

if __name__ == "__main__":
    test_email_detail()
