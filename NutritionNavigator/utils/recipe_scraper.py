import trafilatura
from typing import List, Dict, Any, Optional
import re
import json
from datetime import datetime

def extract_nutritional_info(text: str) -> Dict[str, float]:
    """Extract calories and protein information from recipe text"""
    calories = 0
    protein = 0
    
    # Look for common patterns of nutritional information
    calories_patterns = [
        r'(\d+)\s*calories',
        r'calories:\s*(\d+)',
        r'energy:\s*(\d+)\s*kcal'
    ]
    
    protein_patterns = [
        r'(\d+)g?\s*protein',
        r'protein:\s*(\d+)g?',
        r'protein\s*(\d+)g?'
    ]
    
    for pattern in calories_patterns:
        match = re.search(pattern, text.lower())
        if match:
            try:
                calories = float(match.group(1))
                break
            except ValueError:
                continue
    
    for pattern in protein_patterns:
        match = re.search(pattern, text.lower())
        if match:
            try:
                protein = float(match.group(1))
                break
            except ValueError:
                continue
    
    return {
        'calories': calories,
        'protein': protein
    }

def scrape_recipe(url: str) -> Optional[Dict[str, Any]]:
    """Scrape recipe information from a given URL"""
    try:
        # Download and extract content
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None
            
        text = trafilatura.extract(downloaded)
        if not text:
            return None
        
        # Extract title (first line is usually the title)
        title = text.split('\n')[0].strip()
        
        # Extract nutritional information
        nutrition = extract_nutritional_info(text)
        
        # Create recipe object
        recipe = {
            'name': title,
            'calories': nutrition['calories'],
            'protein': nutrition['protein'],
            'restrictions': [],  # Would need more sophisticated analysis
            'cuisine': ["Any"],  # Would need more sophisticated analysis
            'link': url,
            'scraped_date': datetime.now().strftime("%Y-%m-%d")
        }
        
        return recipe if recipe['calories'] > 0 else None
        
    except Exception as e:
        print(f"Error scraping recipe from {url}: {str(e)}")
        return None

def get_online_recipes(
    target_calories: float,
    target_protein: float,
    meal_type: str,
    num_recipes: int = 3
) -> List[Dict[str, Any]]:
    """Get recipes from predefined healthy recipe websites"""
    recipe_urls = {
        "Breakfast": [
            "https://www.eatingwell.com/recipe/269947/greek-yogurt-parfait",
            "https://www.foodnetwork.com/recipes/food-network-kitchen/healthy-breakfast-sandwich",
            "https://www.allrecipes.com/recipe/21014/good-old-fashioned-pancakes"
        ],
        "Lunch": [
            "https://www.eatingwell.com/recipe/250300/quinoa-chickpea-salad",
            "https://www.foodnetwork.com/recipes/food-network-kitchen/healthy-grilled-chicken-sandwich",
            "https://www.allrecipes.com/recipe/234331/healthy-quinoa-salad"
        ],
        "Dinner": [
            "https://www.eatingwell.com/recipe/262747/sheet-pan-chicken-fajitas",
            "https://www.foodnetwork.com/recipes/food-network-kitchen/healthy-grilled-salmon",
            "https://www.allrecipes.com/recipe/228823/healthy-vegetarian-chickpea-curry"
        ]
    }
    
    recipes = []
    for url in recipe_urls.get(meal_type, []):
        recipe = scrape_recipe(url)
        if recipe:
            recipes.append(recipe)
    
    return recipes[:num_recipes]
