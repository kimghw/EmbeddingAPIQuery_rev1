project_name: "Document Embedding & Retrieval System"
architecture: "Clean Architecture with Ports & Adapters Pattern"
version: "1.0.0"

workflow_phases:
  phase_1:
    name: "프로젝트 기반 구조 설정"
    description: "클린 아키텍처 기반 디렉터리 구조 및 기본 환경 설정"
    duration: "1-2일"
    steps:
      - step_1_1:
          task: "디렉터리 구조 생성"
          details:
            - "프로젝트 루트 디렉터리 생성"
            - "core/, adapters/, interfaces/, schemas/, tests/, docs/ 구조 생성"
            - "core/ 하위: entities/, ports/, usecases/, services/ 생성"
            - "adapters/ 하위: db/, external_api/, pdf/, embedding/, vector_store/, graph_api/ 생성"
            - "interfaces/ 하위: api/, cli/ 생성"
          
      - step_1_2:
          task: "기본 환경 설정"
          details:
            - "Python 3.12+ 가상환경 설정"
            - "pyproject.toml 또는 requirements.txt 생성"
            - "기본 라이브러리 설치: FastAPI, Click, Pydantic, asyncio"
            - ".env, .gitignore, README.md 파일 생성"
            
      - step_1_3:
          task: "설정 관리 구조 설계"
          details:
            - "config/ 디렉터리 생성"
            - "ConfigPort 인터페이스 정의"
            - "ConfigAdapter 기본 구현"
            - "환경별 설정 클래스 (dev, prod) 구조화"

  phase_2:
    name: "Core 도메인 엔티티 및 포트 정의"
    description: "비즈니스 로직의 핵심 엔티티와 외부 의존성 인터페이스 정의"
    duration: "2-3일"
    dependencies: ["phase_1"]
    steps:
      - step_2_1:
          task: "도메인 엔티티 정의"
          location: "core/entities/"
          details:
            - "Document 엔티티 (ID, 제목, 본문, 메타데이터)"
            - "DocumentChunk 엔티티 (문서 분할 정보)"
            - "Embedding 엔티티 (임베딩 벡터 정보)"
            - "RetrievalResult 엔티티 (검색 결과)"
            - "Query 엔티티 (질의 정보)"
          
      - step_2_2:
          task: "포트 인터페이스 정의"
          location: "core/ports/"
          details:
            - "DocumentLoaderPort: PDF/JSON/웹 문서 로딩 인터페이스"
            - "TextChunkerPort: 텍스트 청킹 인터페이스"
            - "EmbeddingModelPort: 임베딩 모델 호출 인터페이스"
            - "VectorStorePort: 벡터 DB 입출력 인터페이스"
            - "RetrieverPort: 검색 인터페이스"
            - "ConfigPort: 설정 관리 인터페이스"
            
      - step_2_3:
          task: "예외 클래스 정의"
          location: "core/exceptions/"
          details:
            - "DocumentNotFoundError"
            - "EmbeddingGenerationError"
            - "VectorStoreError"
            - "InvalidQueryError"

  phase_3:
    name: "Atomic 유스케이스 구현"
    description: "개별 기능 단위의 비즈니스 로직 구현"
    duration: "3-4일"
    dependencies: ["phase_2"]
    steps:
      - step_3_1:
          task: "문서 로딩 유스케이스"
          location: "core/usecases/"
          details:
            - "LoadDocumentUseCase: 다양한 형식 문서 로딩"
            - "ValidateDocumentUseCase: 문서 유효성 검증"
            - "ExtractMetadataUseCase: 메타데이터 추출"
            
      - step_3_2:
          task: "텍스트 처리 유스케이스"
          location: "core/usecases/"
          details:
            - "ChunkTextUseCase: 텍스트 청킹 처리"
            - "GenerateEmbeddingUseCase: 임베딩 생성"
            - "ValidateChunkUseCase: 청크 유효성 검증"
            
      - step_3_3:
          task: "벡터 저장 유스케이스"
          location: "core/usecases/"
          details:
            - "StoreVectorUseCase: 벡터 저장"
            - "IndexVectorUseCase: 벡터 인덱싱"
            - "RetrieveVectorUseCase: 벡터 검색"

  phase_4:
    name: "어댑터 구현"
    description: "외부 시스템 연동을 위한 구체적 구현체 개발"
    duration: "4-5일"
    dependencies: ["phase_3"]
    steps:
      - step_4_1:
          task: "문서 로더 어댑터"
          location: "adapters/pdf/, adapters/external_api/"
          details:
            - "PdfLoaderAdapter: PyPDF, PyMuPDF 구현"
            - "JsonLoaderAdapter: JSON 문서 로딩"
            - "WebLoaderAdapter: 웹 문서 크롤링"
            - "TextLoaderAdapter: 일반 텍스트 파일"
            
      - step_4_2:
          task: "임베딩 어댑터"
          location: "adapters/embedding/"
          details:
            - "OpenAIEmbeddingAdapter: OpenAI API 연동"
            - "HuggingFaceEmbeddingAdapter: HuggingFace 모델 연동"
            - "SemanticChunkerAdapter: 의미 기반 청킹"
            
      - step_4_3:
          task: "벡터 저장소 어댑터"
          location: "adapters/vector_store/"
          details:
            - "QdrantVectorStoreAdapter: Qdrant 연동"
            - "FAISSVectorStoreAdapter: FAISS 연동"
            - "ChromaVectorStoreAdapter: Chroma 연동"
            
      - step_4_4:
          task: "리트리버 어댑터"
          location: "adapters/retriever/"
          details:
            - "MultiVectorRetrieverAdapter"
            - "MultiQueryRetrieverAdapter"
            - "MMRRetrieverAdapter"

  phase_5:
    name: "Composite 서비스 구현"
    description: "여러 유스케이스를 조합한 복합 비즈니스 로직 구현"
    duration: "2-3일"
    dependencies: ["phase_4"]
    steps:
      - step_5_1:
          task: "문서 처리 서비스"
          location: "core/services/"
          details:
            - "DocumentProcessingService: 문서 업로드→청킹→임베딩→저장"
            - "BulkDocumentProcessingService: 대량 문서 처리"
            
      - step_5_2:
          task: "검색 서비스"
          location: "core/services/"
          details:
            - "DocumentSearchService: 질의→임베딩→유사도검색→결과반환"
            - "MultiModalSearchService: 다중 모달 검색"
            
      - step_5_3:
          task: "관리 서비스"
          location: "core/services/"
          details:
            - "DocumentManagementService: 문서 CRUD 관리"
            - "VectorStoreManagementService: 벡터 DB 관리"

  phase_6:
    name: "Pydantic 스키마 정의"
    description: "API 및 CLI 인터페이스용 데이터 모델 정의"
    duration: "1-2일"
    dependencies: ["phase_5"]
    steps:
      - step_6_1:
          task: "요청/응답 스키마"
          location: "schemas/"
          details:
            - "DocumentUploadRequest, DocumentUploadResponse"
            - "SearchRequest, SearchResponse"
            - "EmbeddingRequest, EmbeddingResponse"
            - "ConfigurationRequest, ConfigurationResponse"
            
      - step_6_2:
          task: "내부 전송 DTO"
          location: "schemas/"
          details:
            - "DocumentDTO, ChunkDTO"
            - "EmbeddingDTO, VectorDTO"
            - "RetrievalResultDTO"

  phase_7:
    name: "FastAPI 인터페이스 구현"
    description: "REST API 엔드포인트 구현"
    duration: "2-3일"
    dependencies: ["phase_6"]
    steps:
      - step_7_1:
          task: "API 라우터 구현"
          location: "interfaces/api/"
          details:
            - "document_router: 문서 업로드/관리 엔드포인트"
            - "search_router: 검색 관련 엔드포인트"
            - "config_router: 설정 관리 엔드포인트"
            - "health_router: 헬스체크 엔드포인트"
            
      - step_7_2:
          task: "의존성 주입 설정"
          location: "interfaces/api/dependencies/"
          details:
            - "서비스 의존성 주입 함수"
            - "어댑터 팩토리 함수"
            - "설정 주입 함수"
            
      - step_7_3:
          task: "미들웨어 및 예외 핸들러"
          location: "interfaces/api/"
          details:
            - "CORS 미들웨어"
            - "로깅 미들웨어"
            - "예외 핸들러 (HTTP 상태코드 매핑)"

  phase_8:
    name: "CLI 인터페이스 구현"
    description: "Click 기반 명령행 인터페이스 구현"
    duration: "2일"
    dependencies: ["phase_6"]
    steps:
      - step_8_1:
          task: "CLI 명령어 그룹"
          location: "interfaces/cli/"
          details:
            - "document 그룹: upload, list, delete 명령어"
            - "search 그룹: search, configure 명령어"
            - "config 그룹: set, get, list 명령어"
            
      - step_8_2:
          task: "CLI 어댑터 구현"
          location: "interfaces/cli/"
          details:
            - "동기/비동기 브릿지 (asyncio.run 활용)"
            - "JSON 출력 포매터"
            - "에러 핸들링 및 사용자 친화적 메시지"

  phase_9:
    name: "설정 관리 완성"
    description: "환경별 설정 관리 및 Factory 패턴 구현"
    duration: "1일"
    dependencies: ["phase_7", "phase_8"]
    steps:
      - step_9_1:
          task: "설정 클래스 완성"
          location: "config/"
          details:
            - "BaseConfig, DevelopmentConfig, ProductionConfig"
            - "Pydantic Settings 적용"
            - "환경변수 우선순위 설정"
            
      - step_9_2:
          task: "설정 Factory 구현"
          location: "config/"
          details:
            - "ConfigFactory: 환경별 설정 자동 선택"
            - "설정 검증 로직"
            - "API/CLI 공통 설정 주입"

  phase_10:
    name: "테스트 구현"
    description: "단위 테스트, 통합 테스트 및 E2E 테스트 구현"
    duration: "3-4일"
    dependencies: ["phase_9"]
    steps:
      - step_10_1:
          task: "단위 테스트"
          location: "tests/unit/"
          details:
            - "엔티티 테스트"
            - "유스케이스 테스트 (목킹 활용)"
            - "서비스 테스트"
            - "어댑터 테스트"
            
      - step_10_2:
          task: "통합 테스트"
          location: "tests/integration/"
          details:
            - "API 엔드포인트 테스트"
            - "CLI 명령어 테스트"
            - "실제 외부 서비스 연동 테스트"
            
      - step_10_3:
          task: "E2E 테스트"
          location: "tests/e2e/"
          details:
            - "전체 워크플로우 테스트"
            - "문서 업로드→검색→결과 검증"
            - "성능 테스트"

  phase_11:
    name: "문서화 및 배포 준비"
    description: "API 문서, 사용자 가이드 작성 및 배포 설정"
    duration: "2일"
    dependencies: ["phase_10"]
    steps:
      - step_11_1:
          task: "API 문서화"
          location: "docs/"
          details:
            - "OpenAPI/Swagger 문서 자동 생성"
            - "엔드포인트별 상세 설명"
            - "요청/응답 예제"
            
      - step_11_2:
          task: "사용자 가이드"
          location: "docs/"
          details:
            - "설치 및 설정 가이드"
            - "CLI 사용법"
            - "API 사용 예제"
            - "아키텍처 설명서"
            
      - step_11_3:
          task: "배포 설정"
          details:
            - "Docker 컨테이너화"
            - "환경변수 설정 가이드"
            - "의존성 관리"

  phase_12:
    name: "통합 검증 및 최적화"
    description: "전체 시스템 통합 검증 및 성능 최적화"
    duration: "2-3일"
    dependencies: ["phase_11"]
    steps:
      - step_12_1:
          task: "통합 검증"
          details:
            - "모든 컴포넌트 연동 확인"
            - "다양한 문서 형식 테스트"
            - "대용량 데이터 처리 검증"
            
      - step_12_2:
          task: "성능 최적화"
          details:
            - "비동기 처리 최적화"
            - "메모리 사용량 최적화"
            - "벡터 검색 성능 튜닝"
            
      - step_12_3:
          task: "모니터링 설정"
          details:
            - "로깅 시스템 완성"
            - "에러 트래킹 (Sentry 등)"
            - "성능 메트릭 수집"

delivery_milestones:
  milestone_1:
    name: "기본 아키텍처 완성"
    phases: ["phase_1", "phase_2", "phase_3"]
    delivery_date: "1주차 말"
    
  milestone_2:
    name: "핵심 기능 구현 완성"
    phases: ["phase_4", "phase_5"]
    delivery_date: "2주차 말"
    
  milestone_3:
    name: "인터페이스 구현 완성"
    phases: ["phase_6", "phase_7", "phase_8", "phase_9"]
    delivery_date: "3주차 말"
    
  milestone_4:
    name: "최종 제품 완성"
    phases: ["phase_10", "phase_11", "phase_12"]
    delivery_date: "4주차 말"

quality_gates:
  - name: "아키텍처 준수"
    criteria: "포트/어댑터 패턴 올바른 적용"
  - name: "테스트 커버리지"
    criteria: "단위 테스트 80% 이상"
  - name: "성능 요구사항"
    criteria: "문서 처리 속도 및 검색 응답시간"
  - name: "API 문서 완성도"
    criteria: "모든 엔드포인트 문서화 완료"

risk_management:
  technical_risks:
    - risk: "외부 API 연동 실패"
      mitigation: "Mock 어댑터 우선 구현, 점진적 실제 연동"
    - risk: "벡터 DB 성능 이슈"
      mitigation: "여러 벡터 DB 어댑터 병렬 구현, 성능 비교"
    - risk: "대용량 문서 처리 메모리 부족"
      mitigation: "스트리밍 처리 및 청킹 최적화"
      
  schedule_risks:
    - risk: "외부 라이브러리 학습 곡선"
      mitigation: "초기 POC 및 스파이크 작업"
    - risk: "테스트 작성 지연"
      mitigation: "TDD 접근법, 개발과 테스트 병렬 진행"