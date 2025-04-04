from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

def calculate_recovery_score(
    workout_intensity: str,
    training_volume: int,
    exercise_types: List[str],
    user_metrics: Dict[str, Any]
) -> float:
    """Calculate recovery score based on workout and user metrics"""
    base_score = 100.0
    
    # Intensity impact
    intensity_factors = {
        "light": 0.8,
        "moderate": 0.6,
        "high": 0.4,
        "very high": 0.3
    }
    
    # Volume impact (number of exercises)
    volume_impact = max(0.3, 1 - (training_volume * 0.05))
    
    # Exercise type impact
    exercise_impacts = {
        "compound": 0.4,
        "isolation": 0.7,
        "bodyweight": 0.8,
        "cardio": 0.85
    }
    
    # Calculate average exercise impact
    exercise_score = sum(exercise_impacts.get(ex_type, 0.6) for ex_type in exercise_types) / len(exercise_types)
    
    # Apply all factors
    recovery_score = base_score * intensity_factors.get(workout_intensity.lower(), 0.6) * volume_impact * exercise_score
    
    # Adjust for user metrics
    if user_metrics.get("sleep_hours", 8) < 7:
        recovery_score *= 0.8
    if user_metrics.get("stress_level", "low").lower() == "high":
        recovery_score *= 0.85
    if user_metrics.get("nutrition_status", "good").lower() == "poor":
        recovery_score *= 0.9
        
    return round(recovery_score, 1)

def generate_recovery_recommendations(
    workout_data: Dict[str, Any],
    user_metrics: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate personalized recovery recommendations"""
    
    # Calculate recovery score
    recovery_score = calculate_recovery_score(
        workout_data.get("intensity", "moderate"),
        len(workout_data.get("exercises", [])),
        workout_data.get("exercise_types", ["compound"]),
        user_metrics
    )
    
    # Base recommendations
    recommendations = {
        "recovery_score": recovery_score,
        "recommended_rest_days": 1,
        "nutrition_tips": [],
        "recovery_activities": [],
        "sleep_recommendations": {},
        "next_workout_date": None
    }
    
    # Adjust recommendations based on recovery score
    if recovery_score < 50:
        recommendations["recommended_rest_days"] = 2
        recommendations["nutrition_tips"] = [
            "Increase protein intake to 2g per kg body weight",
            "Focus on anti-inflammatory foods",
            "Stay well hydrated (3-4 liters of water)",
            "Consider BCAAs supplementation"
        ]
        recommendations["recovery_activities"] = [
            "Light stretching",
            "Foam rolling",
            "10-15 minutes of light walking",
            "Cold therapy (ice bath or cold shower)"
        ]
        recommendations["sleep_recommendations"] = {
            "minimum_hours": 8,
            "optimal_hours": 9,
            "tips": [
                "Avoid screens 1 hour before bed",
                "Keep room temperature cool",
                "Use blackout curtains",
                "Consider magnesium supplementation"
            ]
        }
    elif recovery_score < 75:
        recommendations["recommended_rest_days"] = 1
        recommendations["nutrition_tips"] = [
            "Maintain regular protein intake (1.6-1.8g per kg)",
            "Focus on complex carbohydrates",
            "Stay hydrated (2-3 liters of water)"
        ]
        recommendations["recovery_activities"] = [
            "Dynamic stretching",
            "Light mobility work",
            "20-30 minutes of walking",
            "Self-massage techniques"
        ]
        recommendations["sleep_recommendations"] = {
            "minimum_hours": 7,
            "optimal_hours": 8,
            "tips": [
                "Maintain regular sleep schedule",
                "Practice relaxation techniques",
                "Ensure dark, quiet sleeping environment"
            ]
        }
    else:
        recommendations["recommended_rest_days"] = 0
        recommendations["nutrition_tips"] = [
            "Maintain balanced diet",
            "Regular hydration",
            "Consider pre-workout nutrition"
        ]
        recommendations["recovery_activities"] = [
            "Dynamic warm-up",
            "Basic mobility work",
            "Light cardio if desired"
        ]
        recommendations["sleep_recommendations"] = {
            "minimum_hours": 7,
            "optimal_hours": 8,
            "tips": [
                "Maintain regular sleep schedule",
                "Stay hydrated throughout the day"
            ]
        }
    
    # Calculate next workout date
    next_workout_date = datetime.now() + timedelta(days=recommendations["recommended_rest_days"])
    recommendations["next_workout_date"] = next_workout_date.strftime("%Y-%m-%d")
    
    return recommendations

def get_workout_intensity(exercises: List[str], fitness_level: str) -> str:
    """Determine workout intensity based on exercises and fitness level"""
    compound_movements = [
        "Squat", "Deadlift", "Bench Press", "Pull-up", "Clean", "Snatch",
        "Press", "Row", "Lunge"
    ]
    
    # Count compound movements
    compound_count = sum(1 for ex in exercises if any(move in ex for move in compound_movements))
    
    # Calculate intensity based on compound movements and fitness level
    if fitness_level.lower() == "beginner":
        if compound_count >= 3:
            return "high"
        elif compound_count >= 2:
            return "moderate"
        return "light"
    elif fitness_level.lower() == "intermediate":
        if compound_count >= 4:
            return "very high"
        elif compound_count >= 2:
            return "high"
        return "moderate"
    else:  # Advanced
        if compound_count >= 3:
            return "very high"
        elif compound_count >= 2:
            return "high"
        return "moderate"
