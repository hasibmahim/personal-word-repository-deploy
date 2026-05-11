"""Database models for the Personal Word Repository."""
import uuid
from datetime import datetime
from wordrepo.api import db

# ----------------------
# Models
# ----------------------
class User(db.Model):
    """Model representing a user account."""
    __tablename__ = "user"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    words = db.relationship("Word", back_populates="user", cascade="all, delete-orphan")
    categories = db.relationship("Category", back_populates="user",
                                 cascade="all, delete-orphan")

class PartOfSpeech(db.Model):
    """Model representing a part of speech (noun, verb, etc.)."""
    __tablename__ = "part_of_speech"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # e.g., noun, verb
    name = db.Column(db.String(50), unique=True, nullable=False)  # e.g., "Noun"
    description = db.Column(db.String(200), nullable=True)

    words = db.relationship("Word", back_populates="part_of_speech")

class Translation(db.Model):
    """Model representing a translation of a word."""
    __tablename__ = "translation"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    word_id = db.Column(db.String(36), db.ForeignKey("word.id"), nullable=False)
    text = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(5), nullable=False)
    note = db.Column(db.String(200), nullable=True)

    word = db.relationship("Word", back_populates="translations")

class Category(db.Model):
    __tablename__ = "category"

    __table_args__ = (
        db.UniqueConstraint("user_id", "name", name="unique_user_category"),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("user.id", ondelete="CASCADE"),
                        nullable=False)

    user = db.relationship("User", back_populates="categories")
    words = db.relationship("Word", secondary="word_category", back_populates="categories")

class Word(db.Model):
    """Model representing a word stored by a user."""
    __tablename__ = "word"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("user.id", ondelete="CASCADE"),
                        nullable=False)
    text = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    part_of_speech_id = db.Column(
        db.Integer,
        db.ForeignKey("part_of_speech.id", ondelete="RESTRICT"),
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="words")
    part_of_speech = db.relationship("PartOfSpeech", back_populates="words")
    translations = db.relationship("Translation", back_populates="word",
                                   cascade="all, delete-orphan")
    categories = db.relationship("Category", secondary="word_category", back_populates="words")

# ----------------------
# Join table
# ----------------------
class WordCategory(db.Model):
    """Association table linking words to categories."""
    __tablename__ = "word_category"

    word_id = db.Column(
        db.String(36),
        db.ForeignKey("word.id", ondelete="CASCADE"),
        primary_key=True
    )

    category_id = db.Column(
        db.String(36),
        db.ForeignKey("category.id", ondelete="CASCADE"),
        primary_key=True
    )
