"""
FastAPI application main module.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from config.settings import config
from interfaces.api.documents import router as documents_router
from interfaces.api.email_routes import router as email_router
from interfaces.api.email_search_routes import search_router as email_search_router
from interfaces.api.email_list_routes import router as email_list_router
from interfaces.api.chat_routes import router as chat_router

app = FastAPI(
    title=config.get_app_name(),
    version=config.get_app_version(),
    description="A clean architecture-based system for document processing and semantic retrieval"
)

# Include routers
app.include_router(documents_router)
# email_list_router를 email_router보다 먼저 등록하여 /list 경로가 /{email_id}에 가로채이지 않도록 함
app.include_router(email_list_router)
app.include_router(email_router)
app.include_router(email_search_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Document Embedding & Retrieval System",
        "version": config.get_app_version(),
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": config.get_app_name(),
        "version": config.get_app_version()
    }


@app.get("/config")
async def get_config():
    """Get current configuration (non-sensitive data only)."""
    return {
        "app_name": config.get_app_name(),
        "version": config.get_app_version(),
        "debug": config.get_debug(),
        "embedding_model": config.get_embedding_model(),
        "vector_dimension": config.get_vector_dimension(),
        "chunk_size": config.get_chunk_size(),
        "chunk_overlap": config.get_chunk_overlap(),
        "collection_name": config.get_collection_name()
    }


@app.get("/chat", response_class=HTMLResponse)
async def chat_page():
    """Serve chat interface."""
    return """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>📧 이메일 & 문서 검색 채팅</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .chat-container {
                width: 90%;
                max-width: 1200px;
                height: 90vh;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                display: flex;
                overflow: hidden;
            }
            
            .sidebar {
                width: 300px;
                background: #f8f9fa;
                border-right: 1px solid #e9ecef;
                display: flex;
                flex-direction: column;
            }
            
            .sidebar-header {
                padding: 20px;
                background: #495057;
                color: white;
                text-align: center;
            }
            
            .email-list {
                flex: 1;
                overflow-y: auto;
                padding: 10px;
            }
            
            .email-item {
                padding: 12px;
                margin-bottom: 8px;
                background: white;
                border-radius: 8px;
                cursor: pointer;
                border: 1px solid #e9ecef;
                transition: all 0.2s;
            }
            
            .email-item:hover {
                background: #e3f2fd;
                border-color: #2196f3;
            }
            
            .email-item.selected {
                background: #2196f3;
                color: white;
            }
            
            .email-sender {
                font-weight: bold;
                font-size: 14px;
                margin-bottom: 4px;
            }
            
            .email-subject {
                font-size: 13px;
                margin-bottom: 4px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            
            .email-date {
                font-size: 11px;
                opacity: 0.7;
            }
            
            .main-content {
                flex: 1;
                display: flex;
                flex-direction: column;
            }
            
            .chat-header {
                padding: 20px;
                background: #495057;
                color: white;
                text-align: center;
            }
            
            .chat-messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                background: #f8f9fa;
            }
            
            .message {
                margin-bottom: 20px;
                display: flex;
                align-items: flex-start;
            }
            
            .message.user {
                justify-content: flex-end;
            }
            
            .message-content {
                max-width: 70%;
                padding: 12px 16px;
                border-radius: 18px;
                word-wrap: break-word;
            }
            
            .message.user .message-content {
                background: #2196f3;
                color: white;
            }
            
            .message.assistant .message-content {
                background: white;
                border: 1px solid #e9ecef;
                color: #333;
            }
            
            .chat-input-container {
                padding: 20px;
                background: white;
                border-top: 1px solid #e9ecef;
                display: flex;
                gap: 10px;
            }
            
            .chat-input {
                flex: 1;
                padding: 12px 16px;
                border: 1px solid #ddd;
                border-radius: 25px;
                outline: none;
                font-size: 14px;
            }
            
            .chat-input:focus {
                border-color: #2196f3;
            }
            
            .send-button {
                padding: 12px 24px;
                background: #2196f3;
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 14px;
                transition: background 0.2s;
            }
            
            .send-button:hover {
                background: #1976d2;
            }
            
            .send-button:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            
            .search-type-selector {
                padding: 10px 20px;
                background: white;
                border-bottom: 1px solid #e9ecef;
            }
            
            .search-type-selector select {
                width: 100%;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            
            .loading {
                text-align: center;
                padding: 20px;
                color: #666;
            }
            
            .email-detail {
                display: none;
                padding: 20px;
                background: white;
                border-radius: 8px;
                margin: 10px;
                border: 1px solid #e9ecef;
            }
            
            .email-detail.show {
                display: block;
            }
            
            .email-detail-header {
                border-bottom: 1px solid #e9ecef;
                padding-bottom: 15px;
                margin-bottom: 15px;
            }
            
            .email-detail-subject {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            
            .email-detail-meta {
                font-size: 14px;
                color: #666;
                line-height: 1.5;
            }
            
            .email-detail-content {
                line-height: 1.6;
                white-space: pre-wrap;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <!-- 사이드바: 이메일 리스트 -->
            <div class="sidebar">
                <div class="sidebar-header">
                    <h3>📧 이메일 리스트</h3>
                </div>
                <div class="email-list" id="emailList">
                    <div class="loading">이메일을 불러오는 중...</div>
                </div>
            </div>
            
            <!-- 메인 컨텐츠 -->
            <div class="main-content">
                <div class="chat-header">
                    <h2>🤖 이메일 & 문서 검색 어시스턴트</h2>
                    <p>질문하시면 관련 이메일과 문서를 찾아드립니다</p>
                </div>
                
                <div class="search-type-selector">
                    <select id="searchType">
                        <option value="auto">🔍 자동 검색 (이메일 + 문서)</option>
                        <option value="emails">📧 이메일만 검색</option>
                        <option value="documents">📄 문서만 검색</option>
                    </select>
                </div>
                
                <div class="chat-messages" id="chatMessages">
                    <div class="message assistant">
                        <div class="message-content">
                            안녕하세요! 이메일과 문서 검색을 도와드리는 어시스턴트입니다. 
                            궁금한 내용을 질문해주세요. 예: "maritime safety에 대한 이메일 찾아줘"
                        </div>
                    </div>
                </div>
                
                <!-- 이메일 상세 보기 -->
                <div class="email-detail" id="emailDetail">
                    <div class="email-detail-header">
                        <div class="email-detail-subject" id="emailDetailSubject"></div>
                        <div class="email-detail-meta" id="emailDetailMeta"></div>
                    </div>
                    <div class="email-detail-content" id="emailDetailContent"></div>
                    <button onclick="closeEmailDetail()" style="margin-top: 15px; padding: 8px 16px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer;">닫기</button>
                </div>
                
                <div class="chat-input-container">
                    <input type="text" class="chat-input" id="chatInput" placeholder="질문을 입력하세요..." onkeypress="handleKeyPress(event)">
                    <button class="send-button" id="sendButton" onclick="sendMessage()">전송</button>
                </div>
            </div>
        </div>
        
        <script>
            let currentEmails = [];
            let selectedEmailId = null;
            
            // 페이지 로드 시 이메일 리스트 불러오기
            document.addEventListener('DOMContentLoaded', function() {
                loadEmailList();
            });
            
            // 이메일 리스트 불러오기
            async function loadEmailList() {
                try {
                    const response = await fetch('/emails/list');
                    const data = await response.json();
                    
                    if (data.success && data.emails) {
                        currentEmails = data.emails;
                        displayEmailList(data.emails);
                    } else {
                        document.getElementById('emailList').innerHTML = '<div class="loading">이메일이 없습니다</div>';
                    }
                } catch (error) {
                    console.error('이메일 리스트 로드 실패:', error);
                    document.getElementById('emailList').innerHTML = '<div class="loading">이메일 로드 실패</div>';
                }
            }
            
            // 이메일 리스트 표시
            function displayEmailList(emails) {
                const emailList = document.getElementById('emailList');
                
                if (emails.length === 0) {
                    emailList.innerHTML = '<div class="loading">이메일이 없습니다</div>';
                    return;
                }
                
                emailList.innerHTML = emails.map((email, index) => `
                    <div class="email-item" onclick="selectEmail('${email.id}', ${index})">
                        <div class="email-sender">${email.sender_name || 'Unknown'}</div>
                        <div class="email-subject">${email.subject || 'No Subject'}</div>
                        <div class="email-date">${formatDate(email.created_time)}</div>
                    </div>
                `).join('');
            }
            
            // 이메일 선택
            function selectEmail(emailId, index) {
                // 이전 선택 해제
                document.querySelectorAll('.email-item').forEach(item => {
                    item.classList.remove('selected');
                });
                
                // 새 선택 표시
                document.querySelectorAll('.email-item')[index].classList.add('selected');
                selectedEmailId = emailId;
                
                // 이메일 상세 정보 표시
                showEmailDetail(currentEmails[index]);
            }
            
            // 이메일 상세 보기
            function showEmailDetail(email) {
                document.getElementById('emailDetailSubject').textContent = email.subject || 'No Subject';
                document.getElementById('emailDetailMeta').innerHTML = `
                    <strong>발신자:</strong> ${email.sender_name} &lt;${email.sender_address}&gt;<br>
                    <strong>수신자:</strong> ${email.receiver_names ? email.receiver_names.join(', ') : 'Unknown'}<br>
                    <strong>날짜:</strong> ${formatDate(email.created_time)}<br>
                    <strong>스레드:</strong> ${email.correspondence_thread || 'None'}
                `;
                document.getElementById('emailDetailContent').textContent = email.body_content || 'No content';
                document.getElementById('emailDetail').classList.add('show');
                document.getElementById('chatMessages').style.display = 'none';
            }
            
            // 이메일 상세 보기 닫기
            function closeEmailDetail() {
                document.getElementById('emailDetail').classList.remove('show');
                document.getElementById('chatMessages').style.display = 'block';
            }
            
            // 날짜 포맷팅
            function formatDate(dateString) {
                if (!dateString) return 'Unknown';
                const date = new Date(dateString);
                return date.toLocaleDateString('ko-KR') + ' ' + date.toLocaleTimeString('ko-KR', {hour: '2-digit', minute: '2-digit'});
            }
            
            // 키보드 이벤트 처리
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
            
            // 메시지 전송
            async function sendMessage() {
                const input = document.getElementById('chatInput');
                const sendButton = document.getElementById('sendButton');
                const searchType = document.getElementById('searchType').value;
                const query = input.value.trim();
                
                if (!query) return;
                
                // 이메일 상세 보기가 열려있으면 닫기
                closeEmailDetail();
                
                // UI 업데이트
                input.value = '';
                sendButton.disabled = true;
                sendButton.textContent = '전송 중...';
                
                // 사용자 메시지 추가
                addMessage(query, 'user');
                
                try {
                    const response = await fetch('/chat/ask', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            query: query,
                            search_type: searchType,
                            top_k: 5
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        addMessage(data.response, 'assistant');
                    } else {
                        addMessage('죄송합니다. 오류가 발생했습니다: ' + (data.detail || '알 수 없는 오류'), 'assistant');
                    }
                } catch (error) {
                    console.error('Chat error:', error);
                    addMessage('죄송합니다. 서버와의 통신에 실패했습니다.', 'assistant');
                } finally {
                    sendButton.disabled = false;
                    sendButton.textContent = '전송';
                }
            }
            
            // 메시지 추가
            function addMessage(content, type) {
                const messagesContainer = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}`;
                
                const contentDiv = document.createElement('div');
                contentDiv.className = 'message-content';
                contentDiv.textContent = content;
                
                messageDiv.appendChild(contentDiv);
                messagesContainer.appendChild(messageDiv);
                
                // 스크롤을 맨 아래로
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        </script>
    </body>
    </html>
    """
