# 📋 프로젝트 개요 및 아키텍처

## 🎯 프로젝트 목표

**EmbeddingAPIQuery**는 문서 임베딩 및 검색 시스템으로, 다양한 형태의 문서(PDF, JSON, 웹 페이지 등)를 벡터화하여 의미 기반 검색을 제공하는 FastAPI 기반 시스템입니다.

### 핵심 기능
- 📄 **다양한 문서 형식 지원**: PDF, JSON, 웹 스크래핑
- 🧠 **임베딩 생성**: OpenAI, 로컬 모델 지원
- 🔍 **벡터 검색**: Qdrant, FAISS, Mock 벡터 스토어
- 📧 **이메일 시스템**: Microsoft Graph API 이메일 처리
- 🔄 **어댑터 패턴**: 유연한 구성 요소 교체
- 🌐 **다중 인터페이스**: REST API, CLI

## 🏗️ 시스템 아키텍처

### 클린 아키텍처 기반 설계

```
┌─────────────────────────────────────────────────────────────┐
│                    Interfaces Layer                         │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   FastAPI       │    │         CLI                     │ │
│  │   REST API      │    │      Commands                   │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Adapters Layer                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │   Vector    │ │  Embedding  │ │      Document           │ │
│  │   Stores    │ │   Models    │ │      Loaders            │ │
│  │             │ │             │ │                         │ │
│  │ • Qdrant    │ │ • OpenAI    │ │ • PDF                   │ │
│  │ • FAISS     │ │ • Local     │ │ • JSON                  │ │
│  │ • Mock      │ │             │ │ • Web Scraper           │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Core Layer                              │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   Use Cases     │    │           Entities              │ │
│  │                 │    │                                 │ │
│  │ • Document      │    │ • Document                      │ │
│  │   Processing    │    │ • Embedding                     │ │
│  │ • Document      │    │ • Email                         │ │
│  │   Retrieval     │    │ • RetrievalResult               │ │
│  │ • Email         │    │                                 │ │
│  │   Processing    │    │                                 │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    Ports                                │ │
│  │ • DocumentLoaderPort  • EmbeddingModelPort              │ │
│  │ • VectorStorePort     • TextChunkerPort                 │ │
│  │ • EmailLoaderPort     • RetrieverPort                   │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 핵심 설계 원칙

1. **의존성 역전 (Dependency Inversion)**
   - Core는 외부 구현에 의존하지 않음
   - Port/Adapter 패턴으로 추상화

2. **단일 책임 원칙 (Single Responsibility)**
   - 각 컴포넌트는 하나의 명확한 책임
   - 유스케이스별 분리된 로직

3. **개방-폐쇄 원칙 (Open-Closed)**
   - 새로운 어댑터 추가 시 기존 코드 수정 불필요
   - 설정을 통한 런타임 구성 변경

## 📁 프로젝트 구조

```
EmbeddingAPIQuery_rev1/
├── core/                    # 핵심 비즈니스 로직
│   ├── entities/           # 도메인 엔티티
│   ├── ports/              # 인터페이스 정의
│   ├── usecases/           # 비즈니스 유스케이스
│   └── services/           # 도메인 서비스
├── adapters/               # 외부 시스템 연동
│   ├── embedding/          # 임베딩 모델 어댑터
│   ├── vector_store/       # 벡터 스토어 어댑터
│   ├── pdf/                # 문서 로더 어댑터
│   └── email/              # 이메일 로더 어댑터
├── interfaces/             # 외부 인터페이스
│   ├── api/                # FastAPI 라우터
│   └── cli/                # CLI 명령어
├── config/                 # 설정 관리
├── schemas/                # Pydantic 스키마
├── tests/                  # 테스트 코드
└── docs/                   # 문서
```

## 🔧 주요 컴포넌트

### 1. Core Layer

#### Entities (엔티티)
- **Document**: 문서 메타데이터 및 내용
- **Embedding**: 벡터 임베딩 정보
- **Email**: 이메일 데이터 구조
- **RetrievalResult**: 검색 결과

#### Use Cases (유스케이스)
- **DocumentProcessingUseCase**: 문서 처리 파이프라인
- **DocumentRetrievalUseCase**: 문서 검색 로직
- **EmailProcessingUseCase**: 이메일 처리 파이프라인

#### Ports (포트)
- **DocumentLoaderPort**: 문서 로딩 인터페이스
- **EmbeddingModelPort**: 임베딩 모델 인터페이스
- **VectorStorePort**: 벡터 스토어 인터페이스
- **EmailLoaderPort**: 이메일 로더 인터페이스

### 2. Adapters Layer

#### Vector Stores
- **QdrantVectorStoreAdapter**: Qdrant 벡터 데이터베이스
- **FAISSVectorStoreAdapter**: FAISS 로컬 벡터 스토어
- **MockVectorStoreAdapter**: 테스트용 Mock 스토어

#### Embedding Models
- **OpenAIEmbeddingAdapter**: OpenAI API 임베딩
- **SemanticTextChunkerAdapter**: 의미 기반 텍스트 분할

#### Document Loaders
- **PDFLoaderAdapter**: PDF 문서 처리
- **JSONLoaderAdapter**: JSON 데이터 처리
- **WebScraperLoaderAdapter**: 웹 페이지 스크래핑

#### Email Loaders
- **JsonEmailLoaderAdapter**: Microsoft Graph JSON 처리
- **WebhookEmailLoaderAdapter**: 실시간 웹훅 처리

### 3. Interfaces Layer

#### REST API
- **Document API**: 문서 업로드 및 검색
- **Email API**: 이메일 처리 및 검색
- **Chat API**: 대화형 검색 인터페이스

#### CLI
- **Document Commands**: 문서 관련 CLI 명령
- **Email Commands**: 이메일 관련 CLI 명령

## 🔄 데이터 플로우

### 문서 처리 플로우
```
1. 문서 업로드 (PDF/JSON/URL)
   ↓
2. 문서 로더로 텍스트 추출
   ↓
3. 텍스트 청킹 (의미 단위 분할)
   ↓
4. 임베딩 모델로 벡터 생성
   ↓
5. 벡터 스토어에 저장
```

### 검색 플로우
```
1. 사용자 쿼리 입력
   ↓
2. 쿼리 임베딩 생성
   ↓
3. 벡터 유사도 검색
   ↓
4. 결과 랭킹 및 필터링
   ↓
5. 검색 결과 반환
```

### 이메일 처리 플로우
```
1. Microsoft Graph JSON 수신
   ↓
2. 이메일 엔티티 파싱
   ↓
3. 제목/본문 임베딩 생성
   ↓
4. 벡터 스토어에 저장
   ↓
5. 검색 가능한 상태
```

## 🎯 핵심 특징

### 1. 유연한 구성
- **런타임 어댑터 교체**: 설정 파일로 구성 요소 변경
- **다중 벡터 스토어**: Qdrant, FAISS 동시 지원
- **다양한 임베딩 모델**: OpenAI, 로컬 모델 지원

### 2. 확장성
- **새로운 어댑터 추가**: 기존 코드 수정 없이 확장
- **마이크로서비스 준비**: 독립적인 컴포넌트 구조
- **수평 확장**: 벡터 스토어 클러스터링 지원

### 3. 안정성
- **에러 처리**: 각 레이어별 예외 처리
- **재시도 로직**: 네트워크 오류 대응
- **모니터링**: 상세한 로깅 및 메트릭

### 4. 성능
- **배치 처리**: 대량 문서 효율적 처리
- **비동기 처리**: FastAPI 비동기 지원
- **캐싱**: 임베딩 결과 캐싱

## 🔗 관련 문서

- [시스템 설계](02_system_design.md)
- [설정 가이드](03_configuration_guide.md)
- [이메일 시스템](05_email_system_guide.md)
- [개발자 가이드](10_development_guide.md)

---

**작성일**: 2025-05-29  
**버전**: 1.0  
**상태**: 활성
