#!/usr/bin/env python3
"""
이메일 데이터 갯수 검증 스크립트
"""

import asyncio
import json
from config.adapter_factory import get_vector_store
from adapters.email.json_email_loader import JsonEmailLoaderAdapter

async def verify_email_counts():
    print("🔍 이메일 데이터 갯수 검증 중...")
    print("=" * 50)
    
    # 1. 원본 JSON 파일 확인
    print("1️⃣ 원본 JSON 파일 확인...")
    try:
        with open('sample_emails.json', 'r', encoding='utf-8') as f:
            emails_data = json.load(f)
        
        # JSON 구조 확인
        if isinstance(emails_data, dict) and 'value' in emails_data:
            email_list = emails_data['value']
            print(f"   📁 JSON 파일의 이메일 수: {len(email_list)}")
            print(f"   📊 JSON 구조: Microsoft Graph API 형식")
            
            # 각 이메일 정보 출력
            for i, email in enumerate(email_list, 1):
                print(f"   📧 Email {i}:")
                print(f"      - ID: {email.get('id', 'N/A')}")
                sender_info = email.get('sender', {}).get('emailAddress', {})
                print(f"      - Sender: {sender_info.get('address', 'N/A')}")
                print(f"      - Subject: {email.get('subject', 'N/A')[:50]}...")
                print(f"      - Internet Message ID: {email.get('internetMessageId', 'N/A')}")
        else:
            print(f"   📁 JSON 파일의 이메일 수: {len(emails_data) if isinstance(emails_data, list) else 'Unknown'}")
            print(f"   ⚠️  예상과 다른 JSON 구조입니다.")
            
    except Exception as e:
        print(f"   ❌ JSON 파일 읽기 실패: {e}")
        return
    
    # 2. 로더로 처리된 이메일 확인
    print("\n2️⃣ 로더로 처리된 이메일 확인...")
    try:
        loader = JsonEmailLoaderAdapter()
        # Load JSON file first
        with open('sample_emails.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Convert to Graph API format if needed
        if isinstance(json_data, list):
            graph_format = {
                "@odata.context": "sample_data",
                "value": json_data
            }
        else:
            graph_format = json_data
        
        processed_emails = await loader.load_from_json(graph_format)
        
        print(f"   📧 처리된 이메일 수: {len(processed_emails)}")
        
        for i, email in enumerate(processed_emails, 1):
            print(f"   📧 Processed Email {i}:")
            print(f"      - ID: {email.id}")
            print(f"      - Sender: {email.sender}")
            print(f"      - Thread: {getattr(email, 'correspondence_thread', 'N/A')}")
            print(f"      - Subject: {email.subject[:50]}...")
            
    except Exception as e:
        print(f"   ❌ 이메일 로더 실패: {e}")
        return
    
    # 3. Qdrant에 저장된 임베딩 확인
    print("\n3️⃣ Qdrant 임베딩 확인...")
    try:
        vector_store = get_vector_store()
        
        # 컬렉션 존재 확인
        collections = await vector_store.list_collections()
        print(f"   📊 사용 가능한 컬렉션: {collections}")
        
        if 'emails' in collections:
            # 전체 임베딩 수 확인
            all_embeddings = await vector_store.get_all_embeddings('emails')
            print(f"   🔢 총 임베딩 수: {len(all_embeddings)}")
            
            # 임베딩 타입별 분석
            subject_count = 0
            body_count = 0
            unique_emails = set()
            unique_threads = set()
            unique_senders = set()
            
            for embedding in all_embeddings:
                metadata = embedding.get('payload', {})
                embedding_type = metadata.get('type', 'unknown')
                email_id = metadata.get('email_id', 'unknown')
                thread_id = metadata.get('thread_id', 'unknown')
                sender = metadata.get('sender', 'unknown')
                
                if embedding_type == 'subject':
                    subject_count += 1
                elif embedding_type == 'body':
                    body_count += 1
                
                # 고유 값들 수집
                if email_id != 'unknown':
                    unique_emails.add(email_id)
                if thread_id != 'unknown':
                    unique_threads.add(thread_id)
                if sender != 'unknown':
                    unique_senders.add(sender)
            
            print(f"   📝 Subject 임베딩: {subject_count}개")
            print(f"   📄 Body 임베딩: {body_count}개")
            print(f"   📧 고유 이메일 ID: {len(unique_emails)}개")
            print(f"   🧵 고유 Thread ID: {len(unique_threads)}개")
            print(f"   👤 고유 Sender: {len(unique_senders)}개")
            
            print(f"\n   📋 고유 Thread ID 목록: {list(unique_threads)}")
            print(f"   📋 고유 Sender 목록: {list(unique_senders)}")
            
            # 샘플 임베딩 상세 정보
            print(f"\n   🔍 첫 3개 임베딩 상세 정보:")
            for i, embedding in enumerate(all_embeddings[:3], 1):
                metadata = embedding.get('payload', {})
                print(f"      임베딩 {i}:")
                print(f"         - ID: {embedding.get('id', 'N/A')}")
                print(f"         - Type: {metadata.get('type', 'N/A')}")
                print(f"         - Email ID: {metadata.get('email_id', 'N/A')}")
                print(f"         - Thread ID: {metadata.get('thread_id', 'N/A')}")
                print(f"         - Sender: {metadata.get('sender', 'N/A')}")
                print(f"         - Content: {metadata.get('content', 'N/A')[:100]}...")
        else:
            print("   ❌ 'emails' 컬렉션이 존재하지 않습니다.")
            
    except Exception as e:
        print(f"   ❌ Qdrant 확인 실패: {e}")
    
    # 4. 갯수 일치 검증
    print("\n4️⃣ 갯수 일치 검증...")
    print("   📊 예상 갯수:")
    print(f"      - JSON 이메일: {len(emails_data)}개")
    print(f"      - 처리된 이메일: {len(processed_emails)}개")
    print(f"      - 예상 임베딩: {len(processed_emails) * 2}개 (subject + body)")
    
    if 'emails' in collections:
        print("   📊 실제 갯수:")
        print(f"      - 총 임베딩: {len(all_embeddings)}개")
        print(f"      - Subject 임베딩: {subject_count}개")
        print(f"      - Body 임베딩: {body_count}개")
        print(f"      - 고유 이메일: {len(unique_emails)}개")
        
        # 검증 결과
        expected_embeddings = len(processed_emails) * 2
        if len(all_embeddings) == expected_embeddings:
            print("   ✅ 임베딩 갯수 일치!")
        else:
            print(f"   ❌ 임베딩 갯수 불일치! 예상: {expected_embeddings}, 실제: {len(all_embeddings)}")
        
        if len(unique_emails) == len(processed_emails):
            print("   ✅ 고유 이메일 갯수 일치!")
        else:
            print(f"   ❌ 고유 이메일 갯수 불일치! 예상: {len(processed_emails)}, 실제: {len(unique_emails)}")

if __name__ == "__main__":
    asyncio.run(verify_email_counts())
