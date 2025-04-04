from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, JSON, text, Date, Boolean, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import QueuePool
import os
import time
from contextlib import contextmanager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Get database URL from environment variable
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise Exception("DATABASE_URL environment variable is not set")

# Create base class for declarative models
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_active = Column(Boolean, default=True)

    # Profile information
    weight = Column(Float)
    height = Column(Float)
    age = Column(Integer)
    gender = Column(String)
    activity_level = Column(String)
    goal = Column(String)
    dietary_restrictions = Column(JSON)
    cuisine_preferences = Column(JSON)

    # Relationships
    meal_plans = relationship("MealPlan", back_populates="user")
    progress_entries = relationship("ProgressEntry", back_populates="user")
    workout_schedules = relationship("WorkoutSchedule", back_populates="user")
    custom_exercises = relationship("CustomExercise", back_populates="user")
    water_intakes = relationship("WaterIntake", back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class CustomExercise(Base):
    __tablename__ = "custom_exercises"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    muscle_group = Column(String, nullable=False)
    equipment = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="custom_exercises")

class WaterIntake(Base):
    __tablename__ = "water_intake"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount_ml = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="water_intakes")

class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(String)
    meals = Column(JSON)  # Store meal plan as JSON
    calories = Column(Float)
    protein = Column(Float)

    user = relationship("User", back_populates="meal_plans")

class ProgressEntry(Base):
    __tablename__ = "progress_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, default=datetime.now().date)
    current_weight = Column(Float)
    calories_consumed = Column(Float)
    protein_consumed = Column(Float)
    notes = Column(String, nullable=True)

    user = relationship("User", back_populates="progress_entries")

class WorkoutSchedule(Base):
    __tablename__ = "workout_schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, default=datetime.now().date)
    schedule = Column(JSON)  # Store weekly workout schedule as JSON
    preferences = Column(JSON)  # Store workout preferences
    is_custom = Column(Boolean, default=False)  # Whether it's a custom or generated schedule

    user = relationship("User", back_populates="workout_schedules")

# Create database engine with improved connection pool settings
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
    connect_args={
        "connect_timeout": 30,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
        "sslmode": "require"
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@contextmanager
def get_db_with_retry(max_retries=3, retry_delay=1):
    """Get database session with improved retry mechanism and proper cleanup"""
    attempt = 0
    db = None
    while attempt < max_retries:
        try:
            db = SessionLocal()
            # Test the connection
            db.execute(text("SELECT 1"))
            yield db
            # If we get here, the connection worked
            if db:
                try:
                    db.commit()  # Commit any pending transactions
                except Exception as e:
                    db.rollback()
                    print(f"Error during commit: {str(e)}")
                    raise
            break
        except Exception as e:
            if db:
                try:
                    db.rollback()
                except Exception as rollback_error:
                    print(f"Error during rollback: {str(rollback_error)}")

            attempt += 1
            if attempt == max_retries:
                print(f"Failed to connect to database after {max_retries} attempts: {str(e)}")
                raise Exception(f"Database connection error: {str(e)}")
            print(f"Connection attempt {attempt} failed, retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        finally:
            if db:
                try:
                    db.close()
                except Exception as close_error:
                    print(f"Error closing database connection: {str(close_error)}")

def get_db():
    """Database session generator with improved error handling"""
    try:
        with get_db_with_retry() as db:
            yield db
    except Exception as e:
        print(f"Error in get_db: {str(e)}")
        raise

# Initialize database
def init_db():
    try:
        print("Starting database initialization...")
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")

        # Verify users table exists
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM information_schema.tables 
                    WHERE table_name = 'users'
                );
            """))
            if result.scalar():
                print("Users table exists")
            else:
                print("Warning: Users table not found")
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        raise

# Initialize database
init_db()