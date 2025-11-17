from typing import Dict, List
import services.entity as entity
from database import fake_database


def add_meal_to_day(day_id: int, meal: entity.Meal):
    """Добавить блюдо к определенному дню недели"""
    fake_database.weekly_plan[day_id].add_meal(meal)


def get_weekly_plan() -> Dict[entity.DayOfWeek, List[entity.Meal]]:
    """Получить весь недельный план"""
    return {plan.day: plan.meals for plan in fake_database.weekly_plan}

def get_formatted_weekly_plan() -> str:
    """Получить сообщение с форматированным недельным планом"""
    calendar = get_weekly_plan()
    msg = ''
    for day, meals in calendar.items():
        if len(meals) != 0:
            msg += f'{day.name}:\n'
            for meal in meals:
                msg += meal.format_short_data() + '\n'
    return msg


def clear_week():
    """Очистить весь недельный план"""
    fake_database.weekly_plan = [
        el.clear_day() for el in fake_database.weekly_plan]

# def remove_meal_from_day(self, day: DayOfWeek, meal_id: int):
#     """Удалить блюдо из определенного дня недели"""
#     self.weekly_plan[day].remove_meal(meal_id)
