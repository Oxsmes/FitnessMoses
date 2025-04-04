from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.database import MealPlan, ProgressEntry
from datetime import datetime, timedelta

def get_user_meal_plans(db: Session, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve user's saved meal plans with pagination
    """
    try:
        meal_plans = (
            db.query(MealPlan)
            .filter(MealPlan.user_id == user_id)
            .order_by(MealPlan.id.desc())
            .limit(limit)
            .all()
        )
        
        return [{
            'id': plan.id,
            'date': plan.date,
            'meals': plan.meals,
            'calories': plan.calories,
            'protein': plan.protein
        } for plan in meal_plans]
    except Exception as e:
        print(f"Error retrieving meal plans: {str(e)}")
        return []

def get_user_progress_history(
    db: Session,
    user_id: int,
    days: int = 30
) -> List[Dict[str, Any]]:
    """
    Retrieve user's progress history for the specified period
    """
    try:
        start_date = datetime.now().date() - timedelta(days=days)
        entries = (
            db.query(ProgressEntry)
            .filter(
                ProgressEntry.user_id == user_id,
                ProgressEntry.date >= start_date
            )
            .order_by(ProgressEntry.date.desc())
            .all()
        )
        
        return [{
            'date': entry.date.strftime("%Y-%m-%d"),
            'weight': entry.current_weight,
            'calories': entry.calories_consumed,
            'protein': entry.protein_consumed,
            'notes': entry.notes
        } for entry in entries]
    except Exception as e:
        print(f"Error retrieving progress history: {str(e)}")
        return []

def format_meal_plan_for_display(meal_plan: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format meal plan data for display
    """
    return {
        'date': meal_plan['date'],
        'daily_calories': meal_plan['calories'],
        'daily_protein': meal_plan['protein'],
        'meals': meal_plan['meals']
    }
