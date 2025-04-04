def calculate_bmr(weight, height, age, gender):
    """
    Calculate Basal Metabolic Rate using the Mifflin-St Jeor Equation
    """
    if gender == "Male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    return bmr

def calculate_tdee(bmr, activity_factor):
    """
    Calculate Total Daily Energy Expenditure
    """
    return bmr * activity_factor

def calculate_protein_needs(weight, goal):
    """
    Calculate daily protein needs based on weight and goal
    """
    if goal == "Gain Muscle":
        return weight * 2.2  # 2.2g per kg
    elif goal == "Lose Weight":
        return weight * 2.0  # 2.0g per kg
    else:
        return weight * 1.8  # 1.8g per kg for maintenance
