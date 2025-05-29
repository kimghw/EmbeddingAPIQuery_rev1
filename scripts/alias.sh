#!/bin/bash
# EmbeddingAPIQuery_rev1 프로젝트 Alias 설정
# 위치: scripts/alias.sh
# 사용법: source scripts/alias.sh

# =============================================================================
# 프로젝트 루트 디렉토리 설정
# =============================================================================

# scripts 폴더에서 프로젝트 루트로 이동하는 함수
goto-root() {
    if [ -f "../main.py" ]; then
        cd ..
        echo "✅ Moved to project root: $(pwd)"
    else
        echo "❌ Project root not found. Current directory: $(pwd)"
    fi
}

# 프로젝트 루트에서 실행하는 명령어들을 위한 래퍼 함수
run-from-root() {
    local current_dir=$(pwd)
    if [ ! -f "main.py" ]; then
        if [ -f "../main.py" ]; then
            cd ..
        else
            echo "❌ Cannot find project root (main.py not found)"
            return 1
        fi
    fi
    
    # 명령어 실행
    "$@"
    local exit_code=$?
    
    # 원래 디렉토리로 복귀
    cd "$current_dir"
    return $exit_code
}

# =============================================================================
# 서버 실행 관련 Alias
# =============================================================================

# FastAPI 서버 실행 (포트 8080으로 변경)
alias start-server='run-from-root uvicorn main:app --reload --host 0.0.0.0 --port 8080'
alias start-dev='run-from-root uvicorn main:app --reload --host 127.0.0.1 --port 8080'
alias start-prod='run-from-root uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4'

# 다른 포트 옵션들
alias start-8000='run-from-root uvicorn main:app --reload --host 127.0.0.1 --port 8000'
alias start-8001='run-from-root uvicorn main:app --reload --host 127.0.0.1 --port 8001'
alias start-8080='run-from-root uvicorn main:app --reload --host 127.0.0.1 --port 8080'

# 서버 상태 확인 (포트 8080 기준)
alias check-server='curl -s http://localhost:8080/health || echo "Server not running on port 8080"'
alias check-8000='curl -s http://localhost:8000/health || echo "Server not running on port 8000"'
alias check-8001='curl -s http://localhost:8001/health || echo "Server not running on port 8001"'

# API 문서 열기
alias server-docs='open http://localhost:8080/docs'
alias docs-8000='open http://localhost:8000/docs'
alias docs-8001='open http://localhost:8001/docs'

# =============================================================================
# 이메일 시스템 관련 Alias
# =============================================================================

# 이메일 처리
alias email-process='run-from-root python -m interfaces.cli.main email process-json'
alias email-stats='run-from-root python -m interfaces.cli.main email stats'
alias email-list='run-from-root python -m interfaces.cli.main email list'

# 이메일 테스트
alias test-email='run-from-root python tests/test_email_system_final.py'
alias test-email-api='run-from-root python tests/test_email_api.py'
alias test-email-complete='run-from-root python tests/test_email_complete.py'

# 이메일 디버깅
alias debug-email='run-from-root python debug_email_search.py'
alias debug-email-count='run-from-root python debug_email_count.py'
alias debug-email-list='run-from-root python debug_email_list_detailed.py'

# =============================================================================
# 문서 처리 관련 Alias
# =============================================================================

# 문서 처리
alias doc-process='run-from-root python -m interfaces.cli.main document process'
alias doc-search='run-from-root python -m interfaces.cli.main document search'
alias doc-stats='run-from-root python -m interfaces.cli.main document stats'

# 문서 테스트
alias test-doc='run-from-root python tests/test_full_pipeline.py'
alias test-qdrant='run-from-root python tests/test_qdrant_simple.py'

# =============================================================================
# 개발 및 테스트 관련 Alias
# =============================================================================

# 전체 테스트 실행
alias test-all='run-from-root python -m pytest tests/ -v'
alias test-email-all='run-from-root python -m pytest tests/test_email* -v'
alias test-doc-all='run-from-root python -m pytest tests/test_*pipeline* tests/test_*qdrant* -v'

# 설정 테스트
alias test-config='run-from-root python tests/test_config_integration.py'
alias test-adapter='run-from-root python tests/test_adapter_factory.py'

# =============================================================================
# 데이터베이스 관련 Alias
# =============================================================================

# Qdrant 관련
alias qdrant-check='run-from-root python debug_qdrant_simple.py'
alias qdrant-data='run-from-root python check_qdrant_data.py'

# 데이터 확인
alias check-embeddings='run-from-root python temp_get_all_embeddings.py'

# =============================================================================
# 유틸리티 Alias
# =============================================================================

# 환경 설정 (프로젝트 루트 기준)
alias activate-env='run-from-root source embedding_env/bin/activate'
alias install-deps='run-from-root pip install -r requirements.txt'
alias update-deps='run-from-root pip freeze > requirements.txt'

# 로그 확인
alias show-logs='run-from-root tail -f logs/*.log 2>/dev/null || echo "No log files found"'
alias clear-logs='run-from-root rm -f logs/*.log && echo "Logs cleared"'

# 프로젝트 정리
alias clean-cache='run-from-root find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; run-from-root find . -name "*.pyc" -delete 2>/dev/null; echo "Cache cleaned"'
alias clean-all='clean-cache && run-from-root rm -rf .pytest_cache && echo "All cleaned"'

# =============================================================================
# 복합 명령어 (함수 형태)
# =============================================================================

# 서버 시작 및 상태 확인 (포트 8080)
start-and-check() {
    echo "🚀 Starting FastAPI server on port 8080..."
    
    # 프로젝트 루트로 이동
    local current_dir=$(pwd)
    if [ ! -f "main.py" ]; then
        if [ -f "../main.py" ]; then
            cd ..
        else
            echo "❌ Cannot find project root"
            return 1
        fi
    fi
    
    # 서버 시작
    uvicorn main:app --reload --host 127.0.0.1 --port 8080 &
    SERVER_PID=$!
    sleep 3
    
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo "✅ Server started successfully at http://localhost:8080"
        echo "📚 API Documentation: http://localhost:8080/docs"
        echo "🔍 Server PID: $SERVER_PID"
    else
        echo "❌ Server failed to start"
        kill $SERVER_PID 2>/dev/null
    fi
    
    # 원래 디렉토리로 복귀
    cd "$current_dir"
}

# 이메일 시스템 전체 테스트
test-email-system() {
    echo "🧪 Testing Email System..."
    
    local current_dir=$(pwd)
    if [ ! -f "main.py" ]; then
        if [ -f "../main.py" ]; then
            cd ..
        else
            echo "❌ Cannot find project root"
            return 1
        fi
    fi
    
    echo "1. Basic email test..."
    python tests/test_email_basic.py
    
    echo "2. Email pipeline test..."
    python tests/test_email_pipeline.py
    
    echo "3. Email API test..."
    python tests/test_email_api.py
    
    echo "4. Final system test..."
    python tests/test_email_system_final.py
    
    echo "✅ Email system tests completed"
    
    cd "$current_dir"
}

# 개발 환경 설정
setup-dev() {
    echo "🔧 Setting up development environment..."
    
    local current_dir=$(pwd)
    if [ ! -f "main.py" ]; then
        if [ -f "../main.py" ]; then
            cd ..
        else
            echo "❌ Cannot find project root"
            return 1
        fi
    fi
    
    # 가상환경 활성화
    if [ -d "embedding_env" ]; then
        source embedding_env/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ Virtual environment not found. Creating..."
        python -m venv embedding_env
        source embedding_env/bin/activate
        echo "✅ Virtual environment created and activated"
    fi
    
    # 의존성 설치
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    
    # 환경 변수 확인
    if [ -f ".env" ]; then
        echo "✅ .env file found"
    else
        echo "⚠️  .env file not found. Copying from .env.example..."
        cp .env.example .env
        echo "📝 Please edit .env file with your settings"
    fi
    
    echo "🎉 Development environment setup completed"
    
    cd "$current_dir"
}

# 프로덕션 배포 준비
prepare-prod() {
    echo "🚀 Preparing for production deployment..."
    
    local current_dir=$(pwd)
    if [ ! -f "main.py" ]; then
        if [ -f "../main.py" ]; then
            cd ..
        else
            echo "❌ Cannot find project root"
            return 1
        fi
    fi
    
    # 테스트 실행
    echo "1. Running tests..."
    python -m pytest tests/ -v --tb=short
    
    if [ $? -eq 0 ]; then
        echo "✅ All tests passed"
    else
        echo "❌ Tests failed. Fix issues before deployment"
        cd "$current_dir"
        return 1
    fi
    
    # 의존성 업데이트
    echo "2. Updating dependencies..."
    pip freeze > requirements.txt
    
    # 캐시 정리
    echo "3. Cleaning cache..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find . -name "*.pyc" -delete 2>/dev/null
    rm -rf .pytest_cache
    
    echo "✅ Production preparation completed"
    
    cd "$current_dir"
}

# 시스템 상태 체크
health-check() {
    echo "🏥 System Health Check..."
    
    # 서버 상태 (포트 8080)
    echo "1. Checking server status (port 8080)..."
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo "✅ Server is running on port 8080"
    else
        echo "❌ Server is not running on port 8080"
        
        # 다른 포트들도 확인
        echo "   Checking other ports..."
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "   ✅ Server found on port 8000"
        elif curl -s http://localhost:8001/health > /dev/null 2>&1; then
            echo "   ✅ Server found on port 8001"
        else
            echo "   ❌ No server found on common ports"
        fi
    fi
    
    # 데이터베이스 상태
    echo "2. Checking database status..."
    local current_dir=$(pwd)
    if [ ! -f "main.py" ]; then
        if [ -f "../main.py" ]; then
            cd ..
        fi
    fi
    
    python -c "
import asyncio
import sys
sys.path.append('.')
from config.adapter_factory import AdapterFactory

async def check_db():
    try:
        factory = AdapterFactory()
        vector_store = factory.create_vector_store()
        collections = await vector_store.list_collections()
        print(f'✅ Database connected. Collections: {len(collections)}')
    except Exception as e:
        print(f'❌ Database connection failed: {e}')

asyncio.run(check_db())
"
    
    # 환경 변수 확인
    echo "3. Checking environment..."
    if [ -f ".env" ] || [ -f "../.env" ]; then
        echo "✅ Environment file exists"
    else
        echo "❌ Environment file missing"
    fi
    
    echo "🏁 Health check completed"
    
    cd "$current_dir"
}

# 빠른 이메일 검색 테스트 (포트 8080)
quick-email-search() {
    local query=${1:-"test"}
    local port=${2:-8080}
    echo "🔍 Quick email search for: '$query' on port $port"
    
    curl -s -X POST "http://localhost:$port/api/emails/search" \
         -H "Content-Type: application/json" \
         -d "{\"query\": \"$query\", \"top_k\": 5}" | \
    python -m json.tool
}

# 이메일 통계 확인 (포트 8080)
email-dashboard() {
    local port=${1:-8080}
    echo "📊 Email System Dashboard (Port: $port)"
    echo "=========================="
    
    # 서버 상태
    if curl -s http://localhost:$port/health > /dev/null 2>&1; then
        echo "🟢 Server Status: Running on port $port"
        
        # 이메일 통계 API 호출
        echo ""
        echo "📈 Email Statistics:"
        curl -s "http://localhost:$port/api/emails/stats" | python -m json.tool
        
        echo ""
        echo "📋 Recent Emails:"
        curl -s "http://localhost:$port/api/emails/list?limit=5" | python -m json.tool
        
    else
        echo "🔴 Server Status: Not Running on port $port"
        echo "Use 'start-server' to start the server"
    fi
}

# 포트 사용 현황 확인
check-ports() {
    echo "🔍 Checking port usage..."
    echo "Port 8000: $(lsof -ti:8000 > /dev/null && echo "🔴 In use" || echo "🟢 Available")"
    echo "Port 8001: $(lsof -ti:8001 > /dev/null && echo "🔴 In use" || echo "🟢 Available")"
    echo "Port 8080: $(lsof -ti:8080 > /dev/null && echo "🔴 In use" || echo "🟢 Available")"
}

# 실행 중인 서버 종료
kill-servers() {
    echo "🛑 Killing running servers..."
    
    for port in 8000 8001 8080; do
        local pid=$(lsof -ti:$port)
        if [ ! -z "$pid" ]; then
            kill $pid
            echo "   Killed process $pid on port $port"
        else
            echo "   No process running on port $port"
        fi
    done
    
    echo "✅ Server cleanup completed"
}

# =============================================================================
# 사용법 도움말
# =============================================================================

show-aliases() {
    echo "🚀 EmbeddingAPIQuery_rev1 Project Aliases"
    echo "========================================"
    echo "📍 Location: scripts/alias.sh"
    echo "💡 Usage: source scripts/alias.sh"
    echo ""
    echo "📡 Server Commands:"
    echo "  start-server    - Start FastAPI server (public, port 8080)"
    echo "  start-dev       - Start development server (local, port 8080)"
    echo "  start-8000      - Start server on port 8000"
    echo "  start-8001      - Start server on port 8001"
    echo "  start-8080      - Start server on port 8080"
    echo "  check-server    - Check if server is running (port 8080)"
    echo "  check-ports     - Check port usage status"
    echo "  kill-servers    - Kill all running servers"
    echo "  server-docs     - Open API documentation (port 8080)"
    echo ""
    echo "📧 Email Commands:"
    echo "  email-process   - Process email JSON files"
    echo "  email-stats     - Show email statistics"
    echo "  email-list      - List stored emails"
    echo "  test-email      - Run email system tests"
    echo "  debug-email     - Debug email search"
    echo ""
    echo "📄 Document Commands:"
    echo "  doc-process     - Process documents"
    echo "  doc-search      - Search documents"
    echo "  test-doc        - Run document tests"
    echo ""
    echo "🧪 Testing Commands:"
    echo "  test-all        - Run all tests"
    echo "  test-email-all  - Run all email tests"
    echo "  test-config     - Test configuration"
    echo ""
    echo "🛠️  Utility Commands:"
    echo "  goto-root       - Go to project root directory"
    echo "  activate-env    - Activate virtual environment"
    echo "  clean-cache     - Clean Python cache files"
    echo "  show-logs       - Show application logs"
    echo ""
    echo "🔧 Complex Functions:"
    echo "  start-and-check         - Start server and verify"
    echo "  test-email-system       - Run complete email tests"
    echo "  setup-dev               - Setup development environment"
    echo "  health-check            - System health check"
    echo "  email-dashboard [port]  - Show email system dashboard"
    echo "  quick-email-search <query> [port] - Quick email search test"
    echo ""
    echo "🎯 Current Status:"
    check-ports
}

# =============================================================================
# 초기화
# =============================================================================

# 별칭 로드 완료 메시지
echo "✅ EmbeddingAPIQuery_rev1 aliases loaded from scripts/alias.sh!"
echo "💡 Type 'show-aliases' to see all available commands"

# 현재 위치 확인
if [ -f "main.py" ]; then
    echo "📍 You are in the project root directory"
elif [ -f "../main.py" ]; then
    echo "📍 You are in the scripts directory"
    echo "💡 Use 'goto-root' to move to project root"
else
    echo "⚠️  Warning: Project root not found"
    echo "   Current directory: $(pwd)"
    echo "   Expected files: main.py, requirements.txt"
fi

# 서버 상태 확인
echo ""
echo "🔍 Current server status:"
check-ports
