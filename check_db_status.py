#!/usr/bin/env python3
"""
데이터베이스 상태 확인 스크립트
"""
import asyncio
import sys
import os

# 프로젝트 루트를 Python path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.adapter_factory import AdapterFactory

async def check_database_status():
    """데이터베이스 상태 확인"""
    print("🔍 데이터베이스 상태 확인 중...")
    
    try:
        # AdapterFactory 생성
        factory = AdapterFactory()
        vector_store = factory.create_vector_store_adapter()
        
        print(f"✅ 벡터 스토어 연결 성공: {type(vector_store).__name__}")
        
        # 컬렉션 목록 확인
        collections = await vector_store.list_collections()
        print(f"📊 총 컬렉션 수: {len(collections)}")
        
        if collections:
            print("📋 컬렉션 목록:")
            for collection in collections:
                print(f"  - {collection}")
                
                # 각 컬렉션의 임베딩 수 확인
                try:
                    count = await vector_store.count_embeddings(collection)
                    print(f"    임베딩 수: {count}")
                except Exception as e:
                    print(f"    임베딩 수 확인 실패: {e}")
        else:
            print("❌ 컬렉션이 없습니다.")
        
        # 이메일 컬렉션 특별 확인
        email_collection = "emails"
        print(f"\n🔍 '{email_collection}' 컬렉션 상세 확인:")
        
        if await vector_store.collection_exists(email_collection):
            print(f"✅ '{email_collection}' 컬렉션 존재")
            
            # 임베딩 수 확인
            count = await vector_store.count_embeddings(email_collection)
            print(f"📊 임베딩 수: {count}")
            
            # 컬렉션 정보 확인
            try:
                info = await vector_store.get_collection_info(email_collection)
                print(f"📋 컬렉션 정보: {info}")
            except Exception as e:
                print(f"⚠️ 컬렉션 정보 확인 실패: {e}")
                
        else:
            print(f"❌ '{email_collection}' 컬렉션이 존재하지 않습니다.")
        
        print("\n" + "="*50)
        print("🎯 결론:")
        if not collections:
            print("❌ 데이터베이스가 완전히 비어있습니다.")
            print("💡 이메일 데이터를 처리해야 합니다.")
        elif email_collection not in collections:
            print("❌ 이메일 컬렉션이 없습니다.")
            print("💡 이메일 처리 API를 사용해서 데이터를 추가해야 합니다.")
        else:
            email_count = await vector_store.count_embeddings(email_collection)
            if email_count == 0:
                print("❌ 이메일 컬렉션은 있지만 데이터가 없습니다.")
                print("💡 이메일 처리가 실패했을 수 있습니다.")
            else:
                print(f"✅ 이메일 데이터가 {email_count}개 있습니다.")
        
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        print("💡 Qdrant 서버가 실행 중인지 확인하세요.")

if __name__ == "__main__":
    asyncio.run(check_database_status())
