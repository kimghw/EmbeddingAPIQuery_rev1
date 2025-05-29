#!/usr/bin/env python3
"""
Debug email list API endpoint directly.
"""

import requests
import json

def debug_email_list():
    print("🔍 DEBUG EMAIL LIST API")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 1. Check health
    print("\n1. Health Check:")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 2. Get email stats
    print("\n2. Email Statistics:")
    try:
        response = requests.get(f"{base_url}/emails/stats")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # 3. List emails with debug info
    print("\n3. List Emails (with debug):")
    try:
        response = requests.get(f"{base_url}/emails/list")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Total emails: {data.get('total', 0)}")
            print(f"   Page: {data.get('page', 1)}")
            print(f"   Page size: {data.get('page_size', 10)}")
            print(f"   Number of emails returned: {len(data.get('emails', []))}")
            
            if data.get('emails'):
                print("\n   First email:")
                first_email = data['emails'][0]
                print(f"     ID: {first_email.get('id')}")
                print(f"     Subject: {first_email.get('subject')}")
                print(f"     Sender: {first_email.get('sender')}")
        else:
            print(f"   Error response: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. Check API logs
    print("\n4. Recent API logs:")
    try:
        with open('api_server.log', 'r') as f:
            lines = f.readlines()
            print("   Last 10 lines:")
            for line in lines[-10:]:
                print(f"   {line.strip()}")
    except Exception as e:
        print(f"   ❌ Could not read logs: {e}")

if __name__ == "__main__":
    debug_email_list()
