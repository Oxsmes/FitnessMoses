from sqlalchemy.orm import Session
from models.database import User, MealPlan
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

def create_user(
    db: Session,
    weight: float,
    height: float,
    age: int,
    gender: str,
    activity_level: str,
    goal: str,
    dietary_restrictions: List[str],
    cuisine_preferences: List[str]
) -> Optional[User]:
    """Create a new user profile with error handling"""
    try:
        db_user = User(
            weight=weight,
            height=height,
            age=age,
            gender=gender,
            activity_level=activity_level,
            goal=goal,
            dietary_restrictions=dietary_restrictions,
            cuisine_preferences=cuisine_preferences
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        db.rollback()
        raise Exception(f"Error creating user: {str(e)}")

def save_meal_plan(
    db: Session,
    user_id: int,
    meal_plan: Dict[str, Any],
    calories: float,
    protein: float
) -> Optional[MealPlan]:
    """Save a generated meal plan with error handling"""
    try:
        db_meal_plan = MealPlan(
            user_id=user_id,
            meals=meal_plan,
            calories=calories,
            protein=protein,
            date=datetime.now().strftime("%Y-%m-%d")
        )
        db.add(db_meal_plan)
        db.commit()
        db.refresh(db_meal_plan)
        return db_meal_plan
    except Exception as e:
        db.rollback()
        raise Exception(f"Error saving meal plan: {str(e)}")

def get_user_meal_plans(db: Session, user_id: int) -> List[MealPlan]:
    """Get all meal plans for a user with error handling"""
    try:
        return db.query(MealPlan).filter(MealPlan.user_id == user_id).all()
    except Exception as e:
        raise Exception(f"Error retrieving meal plans: {str(e)}")

def get_latest_meal_plan(db: Session, user_id: int) -> Optional[MealPlan]:
    """Get the most recent meal plan for a user with error handling"""
    try:
        return db.query(MealPlan).filter(MealPlan.user_id == user_id).order_by(MealPlan.id.desc()).first()
    except Exception as e:
        raise Exception(f"Error retrieving latest meal plan: {str(e)}")