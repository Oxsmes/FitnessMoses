import random
from typing import List, Dict, Any
from data.food_database import meal_suggestions

def get_recipe_recommendations(
    target_calories: float,
    target_protein: float,
    dietary_restrictions: List[str],
    cuisine_preferences: List[str],
    num_recommendations: int = 5
) -> List[Dict[str, Any]]:
    """
    Generate personalized recipe recommendations based on user preferences
    """
    all_meals = []
    for meal_type in meal_suggestions.values():
        all_meals.extend(meal_type)
    
    # Filter recipes based on restrictions and preferences
    suitable_recipes = [
        meal for meal in all_meals
        if (all(r not in meal['restrictions'] for r in dietary_restrictions) or "None" in dietary_restrictions)
        and (any(c in meal['cuisine'] for c in cuisine_preferences) or "Any" in cuisine_preferences)
        and abs(meal['calories'] - (target_calories / 3)) < 300  # Within 300 calories of target per meal
        and abs(meal['protein'] - (target_protein / 3)) < 20     # Within 20g protein of target per meal
    ]
    
    # Sort by how well they match the targets
    suitable_recipes.sort(key=lambda x: (
        abs(x['calories'] - (target_calories / 3)) +  # Lower difference is better
        abs(x['protein'] - (target_protein / 3))
    ))
    
    # Return top recommendations, randomized if we have more than requested
    if len(suitable_recipes) > num_recommendations:
        return random.sample(suitable_recipes[:int(num_recommendations * 1.5)], num_recommendations)
    return suitable_recipes[:num_recommendations]

def format_recipe_recommendation(recipe: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a recipe recommendation with relevant details
    """
    return {
        "name": recipe['name'],
        "calories": recipe['calories'],
        "protein": recipe['protein'],
        "cuisine_type": recipe['cuisine'][0] if recipe['cuisine'] != ["Any"] else "International",
        "dietary_info": "Suitable for all" if not recipe['restrictions'] else f"Not suitable for: {', '.join(recipe['restrictions'])}",
        "recipe_link": recipe['link']
    }
