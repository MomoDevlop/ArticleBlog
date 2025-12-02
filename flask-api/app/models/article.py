from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import SQLAlchemy
import enum

db = SQLAlchemy()


class ArticleStatus(str, enum.Enum):
    """Article status enumeration"""
    draft = 'draft'
    published = 'published'
    archived = 'archived'


class Article(db.Model):
    """Article model"""
    __tablename__ = 'articles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), default='general')
    tags = db.Column(db.JSON, default=list)
    status = db.Column(db.Enum(ArticleStatus), default=ArticleStatus.draft, nullable=False)
    views_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Article {self.id}: {self.title}>'

    def to_dict(self):
        """Convert article to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'category': self.category,
            'tags': self.tags or [],
            'status': self.status.value if isinstance(self.status, ArticleStatus) else self.status,
            'views_count': self.views_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
        }
