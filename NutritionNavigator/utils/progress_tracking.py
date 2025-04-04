from sqlalchemy.orm import Session
from models.database import ProgressEntry
from datetime import datetime, timedelta
import pandas as pd
from typing import List, Optional, Dict, Any

def add_progress_entry(
    db: Session,
    user_id: int,
    current_weight: float,
    calories_consumed: float,
    protein_consumed: float,
    notes: Optional[str] = None
) -> Optional[ProgressEntry]:
    """Add a new progress entry for the user"""
    try:
        progress_entry = ProgressEntry(
            user_id=user_id,
            current_weight=current_weight,
            calories_consumed=calories_consumed,
            protein_consumed=protein_consumed,
            notes=notes
        )
        db.add(progress_entry)
        db.commit()
        db.refresh(progress_entry)
        return progress_entry
    except Exception as e:
        db.rollback()
        raise Exception(f"Error adding progress entry: {str(e)}")

def get_user_progress(
    db: Session,
    user_id: int,
    days: int = 30
) -> Dict[str, List]:
    """Get user's progress data for the specified number of days"""
    try:
        start_date = datetime.now().date() - timedelta(days=days)
        entries = (
            db.query(ProgressEntry)
            .filter(
                ProgressEntry.user_id == user_id,
                ProgressEntry.date >= start_date
            )
            .order_by(ProgressEntry.date)
            .all()
        )

        progress_data = {
            'dates': [],
            'weights': [],
            'calories': [],
            'protein': []
        }

        for entry in entries:
            progress_data['dates'].append(entry.date)
            progress_data['weights'].append(entry.current_weight)
            progress_data['calories'].append(entry.calories_consumed)
            progress_data['protein'].append(entry.protein_consumed)

        return progress_data
    except Exception as e:
        raise Exception(f"Error retrieving progress data: {str(e)}")

def calculate_progress_metrics(progress_data: Dict[str, List]) -> Dict[str, float]:
    """Calculate progress metrics from the user's data"""
    if not progress_data['weights']:
        return {
            'weight_change': 0.0,
            'avg_calories': 0.0,
            'avg_protein': 0.0
        }

    weight_change = progress_data['weights'][-1] - progress_data['weights'][0]
    avg_calories = sum(progress_data['calories']) / len(progress_data['calories'])
    avg_protein = sum(progress_data['protein']) / len(progress_data['protein'])

    return {
        'weight_change': round(weight_change, 1),
        'avg_calories': round(avg_calories, 1),
        'avg_protein': round(avg_protein, 1)
    }
