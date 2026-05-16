from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True) # Supabase UUID
    username = Column(String(50), unique=True, nullable=True)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String(20), default='Physics')
    chapter = Column(String(50), nullable=False)
    topic = Column(String(50))
    difficulty = Column(String(10))
    content = Column(Text, nullable=False)
    correct_answer = Column(String(10), nullable=False)
    explanation = Column(Text)
    year = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        CheckConstraint(difficulty.in_(['Easy', 'Medium', 'Hard']), name='check_difficulty'),
    )

class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    test_type = Column(String(20))
    duration_minutes = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        CheckConstraint(test_type.in_(['Chapter-wise', 'Full Syllabus', 'Mock']), name='check_test_type'),
    )

class TestQuestion(Base):
    __tablename__ = "test_questions"

    test_id = Column(Integer, ForeignKey('tests.id'), primary_key=True)
    question_id = Column(Integer, ForeignKey('questions.id'), primary_key=True)
    question_order = Column(Integer)

class TestAttempt(Base):
    __tablename__ = "test_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String) # Store Supabase UUID
    test_id = Column(Integer, ForeignKey('tests.id'))
    score = Column(Integer)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime)
    status = Column(String(20), default='In Progress')

class QuestionAttempt(Base):
    __tablename__ = "question_attempts"

    id = Column(Integer, primary_key=True, index=True)
    test_attempt_id = Column(Integer, ForeignKey('test_attempts.id'))
    question_id = Column(Integer, ForeignKey('questions.id'))
    selected_answer = Column(String(10))
    is_correct = Column(Boolean)
    time_spent_seconds = Column(Integer)
    revisit_count = Column(Integer, default=0)
    order_attempted = Column(Integer)
    answer_changed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
