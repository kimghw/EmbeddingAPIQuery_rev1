"""
Web Scraper Document Loader Adapter
"""

import uuid
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from core.ports.document_loader import DocumentLoaderPort
from core.entities.document import Document


class WebScraperLoaderAdapter(DocumentLoaderPort):
    """웹 스크래퍼 문서 로더 어댑터"""
    
    def __init__(
        self,
        timeout: int = 30,
        max_retries: int = 3,
        user_agent: str = "Mozilla/5.0 (compatible; DocumentLoader/1.0)",
        max_content_length: int = 10 * 1024 * 1024  # 10MB
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent
        self.max_content_length = max_content_length
        self.supported_schemes = ['http', 'https']
    
    async def load_from_file(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """파일에서 로드 (구현하지 않음)"""
        raise NotImplementedError("웹 스크래퍼는 파일 로드를 지원하지 않습니다. URL을 사용해주세요.")
    
    async def load_from_bytes(self, content: bytes, filename: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """바이트 데이터에서 HTML 문서 로드"""
        try:
            # 바이트를 문자열로 변환
            html_content = content.decode('utf-8')
            
            # BeautifulSoup으로 파싱
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 텍스트 추출 및 메타데이터 생성
            text_content = self._extract_text_content(soup)
            
            # 메타데이터 생성
            doc_metadata = {
                'filename': filename,
                'file_size': len(content),
                'loader_type': 'web_scraper',
                'scraped_at': datetime.utcnow().isoformat(),
                'source': 'bytes'
            }
            
            # HTML에서 메타데이터 추출
            html_metadata = self._extract_html_metadata(soup)
            doc_metadata.update(html_metadata)
            
            # 사용자 제공 메타데이터 병합
            if metadata:
                doc_metadata.update(metadata)
            
            # Document 생성
            document = Document.create(
                title=doc_metadata.get('title', filename),
                content=text_content,
                metadata=doc_metadata,
                document_id=str(uuid.uuid4())
            )
            
            return document
            
        except UnicodeDecodeError as e:
            raise ValueError(f"HTML 디코딩 오류: {e}")
        except Exception as e:
            raise RuntimeError(f"바이트 데이터 로드 중 오류 발생: {e}")
    
    async def load_from_url(self, url: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """URL에서 웹 페이지 로드"""
        if not self._is_valid_url(url):
            raise ValueError(f"유효하지 않은 URL: {url}")
        
        try:
            content, doc_metadata = await self._scrape_url(url)
            
            # 사용자 제공 메타데이터 병합
            if metadata:
                doc_metadata.update(metadata)
            
            # Document 생성
            document = Document.create(
                title=doc_metadata.get('title', self._extract_title_from_url(url)),
                content=content,
                metadata=doc_metadata,
                document_id=str(uuid.uuid4())
            )
            
            return document
            
        except Exception as e:
            raise RuntimeError(f"웹 페이지 로드 중 오류 발생 ({url}): {e}")
    
    async def load_multiple_files(self, file_paths: List[str], metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """여러 URL에서 웹 페이지 로드"""
        documents = []
        
        # 동시 요청 제한 (최대 5개)
        semaphore = asyncio.Semaphore(5)
        
        async def load_single_url(url: str) -> Optional[Document]:
            async with semaphore:
                try:
                    return await self.load_from_url(url, metadata)
                except Exception as e:
                    print(f"URL 로드 실패 ({url}): {e}")
                    return None
        
        # 모든 URL을 동시에 처리
        tasks = [load_single_url(url) for url in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 성공한 결과만 수집
        for result in results:
            if isinstance(result, Document):
                documents.append(result)
        
        return documents
    
    def get_supported_formats(self) -> List[str]:
        """지원하는 파일 형식 반환 (웹 스크래퍼는 URL 스키마)"""
        return self.supported_schemes.copy()
    
    def is_format_supported(self, file_extension: str) -> bool:
        """파일 형식 지원 여부 확인 (URL 스키마 확인)"""
        return file_extension.lower() in self.supported_schemes
    
    async def _scrape_url(self, url: str) -> tuple[str, Dict[str, Any]]:
        """URL에서 콘텐츠 스크래핑"""
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url, headers=headers) as response:
                        # 응답 상태 확인
                        response.raise_for_status()
                        
                        # 콘텐츠 크기 확인
                        content_length = response.headers.get('content-length')
                        if content_length and int(content_length) > self.max_content_length:
                            raise ValueError(f"콘텐츠가 너무 큽니다: {content_length} bytes")
                        
                        # HTML 콘텐츠 읽기
                        html_content = await response.text()
                        
                        # BeautifulSoup으로 파싱
                        soup = BeautifulSoup(html_content, 'html.parser')
                        
                        # 텍스트 추출 및 메타데이터 생성
                        content = self._extract_text_content(soup)
                        metadata = self._extract_metadata(soup, url, response)
                        
                        return content, metadata
                        
            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # 지수 백오프
                    continue
                raise TimeoutError(f"URL 요청 시간 초과: {url}")
            
            except aiohttp.ClientError as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise ConnectionError(f"HTTP 요청 실패: {e}")
        
        raise RuntimeError(f"최대 재시도 횟수 초과: {url}")
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """HTML에서 텍스트 콘텐츠 추출"""
        # 불필요한 태그 제거
        for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            tag.decompose()
        
        # 주요 콘텐츠 영역 찾기
        main_content = None
        
        # 일반적인 메인 콘텐츠 선택자들
        main_selectors = [
            'main',
            'article',
            '[role="main"]',
            '.main-content',
            '.content',
            '#main',
            '#content'
        ]
        
        for selector in main_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # 메인 콘텐츠를 찾지 못하면 body 사용
        if not main_content:
            main_content = soup.find('body') or soup
        
        # 텍스트 추출
        text_parts = []
        
        # 제목 추출
        title_tags = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for tag in title_tags:
            text = tag.get_text(strip=True)
            if text:
                text_parts.append(f"\n{text}\n")
        
        # 단락 추출
        paragraph_tags = main_content.find_all(['p', 'div', 'section'])
        for tag in paragraph_tags:
            text = tag.get_text(strip=True)
            if text and len(text) > 20:  # 너무 짧은 텍스트 제외
                text_parts.append(text)
        
        # 리스트 추출
        list_tags = main_content.find_all(['ul', 'ol'])
        for tag in list_tags:
            items = tag.find_all('li')
            for item in items:
                text = item.get_text(strip=True)
                if text:
                    text_parts.append(f"• {text}")
        
        # 텍스트 정리 및 결합
        content = '\n\n'.join(text_parts)
        content = self._clean_text(content)
        
        return content
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str, response) -> Dict[str, Any]:
        """HTML에서 메타데이터 추출"""
        metadata = {
            'url': url,
            'loader_type': 'web_scraper',
            'scraped_at': datetime.utcnow().isoformat(),
            'status_code': response.status,
            'content_type': response.headers.get('content-type', ''),
        }
        
        # HTML 메타데이터 추출
        html_metadata = self._extract_html_metadata(soup)
        metadata.update(html_metadata)
        
        # 도메인 정보
        parsed_url = urlparse(url)
        metadata['domain'] = parsed_url.netloc
        metadata['scheme'] = parsed_url.scheme
        
        return metadata
    
    def _extract_html_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """HTML에서 메타데이터만 추출"""
        metadata = {}
        
        # 제목 추출
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text(strip=True)
        
        # 메타 태그 정보 추출
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            name = tag.get('name') or tag.get('property')
            content = tag.get('content')
            
            if name and content:
                if name.lower() in ['description', 'og:description']:
                    metadata['description'] = content
                elif name.lower() in ['keywords', 'og:keywords']:
                    metadata['keywords'] = content
                elif name.lower() in ['author', 'og:author']:
                    metadata['author'] = content
                elif name.lower() == 'og:title':
                    metadata['og_title'] = content
                elif name.lower() == 'og:url':
                    metadata['og_url'] = content
        
        # 언어 정보
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            metadata['language'] = html_tag.get('lang')
        
        return metadata
    
    def _clean_text(self, text: str) -> str:
        """텍스트 정리"""
        # 연속된 공백 제거
        import re
        text = re.sub(r'\s+', ' ', text)
        
        # 연속된 줄바꿈 제거 (최대 2개까지)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 앞뒤 공백 제거
        text = text.strip()
        
        return text
    
    def _is_valid_url(self, url: str) -> bool:
        """URL 유효성 검사"""
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme in self.supported_schemes and
                parsed.netloc and
                len(url) < 2048  # URL 길이 제한
            )
        except Exception:
            return False
    
    def _extract_title_from_url(self, url: str) -> str:
        """URL에서 제목 추출"""
        try:
            parsed = urlparse(url)
            path = parsed.path.strip('/')
            if path:
                # 마지막 경로 세그먼트를 제목으로 사용
                title = path.split('/')[-1]
                # 파일 확장자 제거
                if '.' in title:
                    title = title.rsplit('.', 1)[0]
                # 하이픈이나 언더스코어를 공백으로 변경
                title = title.replace('-', ' ').replace('_', ' ')
                return title.title()
            else:
                return parsed.netloc
        except Exception:
            return url
    
    # 기존 메서드들과의 호환성을 위한 별칭
    async def load_document(self, url: str) -> Document:
        """단일 문서 로드 (호환성)"""
        return await self.load_from_url(url)
    
    async def load_multiple_documents(self, urls: List[str]) -> List[Document]:
        """여러 문서 로드 (호환성)"""
        return await self.load_multiple_files(urls)
    
    def get_loader_type(self) -> str:
        """로더 타입 반환 (호환성)"""
        return "web_scraper"
    
    def get_loader_info(self) -> Dict[str, Any]:
        """로더 정보 반환 (호환성)"""
        return {
            "type": self.get_loader_type(),
            "supported_schemes": self.supported_schemes,
            "features": [
                "html_parsing",
                "content_extraction",
                "metadata_extraction",
                "concurrent_scraping",
                "retry_mechanism",
                "timeout_handling",
                "content_size_limiting"
            ],
            "description": "웹 페이지를 스크래핑하여 텍스트 콘텐츠와 메타데이터를 추출",
            "settings": {
                "timeout": self.timeout,
                "max_retries": self.max_retries,
                "max_content_length": self.max_content_length,
                "user_agent": self.user_agent
            }
        }
    
    async def validate_file(self, url: str) -> bool:
        """URL 유효성 검사 (호환성)"""
        if not self._is_valid_url(url):
            return False
        
        try:
            # HEAD 요청으로 URL 접근 가능성 확인
            timeout = aiohttp.ClientTimeout(total=10)
            headers = {'User-Agent': self.user_agent}
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.head(url, headers=headers) as response:
                    return response.status < 400
                    
        except Exception:
            return False
    
    def set_timeout(self, timeout: int) -> None:
        """타임아웃 설정"""
        self.timeout = max(1, timeout)
    
    def set_max_retries(self, max_retries: int) -> None:
        """최대 재시도 횟수 설정"""
        self.max_retries = max(0, max_retries)
    
    def set_user_agent(self, user_agent: str) -> None:
        """User-Agent 설정"""
        self.user_agent = user_agent
    
    def set_max_content_length(self, max_length: int) -> None:
        """최대 콘텐츠 크기 설정"""
        self.max_content_length = max(1024, max_length)
