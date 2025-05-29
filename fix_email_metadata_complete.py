#!/usr/bin/env python3
"""
이메일 메타데이터 완전 수정 스크립트
- 기존 emails 컬렉션 삭제
- 수정된 어댑터로 이메일 데이터 재처리
- 메타데이터 저장 확인
"""

import asyncio
import json
from config.adapter_factory import get_vector_store, get_embedding_model
from adapters.email.json_email_loader import JsonEmailLoaderAdapter
from core.usecases.email_processing import EmailProcessingUseCase
from config.settings import create_config

async def fix_email_metadata_complete():
    print("🔧 이메일 메타데이터 완전 수정 시작...")
    print("=" * 80)
    
    try:
        # 1. 어댑터 및 유즈케이스 초기화
        print("1️⃣ 어댑터 및 유즈케이스 초기화...")
        vector_store = get_vector_store()
        embedding_model = get_embedding_model()
        email_loader = JsonEmailLoaderAdapter()
        config = create_config()
        
        email_processing = EmailProcessingUseCase(
            email_loader=email_loader,
            embedding_model=embedding_model,
            vector_store=vector_store,
            config=config
        )
        
        # 2. 기존 emails 컬렉션 삭제
        print("\n2️⃣ 기존 emails 컬렉션 삭제...")
        try:
            await vector_store.delete_collection('emails')
            print("   ✅ emails 컬렉션 삭제 완료")
        except Exception as e:
            print(f"   ⚠️  컬렉션 삭제 실패 (존재하지 않을 수 있음): {e}")
        
        # 3. JSON 데이터 로드
        print("\n3️⃣ JSON 데이터 로드...")
        with open('sample_emails.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        print(f"   📧 JSON 파일에서 {len(json_data.get('value', []))} 개 이메일 발견")
        
        # 4. 수정된 어댑터로 이메일 처리
        print("\n4️⃣ 수정된 어댑터로 이메일 처리 중...")
        result = await email_processing.process_emails_from_json(json_data)
        
        if result["success"]:
            print(f"   ✅ 이메일 처리 성공!")
            print(f"   📊 처리된 이메일: {result['processed_count']}")
            print(f"   🔢 생성된 임베딩: {result['embedded_count']}")
            print(f"   📁 컬렉션: {result['collection_name']}")
        else:
            print(f"   ❌ 이메일 처리 실패: {result.get('error', 'Unknown error')}")
            return
        
        # 5. 메타데이터 저장 확인
        print("\n5️⃣ 메타데이터 저장 확인...")
        
        # 첫 번째 이메일의 임베딩 확인
        if result["emails"]:
            first_email = result["emails"][0]
            email_id = first_email["id"]
            
            print(f"   🔍 첫 번째 이메일 확인: {email_id}")
            print(f"   📧 제목: {first_email['subject']}")
            print(f"   👤 발신자: {first_email['sender']}")
            print(f"   🧵 스레드: {first_email['correspondence_thread']}")
            
            # 벡터 스토어에서 직접 확인
            embeddings = await vector_store.get_embeddings_by_document(email_id, 'emails')
            
            if embeddings:
                print(f"   ✅ 벡터 스토어에서 {len(embeddings)} 개 임베딩 발견")
                
                for emb in embeddings:
                    print(f"\n   📋 임베딩 ID: {emb.id}")
                    print(f"      - 타입: {emb.metadata.get('embedding_type', 'unknown')}")
                    print(f"      - 스레드: {emb.metadata.get('correspondence_thread', 'N/A')}")
                    print(f"      - 발신자: {emb.metadata.get('sender_address', 'N/A')}")
                    print(f"      - 제목: {emb.metadata.get('subject', 'N/A')[:50]}...")
                    print(f"      - 내용 길이: {len(emb.metadata.get('content', ''))}")
                    
                    # 메타데이터 필드 확인
                    metadata_fields = [
                        'email_id', 'embedding_type', 'correspondence_thread',
                        'sender_address', 'subject', 'created_time', 'has_attachments'
                    ]
                    
                    missing_fields = [field for field in metadata_fields if field not in emb.metadata]
                    if missing_fields:
                        print(f"      ⚠️  누락된 메타데이터: {missing_fields}")
                    else:
                        print(f"      ✅ 모든 메타데이터 필드 존재")
            else:
                print(f"   ❌ 벡터 스토어에서 임베딩을 찾을 수 없음")
        
        # 6. 전체 통계 확인
        print("\n6️⃣ 전체 통계 확인...")
        total_count = await vector_store.count_embeddings('emails')
        print(f"   📊 전체 임베딩 수: {total_count}")
        
        # 7. 검색 테스트
        print("\n7️⃣ 메타데이터 검색 테스트...")
        
        # 간단한 벡터 검색으로 메타데이터 확인
        all_embeddings = await vector_store.get_all_embeddings('emails', limit=5)
        
        if all_embeddings:
            print(f"   ✅ {len(all_embeddings)} 개 임베딩 샘플 확인:")
            
            for i, emb in enumerate(all_embeddings, 1):
                print(f"\n   📧 임베딩 {i}:")
                print(f"      - ID: {emb.id}")
                print(f"      - 타입: {emb.metadata.get('embedding_type', 'N/A')}")
                print(f"      - 스레드: {emb.metadata.get('correspondence_thread', 'N/A')}")
                print(f"      - 발신자: {emb.metadata.get('sender_address', 'N/A')}")
                
                # 중요한 메타데이터 필드들이 최상위에 있는지 확인
                top_level_fields = ['email_id', 'embedding_type', 'correspondence_thread', 'sender_address']
                for field in top_level_fields:
                    if field in emb.metadata:
                        print(f"      ✅ {field}: {emb.metadata[field]}")
                    else:
                        print(f"      ❌ {field}: 누락")
        else:
            print("   ❌ 임베딩을 가져올 수 없음")
        
        print("\n" + "=" * 80)
        print("🎉 메타데이터 수정 완료!")
        print("✅ 이제 Thread/Sender 검색이 정상 작동해야 합니다.")
        
    except Exception as e:
        print(f"\n❌ 메타데이터 수정 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_email_metadata_complete())
