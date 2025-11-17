from typing import List, Optional, Union
import fake_database
import services.entity as entity


def get_meals() -> List[entity.Meal]:
    """Получить блюда"""
    return fake_database.meals


def get_meal(meal_id: int) -> entity.Meal:
    """Получить одно блюдо"""
    return fake_database.meals[meal_id]


def get_last_user_meal():
    return fake_database.meals[-1]


def create_meal(label: str) -> entity.Meal:
    """Создать блюдо"""
    fake_meal_id = len(fake_database.meals)
    label.strip('\n').capitalize()
    meal = entity.Meal(meal_id=fake_meal_id,
                       meal_label=label, meal_ingredients=[])
    fake_database.meals.append(meal)
    return meal


def update_meal(meal: entity.Meal) -> None:
    fake_database.meals[meal.meal_id] = meal


def get_ingredients():
    """Получить ингредиенты"""
    return fake_database.ingredients


def create_ingredient(label: str, quantity: int) -> entity.Ingredient:
    """Создать ингридиент"""
    fake_ingredient_id = len(fake_database.ingredients)
    gram = fake_database.quantity_types[0]

    label = label.strip().capitalize()

    ingredient = entity.Ingredient(
        ingredient_id=fake_ingredient_id,
        ingredient_label=label,
        ingredient_quantity=quantity,
        ingredient_quantity_type=gram
    )
    fake_database.ingredients.append(ingredient)
    return ingredient


def add_ingredient(meal: entity.Meal, *ingredients: entity.Ingredient) -> entity.Meal:
    """Добавить ингредиенты в блюдо"""
    for ing in ingredients:
        meal.add_ingredient(ing)
    return meal
