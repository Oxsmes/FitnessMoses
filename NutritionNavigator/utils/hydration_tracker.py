
from typing import Dict, List, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

def log_water_intake(
    db: Session,
    user_id: int,
    amount_ml: float,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Log a water intake entry for the user
    """
    try:
        from models.database import WaterIntake
        
        entry = WaterIntake(
            user_id=user_id,
            amount_ml=amount_ml,
            timestamp=timestamp or datetime.now()
        )
        
        db.add(entry)
        db.commit()
        db.refresh(entry)
        
        return {
            "success": True,
            "message": "Water intake logged successfully",
            "entry_id": entry.id
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Error logging water intake: {str(e)}"
        }

def get_daily_water_intake(
    db: Session,
    user_id: int,
    target_date: Optional[date] = None
) -> Dict[str, Any]:
    """
    Get total water intake for a specific day
    """
    try:
        from models.database import WaterIntake
        
        target_date = target_date or date.today()
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = datetime.combine(target_date, datetime.max.time())
        
        entries = (
            db.query(WaterIntake)
            .filter(
                WaterIntake.user_id == user_id,
                WaterIntake.timestamp >= start_datetime,
                WaterIntake.timestamp <= end_datetime
            )
            .all()
        )
        
        total_intake = sum(entry.amount_ml for entry in entries)
        
        return {
            "date": target_date.strftime("%Y-%m-%d"),
            "total_intake_ml": total_intake,
            "total_intake_oz": round(total_intake * 0.033814, 1),
            "entries": len(entries),
            "entries_details": [
                {
                    "id": entry.id,
                    "amount_ml": entry.amount_ml,
                    "timestamp": entry.timestamp
                }
                for entry in entries
            ]
        }
        
    except Exception as e:
        print(f"Error getting water intake: {str(e)}")
        return {
            "date": target_date.strftime("%Y-%m-%d") if target_date else date.today().strftime("%Y-%m-%d"),
            "total_intake_ml": 0,
            "total_intake_oz": 0,
            "entries": 0,
            "entries_details": []
        }

def get_weekly_water_intake(
    db: Session,
    user_id: int,
    end_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """
    Get water intake data for the past 7 days
    """
    end_date = end_date or date.today()
    start_date = end_date - timedelta(days=6)  # Get 7 days including today
    
    results = []
    current_date = start_date
    
    while current_date <= end_date:
        daily_data = get_daily_water_intake(db, user_id, current_date)
        results.append(daily_data)
        current_date += timedelta(days=1)
        
    return results

def calculate_water_recommendation(
    weight_kg: float,
    activity_level: str,
    workout_duration_mins: int = 0,
    climate: str = "moderate"
) -> Dict[str, Any]:
    """
    Calculate recommended daily water intake based on weight, activity and climate
    """
    # Base recommendation: ~30-35ml per kg of body weight
    base_recommendation = weight_kg * 33
    
    # Activity level adjustments
    activity_factors = {
        "sedentary": 1.0,
        "light": 1.1,
        "moderate": 1.2,
        "high": 1.3,
        "very high": 1.4
    }
    
    # Climate adjustments
    climate_factors = {
        "cold": 0.95,
        "moderate": 1.0,
        "hot": 1.1,
        "very hot": 1.2
    }
    
    # Calculate additional needs for workout
    workout_addition = 0
    if workout_duration_mins > 0:
        # Add approximately 500-600ml per hour of exercise
        workout_addition = (workout_duration_mins / 60) * 550
    
    # Calculate total recommendation
    total_ml = (
        base_recommendation *
        activity_factors.get(activity_level.lower(), 1.0) *
        climate_factors.get(climate.lower(), 1.0)
    ) + workout_addition
    
    return {
        "daily_recommendation_ml": round(total_ml),
        "daily_recommendation_oz": round(total_ml * 0.033814, 1),
        "hourly_target_ml": round(total_ml / 16),  # Assuming 16 waking hours
        "workout_additional_ml": round(workout_addition)
    }
