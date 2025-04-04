import trafilatura
from typing import List, Dict, Any, Optional
import re

def scrape_muscleandstrength_exercises(muscle_group: str) -> List[Dict[str, Any]]:
    """
    Scrape exercises from muscleandstrength.com for a specific muscle group
    """
    base_urls = {
        "Chest": "https://www.muscleandstrength.com/exercises/chest",
        "Back": "https://www.muscleandstrength.com/exercises/back",
        "Legs": "https://www.muscleandstrength.com/exercises/legs",
        "Shoulders": "https://www.muscleandstrength.com/exercises/shoulders",
        "Biceps": "https://www.muscleandstrength.com/exercises/biceps",
        "Triceps": "https://www.muscleandstrength.com/exercises/triceps",
        "Core": "https://www.muscleandstrength.com/exercises/abs",
        "Forearms": "https://www.muscleandstrength.com/exercises/forearms"
    }
    
    if muscle_group not in base_urls:
        return []
        
    try:
        url = base_urls[muscle_group]
        print(f"Scraping exercises for {muscle_group} from {url}")
        
        # Download and extract content
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return []
            
        text = trafilatura.extract(downloaded)
        if not text:
            return []
            
        # Extract exercise information using regex patterns
        exercise_pattern = r"(\d+\.\s*)([\w\s\-]+)(?:\n|$)"
        exercises = re.findall(exercise_pattern, text)
        
        # Process and categorize exercises
        processed_exercises = []
        for _, exercise_name in exercises:
            exercise_name = exercise_name.strip()
            if exercise_name:
                # Categorize based on equipment needed
                equipment_category = categorize_exercise(exercise_name)
                
                processed_exercises.append({
                    "name": exercise_name,
                    "equipment": equipment_category,
                    "muscle_group": muscle_group
                })
        
        print(f"Found {len(processed_exercises)} exercises for {muscle_group}")
        return processed_exercises
        
    except Exception as e:
        print(f"Error scraping exercises for {muscle_group}: {str(e)}")
        return []

def categorize_exercise(exercise_name: str) -> str:
    """
    Categorize exercise based on its name to determine equipment needed
    """
    exercise_lower = exercise_name.lower()
    
    # Equipment keywords
    if any(keyword in exercise_lower for keyword in ["machine", "cable", "smith", "hack"]):
        return "Full Gym Access"
    elif any(keyword in exercise_lower for keyword in ["dumbbell", "db"]):
        return "Dumbbells"
    else:
        return "None/Bodyweight"

def get_exercise_difficulty(exercise_name: str) -> str:
    """
    Determine exercise difficulty based on keywords
    """
    exercise_lower = exercise_name.lower()
    
    # Advanced keywords
    if any(keyword in exercise_lower for keyword in ["weighted", "advanced", "complex", "one-arm", "planche"]):
        return "Advanced"
    # Beginner keywords
    elif any(keyword in exercise_lower for keyword in ["basic", "assisted", "beginner", "modified"]):
        return "Beginner"
    else:
        return "Intermediate"
