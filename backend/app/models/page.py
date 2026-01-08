"""
Page 모델 - 위키 문서
"""
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, CheckConstraint, Index, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Page(Base):
    """위키 페이지 모델"""

    __tablename__ = "pages"

    # 기본 필드
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    category = Column(String(100), index=True)
    author = Column(String(100))

    # 프로젝트(세계관) 외래키
    project_id = Column(String(50), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    # 컨텐츠 캐싱 (GitHub 마크다운 원본)
    content = Column(Text, nullable=False)
    content_html = Column(Text, nullable=True)  # 선택사항: 사전 렌더링된 HTML

    # 날짜
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # 상태
    status = Column(String(20), nullable=False, server_default="active")

    # 메타데이터
    summary = Column(Text)

    # GitHub 동기화 메타데이터
    github_sha = Column(String(40))
    github_url = Column(Text)
    last_synced_at = Column(TIMESTAMP(timezone=True))

    # 조회수
    view_count = Column(Integer, server_default="0")

    # Relationships
    project = relationship("Project", back_populates="pages")
    tags = relationship(
        "Tag",
        secondary="page_tags",
        back_populates="pages",
        lazy="selectin"  # 자동으로 태그 로드
    )

    # 제약 조건
    __table_args__ = (
        CheckConstraint("status IN ('active', 'archived', 'draft')", name="status_check"),
        Index("idx_pages_updated", "updated_at"),
        # Trigram 인덱스는 Alembic 마이그레이션에서 수동 추가
    )

    def __repr__(self):
        return f"<Page(slug={self.slug}, title={self.title})>"
