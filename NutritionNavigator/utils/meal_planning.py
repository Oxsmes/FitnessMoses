from data.food_database import meal_suggestions
from utils.recipe_scraper import get_online_recipes
import random
from typing import Dict, List, Any

def generate_meal_plan(target_calories, protein_needs, dietary_restrictions, cuisine_preferences):
    """
    Generate a weekly meal plan based on nutritional needs and preferences
    """
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    meal_plan = {}

    # Calculate target macros per meal
    daily_calories = target_calories
    daily_protein = protein_needs

    calories_per_meal = {
        'Breakfast': daily_calories * 0.25,
        'Lunch': daily_calories * 0.35,
        'Dinner': daily_calories * 0.40
    }

    protein_per_meal = {
        'Breakfast': daily_protein * 0.25,
        'Lunch': daily_protein * 0.35,
        'Dinner': daily_protein * 0.40
    }

    for day in days:
        meal_plan[day] = {}
        for meal_type in ['Breakfast', 'Lunch', 'Dinner']:
            # Get online recipes
            online_recipes = get_online_recipes(
                calories_per_meal[meal_type],
                protein_per_meal[meal_type],
                meal_type
            )

            # Combine with database recipes
            all_meals = meal_suggestions[meal_type] + online_recipes

            # Filter meals based on restrictions and preferences
            suitable_meals = [
                meal for meal in all_meals
                if (all(r not in meal['restrictions'] for r in dietary_restrictions) or "None" in dietary_restrictions)
                and (any(c in meal['cuisine'] for c in cuisine_preferences) or "Any" in cuisine_preferences)
                and abs(meal['calories'] - calories_per_meal[meal_type]) < 200
                and abs(meal['protein'] - protein_per_meal[meal_type]) < 15
            ]

            if suitable_meals:
                meal_plan[day][meal_type] = random.choice(suitable_meals)
            else:
                # Fallback to any meal if no suitable matches found
                meal_plan[day][meal_type] = random.choice(meal_suggestions[meal_type])

    return meal_plan