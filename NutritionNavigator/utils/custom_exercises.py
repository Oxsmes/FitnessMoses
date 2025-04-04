
from typing import Dict, List, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from models.database import User

def add_custom_exercise(
    db: Session,
    user_id: int,
    exercise_name: str,
    muscle_group: str,
    equipment_needed: str,
    difficulty: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add a custom exercise to the user's personal exercise library
    """
    try:
        from models.database import CustomExercise
        
        # Check if exercise already exists for this user
        existing = (
            db.query(CustomExercise)
            .filter(
                CustomExercise.user_id == user_id,
                CustomExercise.name == exercise_name
            )
            .first()
        )
        
        if existing:
            return {
                "success": False,
                "message": "An exercise with this name already exists in your library"
            }
            
        # Create new custom exercise
        new_exercise = CustomExercise(
            user_id=user_id,
            name=exercise_name,
            muscle_group=muscle_group,
            equipment=equipment_needed,
            difficulty=difficulty,
            description=description,
            created_at=datetime.now()
        )
        
        db.add(new_exercise)
        db.commit()
        db.refresh(new_exercise)
        
        return {
            "success": True,
            "message": "Exercise added successfully",
            "exercise_id": new_exercise.id
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Error adding custom exercise: {str(e)}"
        }

def get_user_custom_exercises(
    db: Session,
    user_id: int,
    muscle_group: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get all custom exercises for a user, optionally filtered by muscle group
    """
    try:
        from models.database import CustomExercise
        
        query = db.query(CustomExercise).filter(CustomExercise.user_id == user_id)
        
        if muscle_group:
            query = query.filter(CustomExercise.muscle_group == muscle_group)
            
        exercises = query.order_by(CustomExercise.name).all()
        
        return [
            {
                "id": ex.id,
                "name": ex.name,
                "muscle_group": ex.muscle_group,
                "equipment": ex.equipment,
                "difficulty": ex.difficulty,
                "description": ex.description,
                "created_at": ex.created_at
            }
            for ex in exercises
        ]
        
    except Exception as e:
        print(f"Error retrieving custom exercises: {str(e)}")
        return []

def delete_custom_exercise(
    db: Session,
    user_id: int,
    exercise_id: int
) -> Dict[str, Any]:
    """
    Delete a custom exercise from the user's library
    """
    try:
        from models.database import CustomExercise
        
        exercise = (
            db.query(CustomExercise)
            .filter(
                CustomExercise.id == exercise_id,
                CustomExercise.user_id == user_id
            )
            .first()
        )
        
        if not exercise:
            return {
                "success": False,
                "message": "Exercise not found or you don't have permission to delete it"
            }
            
        db.delete(exercise)
        db.commit()
        
        return {
            "success": True,
            "message": "Exercise deleted successfully"
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"Error deleting custom exercise: {str(e)}"
        }

def format_custom_exercise_for_workout(
    exercise: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Format a custom exercise to be compatible with the workout planner
    """
    return {
        "name": exercise["name"],
        "equipment": exercise["equipment"],
        "muscle_group": exercise["muscle_group"],
        "is_custom": True,
        "custom_id": exercise["id"]
    }

def integrate_custom_exercises_with_library(
    standard_library: Dict[str, Any],
    custom_exercises: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Integrate custom exercises into the standard exercise library format
    """
    enhanced_library = standard_library.copy()
    
    # Group custom exercises by muscle group
    for exercise in custom_exercises:
        muscle_group = exercise["muscle_group"]
        if muscle_group not in enhanced_library:
            # Create the muscle group if it doesn't exist
            enhanced_library[muscle_group] = {}
            
        # Use "Custom" as the subgroup for all custom exercises
        if "Custom" not in enhanced_library[muscle_group]:
            enhanced_library[muscle_group]["Custom"] = {
                "Beginner": {},
                "Intermediate": {},
                "Advanced": {}
            }
            
        # Add to the appropriate difficulty level
        difficulty = exercise["difficulty"]
        equipment = exercise["equipment"]
        
        if equipment not in enhanced_library[muscle_group]["Custom"][difficulty]:
            enhanced_library[muscle_group]["Custom"][difficulty][equipment] = []
            
        enhanced_library[muscle_group]["Custom"][difficulty][equipment].append(
            exercise["name"]
        )
    
    return enhanced_library
