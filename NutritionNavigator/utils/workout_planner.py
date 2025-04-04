import random
from typing import Dict, List, Any, Optional
from datetime import datetime

# Helper functions remain unchanged
def select_exercises_for_subgroup(
    subgroup_exercises: Dict[str, Dict[str, List[str]]],
    fitness_level: str,
    equipment: List[str],
    used_tracker: set,
    exercises_per_subgroup: int = 2
) -> List[str]:
    """Select exercises for a specific subgroup based on equipment and fitness level"""
    print(f"\nSelecting exercises for subgroup:")
    print(f"- Fitness level: {fitness_level}")
    print(f"- Equipment available: {equipment}")

    available_exercises = set()

    # Collect all available exercises for the equipment types
    for equip in equipment:
        if equip in subgroup_exercises[fitness_level]:
            exercises = subgroup_exercises[fitness_level][equip]
            if exercises:  # Check if exercises list is not empty
                available_exercises.update(exercises)
                print(f"Added {len(exercises)} exercises for {equip}")

    if not available_exercises:
        print("No exercises found for current equipment and fitness level")
        return []

    # Get unused exercises
    unused_exercises = available_exercises - used_tracker
    print(f"Available exercises: {len(available_exercises)}")
    print(f"Unused exercises: {len(unused_exercises)}")

    # Reset tracker if all exercises used
    if not unused_exercises:
        unused_exercises = available_exercises
        used_tracker.clear()
        print("Reset exercise tracker - all exercises were used")

    # Select random exercises
    selected = random.sample(
        list(unused_exercises),
        min(exercises_per_subgroup, len(unused_exercises))
    )
    print(f"Selected exercises: {selected}")

    # Update tracker
    used_tracker.update(selected)

    return selected

def get_muscle_group_exercises(
    fitness_level: str,
    muscle_group: str,
    equipment: List[str],
    exercise_library: Dict,
    used_exercises_tracker: Optional[Dict[str, set]] = None
) -> List[str]:
    """Get exercises for specific muscle groups and their subgroups"""
    print(f"\n=== Getting exercises for {muscle_group} ===")
    print(f"Fitness level: {fitness_level}")
    print(f"Equipment: {equipment}")

    # Initialize tracker if not provided
    if used_exercises_tracker is None:
        used_exercises_tracker = {}

    # Validate muscle group exists
    if muscle_group not in exercise_library:
        print(f"Error: Muscle group '{muscle_group}' not found in library")
        return []

    selected_exercises = []

    try:
        # Process each subgroup
        for subgroup, exercises_dict in exercise_library[muscle_group].items():
            print(f"\nProcessing subgroup: {subgroup}")

            # Initialize subgroup tracking
            tracker_key = f"{muscle_group}-{subgroup}"
            if tracker_key not in used_exercises_tracker:
                used_exercises_tracker[tracker_key] = set()
                print(f"Initialized tracking for {tracker_key}")

            # Select exercises for this subgroup
            if fitness_level in exercises_dict:
                subgroup_selections = select_exercises_for_subgroup(
                    exercises_dict,
                    fitness_level,
                    equipment,
                    used_exercises_tracker[tracker_key]
                )

                if subgroup_selections:
                    # Add subgroup prefix to exercises
                    prefixed_exercises = [f"{subgroup}: {ex}" for ex in subgroup_selections]
                    selected_exercises.extend(prefixed_exercises)
                    print(f"Added {len(prefixed_exercises)} exercises for {subgroup}:")
                    for ex in prefixed_exercises:
                        print(f"  - {ex}")
                else:
                    print(f"No suitable exercises found for {subgroup} at {fitness_level} level")

        if not selected_exercises:
            print(f"Warning: No exercises found for {muscle_group} with current settings")
            # Try to get exercises from a different fitness level as fallback
            alternate_level = "Intermediate" if fitness_level != "Intermediate" else "Beginner"
            print(f"Attempting to find exercises at {alternate_level} level...")

            for subgroup, exercises_dict in exercise_library[muscle_group].items():
                if alternate_level in exercises_dict:
                    fallback_selections = select_exercises_for_subgroup(
                        exercises_dict,
                        alternate_level,
                        equipment,
                        used_exercises_tracker.get(f"{muscle_group}-{subgroup}", set())
                    )
                    if fallback_selections:
                        prefixed_exercises = [f"{subgroup} ({alternate_level}): {ex}" for ex in fallback_selections]
                        selected_exercises.extend(prefixed_exercises)
                        print(f"Found fallback exercises at {alternate_level} level")

        return selected_exercises

    except Exception as e:
        print(f"Error selecting exercises for {muscle_group}: {str(e)}")
        return []

def generate_workout_plan(
    fitness_level: str,
    goals: List[str],
    available_days: List[str],
    equipment_available: List[str],
    time_per_session: int,
    muscle_groups: Dict[str, List[str]],
    exercise_library: Dict
) -> Dict[str, Any]:
    """Generate a personalized workout schedule"""
    print("\n=== Starting New Workout Generation ===")
    print("Input parameters:")
    print(f"- Fitness level: {fitness_level}")
    print(f"- Goals: {goals}")
    print(f"- Available days: {available_days}")
    print(f"- Equipment: {equipment_available}")
    print(f"- Time per session: {time_per_session}")
    print(f"- Muscle groups: {muscle_groups}")

    try:
        # Validate inputs
        if not available_days:
            print("Error: No available days provided")
            return {}

        if not muscle_groups:
            print("Error: No muscle groups provided")
            return {}

        if not equipment_available:
            print("Error: No equipment selected")
            return {}

        # Initialize schedule and tracker
        schedule = {}
        used_exercises_tracker = {}

        # Generate workout for each day
        for day in available_days:
            print(f"\nProcessing workout for {day}")

            if day not in muscle_groups:
                print(f"Error: No muscle groups defined for {day}")
                continue

            day_muscles = muscle_groups[day]
            if not day_muscles:
                print(f"Error: Empty muscle group list for {day}")
                continue

            print(f"Selected muscles: {day_muscles}")

            # Handle rest days
            if "Rest" in day_muscles:
                schedule[day] = {
                    "focus": "Rest Day",
                    "duration": 0,
                    "exercises": ["Rest and Recovery"]
                }
                print(f"Added rest day for {day}")
                continue

            # Get exercises for each muscle group
            day_exercises = []
            for muscle in day_muscles:
                muscle_exercises = get_muscle_group_exercises(
                    fitness_level=fitness_level,
                    muscle_group=muscle,
                    equipment=equipment_available,
                    exercise_library=exercise_library,
                    used_exercises_tracker=used_exercises_tracker
                )

                if muscle_exercises:
                    day_exercises.extend(muscle_exercises)
                    print(f"Added {len(muscle_exercises)} exercises for {muscle}")

            # Add day to schedule
            if day_exercises:
                schedule[day] = {
                    "focus": ", ".join(day_muscles),
                    "duration": time_per_session,
                    "exercises": day_exercises
                }
                print(f"Complete workout for {day}:")
                for ex in day_exercises:
                    print(f"  - {ex}")
            else:
                print(f"Warning: No exercises found for {day}")

        if not schedule:
            print("Error: Failed to generate any workouts")
            return {}

        return schedule

    except Exception as e:
        print(f"Error generating workout plan: {str(e)}")
        return {}

def save_workout_schedule(
    db,
    user_id: int,
    schedule: Dict[str, Any],
    preferences: Dict[str, Any],
    is_custom: bool = False
) -> bool:
    """Save workout schedule to database"""
    try:
        from models.database import WorkoutSchedule

        new_schedule = WorkoutSchedule(
            user_id=user_id,
            schedule=schedule,
            preferences=preferences,
            is_custom=is_custom,
            date=datetime.now().date()
        )

        db.add(new_schedule)
        db.commit()
        print("Successfully saved workout schedule")
        return True

    except Exception as e:
        print(f"Error saving schedule: {str(e)}")
        db.rollback()
        return False

def get_latest_workout_schedule(
    db,
    user_id: int
) -> Optional[Dict[str, Any]]:
    """Get user's most recent workout schedule"""
    try:
        from models.database import WorkoutSchedule

        schedule = (
            db.query(WorkoutSchedule)
            .filter(WorkoutSchedule.user_id == user_id)
            .order_by(WorkoutSchedule.date.desc())
            .first()
        )

        if schedule:
            return {
                "schedule": schedule.schedule,
                "preferences": schedule.preferences,
                "is_custom": schedule.is_custom,
                "date": schedule.date
            }

        return None

    except Exception as e:
        print(f"Error getting schedule: {str(e)}")
        return None

# Exercise library TypedDict definition
ExerciseLibrary = Dict[str, Dict[str, Dict[str, Dict[str, List[str]]]]]

# Exercise library definition
exercise_library: ExerciseLibrary = {
    "Chest": {
        "Upper Chest": {
            "Beginner": {
                "None/Bodyweight": [
                    "Incline Push-ups",
                    "Pike Push-ups",
                    "Decline Diamond Push-ups",
                    "Wall Push-ups (elevated)",
                    "Elevated Push-ups (feet raised)",
                    "Band-Resisted Incline Push-ups",
                    "Isometric Chest Holds (upper)",
                    "Half-Range Incline Push-ups"
                ],
                "Dumbbells": [
                    "Incline Dumbbell Press",
                    "Incline Dumbbell Flyes",
                    "High-Incline Press",
                    "Upper Chest Pullovers",
                    "Single-Arm Incline Press",
                    "Alternating Incline Press",
                    "Incline Hammer Press",
                    "Stability Ball Incline Press"
                ],
                "Full Gym Access": [
                    "Incline Bench Press",
                    "Low-to-High Cable Flyes",
                    "Smith Machine Incline Press",
                    "Reverse Grip Bench Press",
                    "Incline Machine Press",
                    "30-Degree Incline Press",
                    "Incline Plate Press",
                    "Upper Chest Cable Press"
                ]
            },
            "Intermediate": {
                "None/Bodyweight": [
                    "Weighted Incline Push-ups",
                    "Pseudo Planche Push-ups",
                    "Archer Push-ups (incline)",
                    "Diamond Push-ups (incline)",
                    "Resistance Band Crossovers",
                    "One-Arm Push-up Progression",
                    "Plyometric Incline Push-ups",
                    "TRX Incline Press"
                ],
                "Dumbbells": [
                    "Heavy Incline Dumbbell Press",
                    "Heavy Incline Flyes",
                    "Alternating Incline Press",
                    "Single-Arm Incline Press",
                    "Incline Twist Press",
                    "Stability Ball Flyes",
                    "Incline Arnold Press",
                    "Incline Cross-Body Press"
                ],
                "Full Gym Access": [
                    "Heavy Incline Bench Press",
                    "Incline Dumbbell Press",
                    "Hammer Strength Incline",
                    "Cable Upper Chest Flyes",
                    "Multi-Angle Incline Press",
                    "Incline Pin Press",
                    "Upper Chest Specialization",
                    "Incline Smith Machine Press"
                ]
            },
            "Advanced": {
                "None/Bodyweight": [
                    "Planche Push-up Progressions",
                    "One-Arm Incline Push-ups",
                    "Explosive Incline Push-ups",
                    "Handstand Push-ups",
                    "Ring Fly Progressions",
                    "Weighted Vest Push-ups",
                    "Deficit Push-ups (elevated)",
                    "Complex Push-up Series"
                ],
                "Dumbbells": [
                    "Complex Incline Press Sets",
                    "Drop Set Incline Flyes",
                    "Tempo Incline Press",
                    "Plyometric Incline Press",
                    "Mechanical Advantage Drop Sets",
                    "Pause Reps at Different Angles",
                    "Alternating Power Press",
                    "Pre-Exhaust Supersets"
                ],
                "Full Gym Access": [
                    "Weighted Dips (lean forward)",
                    "Pause Rep Incline Press",
                    "Incline Bench Drop Sets",
                    "Resistance Band Press",
                    "Chain-Loaded Incline Press",
                    "Partial Rep Specialization",
                    "1.5 Rep Technique",
                    "Multi-Angle Strength Work"
                ]
            }
        }
    },
    "Back": {
        "Lats": {
            "Beginner": {
                "None/Bodyweight": [
                    "Inverted Rows (horizontal)",
                    "Negative Pull-ups (slow descent)",
                    "Band-Assisted Pull-ups",
                    "Dead Hangs (active grip)",
                    "Scapular Pull-ups",
                    "Australian Pull-ups",
                    "Resistance Band Straight-Arm Pulldowns",
                    "Active Hang to Arch Hangs"
                ],
                "Dumbbells": [
                    "Single-Arm Rows (supported)",
                    "Bent Over Rows (neutral grip)",
                    "Renegade Rows",
                    "Two-Point Rows",
                    "Meadows Rows",
                    "Chest-Supported DB Rows",
                    "Standing Lat Pushdowns",
                    "DB Pullovers"
                ],
                "Full Gym Access": [
                    "Lat Pulldowns (wide grip)",
                    "Seated Cable Rows",
                    "Machine Rows",
                    "Straight Arm Pulldowns",
                    "Assisted Pull-up Machine",
                    "Low Cable Rows",
                    "Single-Arm Lat Pulldowns",
                    "Guided Row Machine"
                ]
            }
        }
    },
    "Shoulders": {
        "Anterior Deltoids": {
            "Beginner": {
                "None/Bodyweight": [
                    "Pike Push-ups (wall-supported)",
                    "Wall Handstand Holds (30s)",
                    "Incline Push-ups (shoulder focus)",
                    "Band Front Raises",
                    "Resistance Band Press",
                    "Arm Circles (forward/backward)",
                    "Wall Slides with Band",
                    "Scapular Push-ups"
                ],
                "Dumbbells": [
                    "Standing Front Raises",
                    "Seated Arnold Press",
                    "Single-Arm Press",
                    "Alternating Front Raises",
                    "Half-Kneeling Press",
                    "Landmine Press (single DB)",
                    "Neutral Grip Press",
                    "Z-Press"
                ],
                "Full Gym Access": [
                    "Military Press (light)",
                    "Smith Machine Press",
                    "Cable Front Raises",
                    "Machine Shoulder Press",
                    "High Cable Front Raises",
                    "Plate Front Raises",
                    "Landmine Press",
                    "Face-Pull to Press"
                ]
            }
        }
    },
    "Arms": {
        "Biceps": {
            "Beginner": {
                "None/Bodyweight": [
                    "Resistance Band Curls",
                    "Isometric Chin Hold",
                    "Negative Chin-ups",
                    "Band-assisted Chin-ups",
                    "TRX Curls",
                    "Inverted Rows (supinated)",
                    "Door Frame Curls",
                    "Towel Curls"
                ],
                "Dumbbells": [
                    "Standing Bicep Curls",
                    "Hammer Curls",
                    "Alternating Curls",
                    "Incline Bench Curls",
                    "Concentration Curls",
                    "Cross-Body Curls",
                    "Seated Curls",
                    "Waiter Curls"
                ],
                "Full Gym Access": [
                    "EZ Bar Curls",
                    "Cable Curls",
                    "Preacher Curls",
                    "Machine Curls",
                    "Low Cable Curls",
                    "High Cable Curls",
                    "Incline Cable Curls",
                    "Rope Curls"
                ]
            },
            "Intermediate": {
                "None/Bodyweight": [
                    "Weighted Chin-ups",
                    "Eccentric Chin-ups",
                    "Ring Curls",
                    "Advanced Band Work",
                    "Isometric Hold Series",
                    "Dynamic Tension",
                    "Movement Flow",
                    "Control Series"
                ],
                "Dumbbells": [
                    "Heavy Curl Complex",
                    "Drop Set Protocol",
                    "21s Series",
                    "Tempo Training",
                    "Mechanical Advantage",
                    "Power Development",
                    "Time Under Tension",
                    "Integration Work"
                ],
                "Full Gym Access": [
                    "Barbell Curl Series",
                    "Cable Complex",
                    "Advanced Preacher",
                    "Machine Drop Sets",
                    "Super Set Protocol",
                    "Giant Set Series",
                    "Power Training",
                    "Integration Focus"
                ]
            },
            "Advanced": {
                "None/Bodyweight": [
                    "One-Arm Chin-up",
                    "Advanced Ring Work",
                    "Complex Movement",
                    "Power Protocol",
                    "Stability Challenge",
                    "Dynamic Control",
                    "Flow Sequence",
                    "Movement Mastery"
                ],
                "Dumbbells": [
                    "Heavy Complex Work",
                    "Power Development",
                    "Drop Set Series",
                    "Time Under Tension",
                    "Mechanical Advantage",
                    "Pre-Exhaust Protocol",
                    "Giant Sets",
                    "Advanced Techniques"
                ],
                "Full Gym Access": [
                    "Advanced Cable Work",
                    "Machine Intensity",
                    "Power Protocol",
                    "Drop Set Series",
                    "Super Set Work",
                    "Movement Integration",
                    "Time Under Tension",
                    "Peak Contraction"
                ]
            }
        },
        "Triceps": {
            "Beginner": {
                "None/Bodyweight": [
                    "Diamond Push-ups",
                    "Bench Dips",
                    "Close Push-ups",
                    "Band Pushdowns",
                    "Band Overhead Extension",
                    "Floor Triceps Extensions",
                    "Wall Push-ups (close)",
                    "Triceps Stretch Series"
                ],
                "Dumbbells": [
                    "Overhead Extensions",
                    "Lying Triceps Press",
                    "Kickbacks",
                    "Close-Grip Press",
                    "Single-Arm Extension",
                    "Floor Skull Crushers",
                    "Two-Hand Press",
                    "Standing Press"
                ],
                "Full Gym Access": [
                    "Rope Pushdowns",
                    "Cable Overhead Extension",
                    "Machine Press",
                    "Close-Grip Bench",
                    "V-Bar Pushdown",
                    "Single-Arm Cable",
                    "Machine Dips",
                    "EZ Bar Extension"
                ]
            },
            "Intermediate": {
                "None/Bodyweight": [
                    "Weighted Dips",
                    "Ring Extensions",
                    "Advanced Push-ups",
                    "Band Complex",
                    "Isometric Series",
                    "Movement Flow",
                    "Control Work",
                    "Power Training"
                ],
                "Dumbbells": [
                    "Heavy Extension Series",
                    "Drop Set Protocol",
                    "Tempo Training",
                    "Power Development",
                    "Complex Movement",
                    "Time Under Tension",
                    "Integration Work",
                    "Control Focus"
                ],
                "Full Gym Access": [
                    "Cable Complex",
                    "Machine Drop Sets",
                    "Super Set Protocol",
                    "Giant Set Series",
                    "Power Training",
                    "Movement Pattern",
                    "Time Under Tension",
                    "Integration Focus"
                ]
            },
            "Advanced": {
                "None/Bodyweight": [
                    "Ring Mastery",
                    "Advanced Calisthenics",
                    "Complex Movement",
                    "Power Protocol",
                    "Stability Challenge",
                    "Dynamic Control",
                    "Flow Sequence",
                    "Movement Integration"
                ],
                "Dumbbells": [
                    "Heavy Complex Work",
                    "Power Development",
                    "Drop Set Series",
                    "Time Under Tension",
                    "Mechanical Advantage",
                    "Pre-Exhaust Protocol",
                    "Giant Sets",
                    "Advanced Techniques"
                ],
                "Full Gym Access": [
                    "Advanced Cable Work",
                    "Machine Intensity",
                    "Power Protocol",
                    "Drop Set Series",
                    "Super Set Work",
                    "Movement Integration",
                    "Time Under Tension",
                    "Peak Contraction"
                ]
            }
        }
    },
    "Core": {
        "Upper Abs": {
            "Beginner": {
                "None/Bodyweight": [
                    "Crunches",
                    "Dead Bug",
                    "Plank Hold",
                    "Bird Dog",
                    "Reverse Crunch",
                    "Flutter Kicks",
                    "Mountain Climbers",
                    "Hollow Body Hold"
                ],
                "Dumbbells": [
                    "Weighted Crunch",
                    "Russian Twist",
                    "Sit-up",
                    "Wood Chop",
                    "Standing Side Bend",
                    "Plate Hold",
                    "DB Pull-in",
                    "Floor Press"
                ],
                "Full Gym Access": [
                    "Cable Crunch",
                    "Machine Crunch",
                    "Decline Bench Work",
                    "Ab Roller",
                    "Hanging Knee Raise",
                    "Cable Wood Chop",
                    "Machine Rotation",
                    "Smith Machine Crunch"
                ]
            },
            "Intermediate": {
                "None/Bodyweight": [
                    "V-Ups",
                    "Hollow Rock",
                    "Dragon Flag Negative",
                    "L-Sit Hold",
                    "Windshield Wiper",
                    "Toes to Bar",
                    "Ab Wheel",
                    "Hanging Leg Raise"
                ],
                "Dumbbells": [
                    "Weighted V-up",
                    "Turkish Get-up",
                    "Renegade Row",
                    "Side Plank Row",
                    "Standing Rotation",
                    "Complex Core Series",
                    "Dynamic Stability",
                    "Power Protocol"
                ],
                "Full Gym Access": [
                    "Cable Core Press",
                    "Decline Weighted Sit-up",
                    "Machine Complex",
                    "Landmine Series",
                    "Swiss Ball Pike",
                    "Cable Rotation",
                    "Ab Sling Work",
                    "Hanging Complex"
                ]
            },
            "Advanced": {
                "None/Bodyweight": [
                    "Dragon Flag",
                    "Front Lever",
                    "Straddle Planche",
                    "Advanced L-Sit",
                    "Strict Toes to Bar",
                    "Human Flag Prep",
                    "Muscle-up Transition",
                    "Movement Flow"
                ],
                "Dumbbells": [
                    "Heavy Get-up Complex",
                    "DB Flow Series",
                    "Power Protocol",
                    "Complex Movement",
                    "Stability Challenge",
                    "Integration Work",
                    "Dynamic Control",
                    "Movement Mastery"
                ],
                "Full Gym Access": [
                    "Advanced Cable Work",
                    "Machine Intensity",
                    "Complex Integration",
                    "Power Development",
                    "Drop Set Protocol",
                    "Time Under Tension",
                    "Movement Flow",
                    "Advanced Technique"
                ]
            }
        }
    },
    "Legs": {
        "Quadriceps": {
            "Beginner": {
                "None/Bodyweight": [
                    "Bodyweight Squats",
                    "Walking Lunges",
                    "Step-ups",
                    "Wall Sits",
                    "Reverse Lunges",
                    "Assisted Pistol Squats",
                    "Split Squats",
                    "Box Step-ups"
                ],
                "Dumbbells": [
                    "Goblet Squats",
                    "DB Front Squats",
                    "DB Split Squats",
                    "DB Lunges",
                    "DB Step-ups",
                    "DB Box Squats",
                    "DB Bulgarian Split Squats",
                    "DB Walking Lunges"
                ],
                "Full Gym Access": [
                    "Leg Press",
                    "Leg Extensions",
                    "Smith Machine Squats",
                    "Hack Squats",
                    "Machine Step-ups",
                    "Sissy Squats",
                    "Linear Leg Press",
                    "Assisted Squat Machine"
                ]
            },
            "Intermediate": {
                "None/Bodyweight": [
                    "Jump Squats",
                    "Pistol Squat Progressions",
                    "Box Jumps",
                    "Split Jump Lunges",
                    "Elevated Split Squats",
                    "Sissy Squats",
                    "Complex Lunge Series",
                    "Plyometric Step-ups"
                ],
                "Dumbbells": [
                    "Heavy DB Front Squats",
                    "DB Jump Squats",
                    "Walking DB Lunges",
                    "Heavy Split Squats",
                    "DB Box Step-overs",
                    "Tempo DB Squats",
                    "DB Reverse Lunges",
                    "Complex Squat Series"
                ],
                "Full Gym Access": [
                    "Barbell Back Squats",
                    "Front Squats",
                    "Heavy Leg Press",
                    "Bulgarian Split Squats",
                    "Hack Squat Machine",
                    "Smith Machine Lunges",
                    "V-Squat Machine",
                    "Complex Leg Series"
                ]
            },
            "Advanced": {
                "None/Bodyweight": [
                    "Pistol Squats",
                    "Plyometric Lunges",
                    "Depth Jumps",
                    "Single-Leg Box Jumps",
                    "Advanced Lunge Complex",
                    "Power Skips",
                    "Complex Jump Series",
                    "Advanced Bodyweight Complex"
                ],
                "Dumbbells": [
                    "Heavy Complex Series",
                    "DB Power Series",
                    "Advanced Lunge Work",
                    "Drop Set Protocol",
                    "Time Under Tension",
                    "Power Development",
                    "Complex Movement Chains",
                    "Integration Series"
                ],
                "Full Gym Access": [
                    "Heavy Squat Protocol",
                    "Olympic Lift Complex",
                    "Advanced Leg Press",
                    "Power Development",
                    "Drop Set Series",
                    "Complex Integration",
                    "Time Under Tension",
                    "Advanced Training Methods"
                ]
            }
        },
        "Hamstrings": {
            "Beginner": {
                "None/Bodyweight": [
                    "Glute Bridges",
                    "Floor Hip Thrusts",
                    "Good Mornings",
                    "Single-Leg Glute Bridge",
                    "Romanian Deadlift Motion",
                    "Leg Curls (stability ball)",
                    "Bird Dogs",
                    "Superman Holds"
                ],
                "Dumbbells": [
                    "DB Romanian Deadlifts",
                    "Single-Leg RDL",
                    "DB Good Mornings",
                    "DB Hip Thrusts",
                    "DB Glute Bridge",
                    "DB Straight Leg Deadlift",
                    "DB Step-Through Lunges",
                    "DB Swing Pattern"
                ],
                "Full Gym Access": [
                    "Leg Curls",
                    "Seated Leg Curls",
                    "Good Morning Machine",
                    "Cable Pull-Throughs",
                    "Smith RDL",
                    "Glute Ham Raise",
                    "45 Degree Back Extension",
                    "Hip Thrust Machine"
                ]
            },
            "Intermediate": {
                "None/Bodyweight": [
                    "Nordic Curl Negatives",
                    "Single-Leg Hip Thrusts",
                    "Sliding Leg Curls",
                    "Advanced Bridge Work",
                    "Band Good Mornings",
                    "Complex Hip Work",
                    "Movement Patterns",
                    "Dynamic Stability"
                ],
                "Dumbbells": [
                    "Heavy RDL Complex",
                    "Single-Leg Series",
                    "Power Development",
                    "Tempo Training",
                    "Complex Movement",
                    "Time Under Tension",
                    "Integration Work",
                    "Dynamic Control"
                ],
                "Full Gym Access": [
                    "Romanian Deadlifts",
                    "Nordic Hamstring Curls",
                    "Glute Ham Raises",
                    "Cable Complex",
                    "Machine Focus Series",
                    "Power Protocol",
                    "Drop Set Work",
                    "Movement Integration"
                ]
            },
            "Advanced": {
                "None/Bodyweight": [
                    "Nordic Curls",
                    "Natural Leg Curls",
                    "Advanced Hip Complex",
                    "Power Development",
                    "Movement Mastery",
                    "Complex Integration",
                    "Dynamic Control",
                    "Advanced Patterns"
                ],
                "Dumbbells": [
                    "Heavy Complex Work",
                    "Power Series",
                    "Drop Set Protocol",
                    "Time Under Tension",
                    "Movement Flow",
                    "Integration Series",
                    "Control Focus",
                    "Advanced Training"
                ],
                "Full Gym Access": [
                    "Advanced Machine Work",
                    "Cable Master Series",
                    "Complex Integration",
                    "Power Development",
                    "Drop Set Protocol",
                    "Time Under Tension",
                    "Movement Pattern",
                    "Advanced Technique"
                ]
            }
        },
        "Calves": {
            "Beginner": {
                "None/Bodyweight": [
                    "Standing Calf Raises",
                    "Seated Calf Raises",
                    "Jump Rope",
                    "Hill Walks",
                    "Step-up Calf Raises",
                    "Single-Leg Balance",
                    "Calf Stretch Series",
                    "Mobility Work"
                ],
                "Dumbbells": [
                    "DB Standing Calf Raise",
                    "Single-Leg DB Raise",
                    "DB Seated Calf Raise",
                    "DB Jump Series",
                    "DB Step Series",
                    "DB Balance Work",
                    "DB Complex",
                    "DB Control Series"
                ],
                "Full Gym Access": [
                    "Machine Calf Raises",
                    "Smith Machine Raises",
                    "Seated Calf Machine",
                    "Leg Press Calf Raise",
                    "Cable Calf Work",
                    "Balance Machine",
                    "Movement Pattern",
                    "Control Series"
                ]
            },
            "Intermediate": {
                "None/Bodyweight": [
                    "Jump Series",
                    "Single-Leg Complex",
                    "Plyometric Work",
                    "Balance Training",
                    "Movement Flow",
                    "Power Development",
                    "Control Series",
                    "Integration Work"
                ],
                "Dumbbells": [
                    "Heavy Raise Series",
                    "Single-Leg Focus",
                    "Jump Complex",
                    "Power Protocol",
                    "Time Under Tension",
                    "Movement Pattern",
                    "Control Work",
                    "Integration Series"
                ],
                "Full Gym Access": [
                    "Machine Complex",
                    "Heavy Focus Work",
                    "Power Development",
                    "Drop Set Series",
                    "Time Under Tension",
                    "Movement Flow",
                    "Control Focus",
                    "Integration Pattern"
                ]
            },
            "Advanced": {
                "None/Bodyweight": [
                    "Advanced Jump Work",
                    "Plyometric Series",
                    "Complex Movement",
                    "Power Protocol",
                    "Balance Challenge",
                    "Movement Flow",
                    "Control Focus",
                    "Integration Series"
                ],
                "Dumbbells": [
                    "Heavy Complex Work",
                    "Power Development",
                    "Drop Set Series",
                    "Time Under Tension",
                    "Movement Pattern",
                    "Control Focus",
                    "Integration Work",
                    "Advanced Training"
                ],
                "Full Gym Access": [
                    "Machine Master Series",
                    "Complex Integration",
                    "Power Protocol",
                    "Drop Set Work",
                    "Time Under Tension",
                    "Movement Flow",
                    "Control Focus",
                    "Advanced Technique"
                ]
            }
        }
    }
}

# Training guidelines definition
training_guidelines = {
    "Hybrid Training": {
        "rep_range": "Varied (3-15)",
        "sets_per_exercise": "3-5",
        "rest_period": "60-120 seconds",
        "intensity": "65-85% 1RM",
        "frequency": "4-5 days/week",
        "tempo": "Varied",
        "techniques": [
            "Strength-Endurance Supersets",
            "Power-Hypertrophy Complexes",
            "CrossFit-Style WODs",
            "Circuit-Strength Combinations",
            "HIIT with Strength Elements"
        ],
        "summary": "Combines multiple training modalities (strength, power, endurance) in structured workouts. Alternates between heavy compound movements and high-intensity cardio/bodyweight exercises for comprehensive fitness development.",
        "workout_structure": "Typically includes: 1) Strength component (2-3 compound exercises), 2) Power/explosive movement, 3) High-intensity conditioning circuit",
        "recovery_focus": "Strategic deload weeks and alternating intensity days to prevent overtraining"
    },
    "Hypertrophy": {
        "rep_range": "8-12",
        "sets_per_exercise": "3-5",
        "rest_period": "60-90 seconds",
        "intensity": "65-80% 1RM",
        "frequency": "4-5 days/week",
        "tempo": "2-1-2",
        "techniques": [
            "Progressive Overload",
            "Time Under Tension",
            "Drop Sets",
            "Super Sets",
            "Rest-Pause Sets"
        ],
        "summary": "Focus on moderate weights with controlled form and optimal time undertension. Incorporate progressive overload and varied techniques to maximize muscle growth."
    },
    "Weight Loss": {
        "rep_range": "12-15",
        "sets_per_exercise": "3-4",
        "rest_period": "30-60 seconds",
        "intensity": "60-75% 1RM",
        "frequency": "3-5 days/week",
        "tempo": "2-0-1",
        "techniques": [
            "Circuit Training",
            "HIIT",
            "Supersets",
            "Compound Movements",
            "Active Recovery"
        ],
        "summary": "Focus on higher reps with shorter rest periods to maximize calorie burn and improve metabolic conditioning. Combine with proper nutrition and cardio."
    },
    "Muscle Gain": {
        "rep_range": "6-12",
        "sets_per_exercise": "4-6",
        "rest_period": "90-120 seconds",
        "intensity": "70-85% 1RM",
        "frequency": "4-6 days/week",
        "tempo": "2-1-2",
        "techniques": [
            "Progressive Overload",
            "Volume Training",
            "Mechanical Drop Sets",
            "Pre-exhaust Sets",
            "Giant Sets"
        ],
        "summary": "Emphasize progressive overload with moderate to heavy weights and adequate rest between sets for optimal muscle growth. Focus on proper nutrition and recovery."
    },
    "Strength": {
        "rep_range": "1-6",
        "sets_per_exercise": "4-6",
        "rest_period": "2-5 minutes",
        "intensity": "85-95% 1RM",
        "frequency": "3-4 days/week",
        "tempo": "2-1-X",
        "techniques": [
            "Progressive Overload",
            "Cluster Sets",
            "Heavy Singles",
            "Partial Reps",
            "Accommodating Resistance"
        ],
        "summary": "Focus on low reps with heavy weights and longer rest periods to maximize strength gains. Emphasize compound movements and proper form."
    },
    "Endurance": {
        "rep_range": "15-30+",
        "sets_per_exercise": "2-4",
        "rest_period": "15-45 seconds",
        "intensity": "40-65% 1RM",
        "frequency": "3-5 days/week",
        "tempo": "1-0-1",
        "techniques": [
            "Circuit Training",
            "AMRAP Sets",
            "Density Training",
            "EMOMs",
            "Metabolic Conditioning"
        ],
        "summary": "Use lighter weights with high reps and minimal rest to build muscular endurance and stamina. Focus on maintaining form throughout high-volume work."
    },
    "Power": {
        "rep_range": "3-5",
        "sets_per_exercise": "4-6",
        "rest_period": "2-3 minutes",
        "intensity": "70-85% 1RM",
        "frequency": "2-4 days/week",
        "tempo": "X-0-X",
        "techniques": [
            "Olympic Lifts",
            "Plyometrics",
            "Explosive Movements",
            "Complex Training",
            "Contrast Sets"
        ],
        "summary": "Focus on explosive movements and perfect technique. Combine strength training with plyometrics and Olympic lifting variations."
    },
    "General Fitness": {
        "rep_range": "8-15",
        "sets_per_exercise": "2-4",
        "rest_period": "45-90 seconds",
        "intensity": "60-75% 1RM",
        "frequency": "3-4 days/week",
        "tempo": "2-0-2",
        "techniques": [
            "Circuit Training",
            "Compound Movements",
            "Functional Training",
            "Core Stability",
            "Mobility Work"
        ],
        "summary": "Balanced approach combining elements of strength, endurance, and conditioning for overall fitness improvement. Focus on functional movements and proper form."
    }
}