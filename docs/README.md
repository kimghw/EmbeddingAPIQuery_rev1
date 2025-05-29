# 📚 EmbeddingAPIQuery 프로젝트 문서 가이드

## 📁 문서 구조

### 🏗️ 핵심 가이드 (순서대로 읽기 권장)

1. **[01_project_overview.md](01_project_overview.md)** - 프로젝트 전체 개요 및 목표
2. **[02_architecture_guide.md](02_architecture_guide.md)** - 클린 아키텍처와 설계 원칙
3. **[03_configuration_guide.md](03_configuration_guide.md)** - 시스템 설정 및 환경 구성
4. **[04_document_system_guide.md](04_document_system_guide.md)** - PDF, JSON, 웹 문서 처리
5. **[05_email_system_guide.md](05_email_system_guide.md)** - 이메일 처리 시스템 완전 가이드
6. **[06_email_troubleshooting.md](06_email_troubleshooting.md)** - 시스템 문제 해결 가이드

### 📂 아카이브 문서

이전 개발 과정에서 생성된 문서들은 `archive/` 디렉토리로 이동되었습니다:

- **adapter_switching_guide.md** - 어댑터 전환 가이드
- **dependency_injection_guide.md** - 의존성 주입 가이드
- **email_system_implementation_report.md** - 이메일 시스템 구현 보고서
- **project_summary.md** - 프로젝트 요약
- **testreport.md** - 테스트 보고서
- 기타 개발 과정 문서들

---

## 🚀 빠른 시작

### 새로운 사용자를 위한 가이드

1. **프로젝트 이해**: [01_project_overview.md](01_project_overview.md) 읽기
2. **아키텍처 파악**: [02_architecture_guide.md](02_architecture_guide.md) 학습
3. **환경 설정**: [03_configuration_guide.md](03_configuration_guide.md) 따라하기
4. **문서 처리**: [04_document_system_guide.md](04_document_system_guide.md) 참조
5. **이메일 시스템**: [05_email_system_guide.md](05_email_system_guide.md) 활용
6. **문제 발생 시**: [06_email_troubleshooting.md](06_email_troubleshooting.md) 확인

### 개발자를 위한 가이드

```bash
# 1. 환경 설정
cp .env.example .env
# .env 파일 편집 후

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 시스템 테스트
python -m pytest tests/

# 4. 문서 처리 테스트
python -m interfaces.cli.main documents process-pdf --file-path ./testdata/sample.pdf

# 5. 이메일 처리 테스트
python -m interfaces.cli.main email process-json --file-path ./sample_emails.json

# 6. API 서버 실행
python main.py
```

## 📋 시스템 기능 개요

### 🔧 핵심 기능

- **문서 처리**: PDF, JSON, 웹 페이지 로딩 및 임베딩
- **이메일 처리**: Microsoft Graph API 이메일 데이터 처리
- **벡터 검색**: Qdrant/FAISS 기반 유사도 검색
- **다중 인터페이스**: CLI, REST API, 웹훅 지원

### 🏗️ 아키텍처 특징

- **클린 아키텍처**: Core/Adapters/Interfaces 분리
- **포트/어댑터 패턴**: 확장 가능한 설계
- **의존성 주입**: 테스트 가능한 구조
- **비동기 처리**: 고성능 I/O 처리

### 🔌 지원 어댑터

- **벡터 저장소**: Qdrant, FAISS, Mock
- **임베딩 모델**: OpenAI, 커스텀 모델
- **문서 로더**: PDF, JSON, 웹 스크래핑
- **이메일 로더**: Microsoft Graph API

## 📊 사용 사례

### 1. 문서 검색 시스템
```bash
# PDF 문서 업로드 및 검색
curl -X POST "http://localhost:8000/api/documents/upload" -F "file=@manual.pdf"
curl -X POST "http://localhost:8000/api/documents/search" -d '{"query": "temperature sensor"}'
```

### 2. 이메일 분석 시스템
```bash
# 이메일 데이터 처리
curl -X POST "http://localhost:8000/api/emails/process" -d @email_data.json
curl -X POST "http://localhost:8000/api/emails/search" -d '{"query": "project update"}'
```

### 3. 채팅 기반 검색
```bash
# 자연어 질의응답
curl -X POST "http://localhost:8000/api/chat" -d '{"message": "IMU 센서 사양을 알려줘"}'
```

## 🔧 설정 및 환경

### 필수 환경 변수

```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key

# Qdrant 설정
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key

# 어댑터 선택
VECTOR_STORE_TYPE=qdrant
EMBEDDING_MODEL_TYPE=openai
DOCUMENT_LOADER_TYPE=pdf
```

### 개발 환경 설정

```bash
# Docker로 Qdrant 실행
docker run -p 6333:6333 qdrant/qdrant

# 가상환경 설정
python -m venv embedding_env
source embedding_env/bin/activate  # Linux/Mac
# embedding_env\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

## 🧪 테스트

### 테스트 실행

```bash
# 전체 테스트
python -m pytest tests/

# 특정 테스트
python -m pytest tests/test_email_system_final.py

# 통합 테스트
python -m pytest tests/test_full_pipeline.py
```

### 테스트 커버리지

- **단위 테스트**: Core 레이어 로직
- **통합 테스트**: 어댑터 연동
- **E2E 테스트**: 전체 파이프라인

## 📝 문서 업데이트 이력

- **2025-05-29**: 문서 구조 대폭 개편 및 통합
  - 6개 핵심 가이드로 재구성
  - 아카이브 디렉토리로 이전 문서 이동
  - 순차적 학습 경로 제공
- **2025-05-29**: 이메일 시스템 완전 구현
- **2025-05-29**: Qdrant 무한 루프 문제 해결

## 🔗 관련 링크

- **[프로젝트 루트 README](../README.md)** - 프로젝트 전체 개요
- **[설정 예시 파일](../.env.example)** - 환경 변수 템플릿
- **[테스트 디렉토리](../tests/)** - 테스트 코드
- **[스크립트 디렉토리](../scripts/)** - 유틸리티 스크립트

## 💡 도움이 필요하신가요?

1. **일반적인 문제**: [06_email_troubleshooting.md](06_email_troubleshooting.md) 확인
2. **설정 문제**: [03_configuration_guide.md](03_configuration_guide.md) 재검토
3. **아키텍처 이해**: [02_architecture_guide.md](02_architecture_guide.md) 학습
4. **기능별 가이드**: 해당 시스템 가이드 참조

---

**📌 참고**: 이 문서들은 프로젝트의 지속적인 발전과 함께 업데이트됩니다. 최신 정보는 각 가이드 문서를 직접 확인해 주세요.
