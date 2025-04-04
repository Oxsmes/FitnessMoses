from typing import Dict, List, Any, Optional
from data.food_database import meal_suggestions

def get_alternative_meals(
    meal_type: str,
    target_calories: float,
    target_protein: float,
    dietary_restrictions: List[str],
    cuisine_preferences: List[str],
    current_meal_name: str,
    num_alternatives: int = 3
) -> List[Dict[str, Any]]:
    """
    Get alternative meal suggestions based on user preferences and nutritional targets
    """
    print(f"Searching alternatives for {meal_type}, current meal: {current_meal_name}")  # Debug log
    print(f"Available meals for {meal_type}: {len(meal_suggestions[meal_type])}")  # Debug log

    suitable_alternatives = [
        meal for meal in meal_suggestions[meal_type]
        if meal['name'] != current_meal_name
        and (all(r not in meal['restrictions'] for r in dietary_restrictions) or "None" in dietary_restrictions)
        and (any(c in meal['cuisine'] for c in cuisine_preferences) or "Any" in cuisine_preferences)
        and abs(meal['calories'] - target_calories) < 200
        and abs(meal['protein'] - target_protein) < 15
    ]

    print(f"Found {len(suitable_alternatives)} suitable alternatives")  # Debug log
    return suitable_alternatives[:num_alternatives]

def validate_meal_plan(
    meal_plan: Dict[str, Dict[str, Dict[str, Any]]],
    target_daily_calories: float,
    target_daily_protein: float
) -> Dict[str, Any]:
    """
    Validate the customized meal plan meets nutritional targets
    """
    total_daily_calories = 0
    total_daily_protein = 0

    # Calculate average daily nutrition
    for day, meals in meal_plan.items():
        day_calories = sum(meal['calories'] for meal in meals.values())
        day_protein = sum(meal['protein'] for meal in meals.values())
        total_daily_calories += day_calories
        total_daily_protein += day_protein

    avg_daily_calories = total_daily_calories / len(meal_plan)
    avg_daily_protein = total_daily_protein / len(meal_plan)

    return {
        'meets_targets': (
            abs(avg_daily_calories - target_daily_calories) < 300 and
            abs(avg_daily_protein - target_daily_protein) < 20
        ),
        'avg_daily_calories': avg_daily_calories,
        'avg_daily_protein': avg_daily_protein,
        'calories_difference': avg_daily_calories - target_daily_calories,
        'protein_difference': avg_daily_protein - target_daily_protein
    }