"""
Markdown 유틸리티 - Frontmatter 파싱
"""
import frontmatter
from typing import Dict, Any, Tuple
from datetime import datetime


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """
    Markdown 파일에서 frontmatter와 본문 분리

    Args:
        content: Markdown 파일 내용

    Returns:
        (metadata, body) 튜플
    """
    post = frontmatter.loads(content)
    metadata = dict(post.metadata)
    body = post.content

    return metadata, body


def create_markdown(metadata: Dict[str, Any], content: str) -> str:
    """
    Frontmatter와 본문을 결합하여 Markdown 생성

    Args:
        metadata: frontmatter 딕셔너리
        content: 본문 내용

    Returns:
        완성된 Markdown 문자열
    """
    # frontmatter 생성
    post = frontmatter.Post(content, **metadata)
    return frontmatter.dumps(post)


def extract_metadata_from_page(page_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Page 데이터에서 frontmatter 생성

    Args:
        page_data: PageCreate 또는 PageUpdate 스키마 데이터

    Returns:
        frontmatter 딕셔너리
    """
    metadata = {
        "title": page_data.get("title"),
        "category": page_data.get("category"),
        "author": page_data.get("author"),
        "status": page_data.get("status", "active"),
        "created": page_data.get("created", datetime.now().isoformat()),
        "updated": datetime.now().isoformat(),
    }

    # summary가 있으면 추가
    if page_data.get("summary"):
        metadata["summary"] = page_data["summary"]

    # tags가 있으면 추가
    if page_data.get("tags"):
        metadata["tags"] = page_data["tags"]

    # None 값 제거
    metadata = {k: v for k, v in metadata.items() if v is not None}

    return metadata
