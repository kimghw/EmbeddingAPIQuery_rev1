"""
Chat API routes for interactive Q&A interface.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from config.adapter_factory import get_document_retrieval_use_case, get_email_retrieval_use_case
from core.usecases.document_retrieval import DocumentRetrievalUseCase
from core.usecases.email_retrieval import EmailRetrievalUseCase

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    """Chat message model."""
    message: str
    timestamp: datetime
    type: str  # 'user' or 'assistant'
    metadata: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    """Chat request model."""
    query: str
    search_type: Optional[str] = "auto"  # 'documents', 'emails', 'auto'
    top_k: Optional[int] = 5


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    sources: List[Dict[str, Any]]
    search_type: str
    timestamp: datetime
    metadata: Dict[str, Any]


@router.post("/ask", response_model=ChatResponse)
async def chat_ask(
    request: ChatRequest,
    doc_retrieval: DocumentRetrievalUseCase = Depends(get_document_retrieval_use_case),
    email_retrieval: EmailRetrievalUseCase = Depends(get_email_retrieval_use_case)
):
    """
    Process chat query and return intelligent response.
    """
    try:
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Determine search type
        search_type = _determine_search_type(query, request.search_type)
        
        # Perform search based on type
        if search_type == "emails":
            result = await _search_emails(query, request.top_k, email_retrieval)
        elif search_type == "documents":
            result = await _search_documents(query, request.top_k, doc_retrieval)
        else:  # auto - search both
            result = await _search_both(query, request.top_k, doc_retrieval, email_retrieval)
        
        # Generate response
        response_text = _generate_response(query, result, search_type)
        
        return ChatResponse(
            response=response_text,
            sources=result.get("sources", []),
            search_type=search_type,
            timestamp=datetime.utcnow(),
            metadata={
                "query": query,
                "total_results": len(result.get("sources", [])),
                "search_strategy": result.get("strategy", "unknown")
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


def _determine_search_type(query: str, requested_type: str) -> str:
    """Determine the best search type based on query content."""
    if requested_type in ["documents", "emails"]:
        return requested_type
    
    # Auto-detection based on keywords
    email_keywords = [
        "email", "메일", "sender", "발신자", "recipient", "수신자", 
        "correspondence", "회신", "thread", "스레드", "PL", "MSC"
    ]
    
    doc_keywords = [
        "document", "문서", "specification", "사양", "manual", "매뉴얼",
        "datasheet", "데이터시트", "technical", "기술", "IMU", "sensor"
    ]
    
    query_lower = query.lower()
    
    email_score = sum(1 for keyword in email_keywords if keyword.lower() in query_lower)
    doc_score = sum(1 for keyword in doc_keywords if keyword.lower() in query_lower)
    
    if email_score > doc_score:
        return "emails"
    elif doc_score > email_score:
        return "documents"
    else:
        return "auto"


async def _search_emails(query: str, top_k: int, email_retrieval: EmailRetrievalUseCase) -> Dict[str, Any]:
    """Search emails and format results."""
    try:
        # Try text search first
        result = await email_retrieval.search_emails_by_text(query, top_k)
        
        if result.get("success") and result.get("results"):
            sources = []
            for email_result in result["results"]:
                sources.append({
                    "type": "email",
                    "subject": email_result.get("subject", ""),
                    "sender": email_result.get("sender_name", ""),
                    "content_preview": email_result.get("content_preview", ""),
                    "score": email_result.get("score", 0),
                    "correspondence_thread": email_result.get("correspondence_thread"),
                    "created_time": email_result.get("created_time")
                })
            
            return {
                "sources": sources,
                "strategy": "email_text_search",
                "total_found": len(sources)
            }
        
        return {"sources": [], "strategy": "email_search_failed", "total_found": 0}
        
    except Exception as e:
        return {"sources": [], "strategy": f"email_search_error: {str(e)}", "total_found": 0}


async def _search_documents(query: str, top_k: int, doc_retrieval: DocumentRetrievalUseCase) -> Dict[str, Any]:
    """Search documents and format results."""
    try:
        result = await doc_retrieval.search_documents(query, top_k)
        
        if result.get("success") and result.get("results"):
            sources = []
            for doc_result in result["results"]:
                sources.append({
                    "type": "document",
                    "title": doc_result.get("title", ""),
                    "content": doc_result.get("content", ""),
                    "score": doc_result.get("score", 0),
                    "chunk_id": doc_result.get("chunk_id"),
                    "document_id": doc_result.get("document_id")
                })
            
            return {
                "sources": sources,
                "strategy": "document_search",
                "total_found": len(sources)
            }
        
        return {"sources": [], "strategy": "document_search_failed", "total_found": 0}
        
    except Exception as e:
        return {"sources": [], "strategy": f"document_search_error: {str(e)}", "total_found": 0}


async def _search_both(query: str, top_k: int, doc_retrieval: DocumentRetrievalUseCase, email_retrieval: EmailRetrievalUseCase) -> Dict[str, Any]:
    """Search both documents and emails, then combine results."""
    try:
        # Search both in parallel
        email_result = await _search_emails(query, top_k // 2, email_retrieval)
        doc_result = await _search_documents(query, top_k // 2, doc_retrieval)
        
        # Combine sources
        all_sources = email_result.get("sources", []) + doc_result.get("sources", [])
        
        # Sort by score if available
        all_sources.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        return {
            "sources": all_sources[:top_k],
            "strategy": "combined_search",
            "total_found": len(all_sources),
            "email_found": len(email_result.get("sources", [])),
            "document_found": len(doc_result.get("sources", []))
        }
        
    except Exception as e:
        return {"sources": [], "strategy": f"combined_search_error: {str(e)}", "total_found": 0}


def _generate_response(query: str, search_result: Dict[str, Any], search_type: str) -> str:
    """Generate intelligent response based on search results."""
    sources = search_result.get("sources", [])
    total_found = search_result.get("total_found", 0)
    
    if not sources:
        return f"죄송합니다. '{query}'에 대한 관련 정보를 찾을 수 없습니다. 다른 키워드로 검색해보시거나 더 구체적인 질문을 해주세요."
    
    # Generate response based on search type
    if search_type == "emails":
        return _generate_email_response(query, sources, total_found)
    elif search_type == "documents":
        return _generate_document_response(query, sources, total_found)
    else:  # combined
        return _generate_combined_response(query, sources, total_found, search_result)


def _generate_email_response(query: str, sources: List[Dict], total_found: int) -> str:
    """Generate response for email search results."""
    response = f"'{query}'에 대한 이메일 검색 결과 {total_found}개를 찾았습니다.\n\n"
    
    for i, source in enumerate(sources[:3], 1):
        response += f"📧 **{i}. {source.get('subject', 'No Subject')}**\n"
        response += f"   발신자: {source.get('sender', 'Unknown')}\n"
        
        if source.get('correspondence_thread'):
            response += f"   스레드: {source.get('correspondence_thread')}\n"
        
        if source.get('content_preview'):
            preview = source['content_preview'][:200] + "..." if len(source['content_preview']) > 200 else source['content_preview']
            response += f"   내용: {preview}\n"
        
        response += f"   유사도: {source.get('score', 0):.3f}\n\n"
    
    if len(sources) > 3:
        response += f"... 외 {len(sources) - 3}개 결과가 더 있습니다."
    
    return response


def _generate_document_response(query: str, sources: List[Dict], total_found: int) -> str:
    """Generate response for document search results."""
    response = f"'{query}'에 대한 문서 검색 결과 {total_found}개를 찾았습니다.\n\n"
    
    for i, source in enumerate(sources[:3], 1):
        response += f"📄 **{i}. {source.get('title', 'Untitled Document')}**\n"
        
        content = source.get('content', '')
        if content:
            preview = content[:300] + "..." if len(content) > 300 else content
            response += f"   내용: {preview}\n"
        
        response += f"   유사도: {source.get('score', 0):.3f}\n\n"
    
    if len(sources) > 3:
        response += f"... 외 {len(sources) - 3}개 결과가 더 있습니다."
    
    return response


def _generate_combined_response(query: str, sources: List[Dict], total_found: int, search_result: Dict) -> str:
    """Generate response for combined search results."""
    email_count = search_result.get("email_found", 0)
    doc_count = search_result.get("document_found", 0)
    
    response = f"'{query}'에 대한 통합 검색 결과:\n"
    response += f"📧 이메일 {email_count}개, 📄 문서 {doc_count}개 (총 {total_found}개)\n\n"
    
    # Group by type
    emails = [s for s in sources if s.get('type') == 'email']
    documents = [s for s in sources if s.get('type') == 'document']
    
    if emails:
        response += "**📧 관련 이메일:**\n"
        for i, email in enumerate(emails[:2], 1):
            response += f"{i}. {email.get('subject', 'No Subject')} (발신자: {email.get('sender', 'Unknown')})\n"
        response += "\n"
    
    if documents:
        response += "**📄 관련 문서:**\n"
        for i, doc in enumerate(documents[:2], 1):
            response += f"{i}. {doc.get('title', 'Untitled Document')}\n"
        response += "\n"
    
    response += "더 자세한 정보가 필요하시면 구체적인 질문을 해주세요."
    
    return response


@router.get("/history")
async def get_chat_history():
    """Get chat history (placeholder for future implementation)."""
    return {
        "message": "Chat history feature will be implemented in future versions",
        "history": []
    }


@router.delete("/history")
async def clear_chat_history():
    """Clear chat history (placeholder for future implementation)."""
    return {
        "message": "Chat history cleared",
        "success": True
    }
