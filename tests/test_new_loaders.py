"""
새로운 문서 로더들 테스트
"""

import asyncio
import json
from pathlib import Path
from config.adapter_factory import AdapterFactory


async def test_json_loader():
    """JSON 로더 테스트"""
    print("=== JSON 로더 테스트 ===")
    
    # 테스트용 JSON 파일 생성
    test_json_data = {
        "title": "테스트 문서",
        "content": "이것은 JSON 로더 테스트용 문서입니다.",
        "metadata": {
            "author": "테스트 작성자",
            "created_date": "2024-01-01",
            "tags": ["test", "json", "document"]
        },
        "sections": [
            {
                "heading": "섹션 1",
                "text": "첫 번째 섹션의 내용입니다."
            },
            {
                "heading": "섹션 2", 
                "text": "두 번째 섹션의 내용입니다."
            }
        ]
    }
    
    # 테스트 파일 생성
    test_file = Path("testdata/test_document.json")
    test_file.parent.mkdir(exist_ok=True)
    
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_json_data, f, ensure_ascii=False, indent=2)
    
    try:
        # JSON 로더 생성 및 테스트
        loader = AdapterFactory.create_document_loader_adapter("json")
        
        # 로더 정보 출력
        print(f"로더 타입: {loader.get_loader_type()}")
        print(f"지원 확장자: {loader.get_supported_extensions()}")
        
        # 파일 유효성 검사
        is_valid = await loader.validate_file(str(test_file))
        print(f"파일 유효성: {is_valid}")
        
        # 문서 로드
        document = await loader.load_document(str(test_file))
        
        print(f"문서 ID: {document.id}")
        print(f"문서 제목: {document.title}")
        print(f"문서 내용 길이: {len(document.content)} 문자")
        print(f"메타데이터 키: {list(document.metadata.keys())}")
        print(f"문서 내용 미리보기:\n{document.content[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"JSON 로더 테스트 실패: {e}")
        return False
    
    finally:
        # 테스트 파일 정리
        if test_file.exists():
            test_file.unlink()


async def test_web_scraper_loader():
    """웹 스크래퍼 로더 테스트"""
    print("\n=== 웹 스크래퍼 로더 테스트 ===")
    
    try:
        # 웹 스크래퍼 로더 생성
        loader = AdapterFactory.create_document_loader_adapter(
            "web_scraper",
            timeout=10,
            max_retries=2
        )
        
        # 로더 정보 출력
        print(f"로더 타입: {loader.get_loader_type()}")
        loader_info = loader.get_loader_info()
        print(f"지원 기능: {loader_info['features']}")
        
        # 테스트 URL (간단한 예제 사이트)
        test_url = "https://httpbin.org/html"
        
        # URL 유효성 검사
        is_valid = await loader.validate_file(test_url)
        print(f"URL 유효성: {is_valid}")
        
        if is_valid:
            # 웹 페이지 로드
            document = await loader.load_document(test_url)
            
            print(f"문서 ID: {document.id}")
            print(f"문서 제목: {document.title}")
            print(f"문서 내용 길이: {len(document.content)} 문자")
            print(f"메타데이터 키: {list(document.metadata.keys())}")
            print(f"도메인: {document.metadata.get('domain', 'N/A')}")
            print(f"상태 코드: {document.metadata.get('status_code', 'N/A')}")
            print(f"문서 내용 미리보기:\n{document.content[:200]}...")
        else:
            print("URL에 접근할 수 없어 테스트를 건너뜁니다.")
        
        return True
        
    except Exception as e:
        print(f"웹 스크래퍼 로더 테스트 실패: {e}")
        return False


async def test_unstructured_loader():
    """Unstructured 로더 테스트"""
    print("\n=== Unstructured 로더 테스트 ===")
    
    try:
        # Unstructured 로더 생성
        loader = AdapterFactory.create_document_loader_adapter("unstructured")
        
        # 로더 정보 출력
        print(f"로더 타입: {loader.get_loader_type()}")
        print(f"라이브러리 사용 가능: {loader.is_available()}")
        
        if not loader.is_available():
            print("Unstructured 라이브러리가 설치되지 않았습니다.")
            print(loader.get_installation_guide())
            return False
        
        loader_info = loader.get_loader_info()
        print(f"지원 확장자: {loader_info['supported_extensions']}")
        print(f"지원 기능: {loader_info['features']}")
        
        # 기존 PDF 파일로 테스트
        test_file = Path("testdata/3DM GV7 Data Sheet_0.pdf")
        
        if test_file.exists():
            # 파일 유효성 검사
            is_valid = await loader.validate_file(str(test_file))
            print(f"파일 유효성: {is_valid}")
            
            if is_valid:
                # 문서 로드
                document = await loader.load_document(str(test_file))
                
                print(f"문서 ID: {document.id}")
                print(f"문서 제목: {document.title}")
                print(f"문서 내용 길이: {len(document.content)} 문자")
                print(f"메타데이터 키: {list(document.metadata.keys())}")
                print(f"총 요소 수: {document.metadata.get('total_elements', 'N/A')}")
                print(f"요소 타입: {document.metadata.get('element_types', {})}")
                print(f"문서 내용 미리보기:\n{document.content[:200]}...")
            else:
                print("파일이 유효하지 않습니다.")
        else:
            print("테스트 파일이 존재하지 않습니다.")
        
        return True
        
    except Exception as e:
        print(f"Unstructured 로더 테스트 실패: {e}")
        return False


async def test_loader_factory():
    """로더 팩토리 테스트"""
    print("\n=== 로더 팩토리 테스트 ===")
    
    try:
        # 지원하는 모든 로더 타입 테스트
        loader_types = ["pdf", "json", "web_scraper", "unstructured"]
        
        for loader_type in loader_types:
            try:
                loader = AdapterFactory.create_document_loader_adapter(loader_type)
                print(f"✓ {loader_type} 로더 생성 성공")
                print(f"  - 타입: {loader.get_loader_type()}")
                
                if hasattr(loader, 'get_supported_extensions'):
                    extensions = loader.get_supported_extensions()
                    if extensions:
                        print(f"  - 지원 확장자: {extensions}")
                
            except Exception as e:
                print(f"✗ {loader_type} 로더 생성 실패: {e}")
        
        return True
        
    except Exception as e:
        print(f"로더 팩토리 테스트 실패: {e}")
        return False


async def main():
    """메인 테스트 함수"""
    print("새로운 문서 로더들 테스트 시작\n")
    
    results = []
    
    # 각 테스트 실행
    results.append(await test_json_loader())
    results.append(await test_web_scraper_loader())
    results.append(await test_unstructured_loader())
    results.append(await test_loader_factory())
    
    # 결과 요약
    print("\n" + "="*50)
    print("테스트 결과 요약:")
    print(f"성공: {sum(results)}/{len(results)}")
    
    if all(results):
        print("✓ 모든 테스트가 성공했습니다!")
    else:
        print("✗ 일부 테스트가 실패했습니다.")
    
    return all(results)


if __name__ == "__main__":
    asyncio.run(main())
