"""
Tag 모델 - 태그 시스템
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, Index
from sqlalchemy.orm import relationship
from app.db.database import Base


# 다대다 관계 테이블
page_tags = Table(
    'page_tags',
    Base.metadata,
    Column('page_id', Integer, ForeignKey('pages.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    Index('idx_page_tags_page', 'page_id'),
    Index('idx_page_tags_tag', 'tag_id')
)


class Tag(Base):
    """태그 모델"""

    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)  # 예: "종족/엘프"
    display_name = Column(String(100))  # 표시용 이름
    description = Column(Text)
    color = Column(String(7))  # 태그 색상 (#FF5733)
    usage_count = Column(Integer, server_default="0")

    # Relationships
    pages = relationship(
        "Page",
        secondary="page_tags",
        back_populates="tags",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<Tag(name={self.name}, usage={self.usage_count})>"
