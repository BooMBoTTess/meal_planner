from typing import List, Optional
from database import fake_database
from services import entity
import services.entity as entity


def get_meals() -> List[entity.Meal]:
    """Получить блюда"""
    return fake_database.meals


def get_meal(meal_id: int) -> entity.Meal:
    """Получить одно блюдо"""
    return fake_database.meals[meal_id]


def get_last_user_meal():
    """Получить последнее блюдо пользователя"""
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
    """Обновить блюдо"""
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


def _get_ingredients_known_separator(
        text: str,
        separator: str
        ) -> List[entity.Ingredient]:
    """Получить ингредиенты с известным сепаратором"""
    ingredients: List[entity.Ingredient] = []
    lines = text.split('\n')
    
    for line in lines:
        name, value = line.split(sep=separator)
        value = int(value)
        ingredient = create_ingredient(
            label=name,
            quantity=value
        )
        ingredients.append(ingredient)
    return ingredients


def _get_ingredients_unknown_separator(
        text: str,
        ) -> List[entity.Ingredient]:
    """Получить ингредиент с неизвестным разделителем."""
    separators = entity.AVAILABLE_SEPARATORS
    ingredients: List[entity.Ingredient] = []
    lines = text.split('\n')
    sep_counter = 0
    for line in lines:
        sep_counter = 0
        separator = separators[sep_counter]
        while line.find(separator) == -1:
            sep_counter += 1
            separator = separators[sep_counter]
        name, value = line.split(sep=separator, maxsplit=1)
        value = int(value)
        ingredient = create_ingredient(
            label=name,
            quantity=value
        )
        ingredients.append(ingredient)
    return ingredients

def get_ingredients_from_text(
        text: str, 
        separator: Optional[str] = None
    ) -> List[entity.Ingredient]:
    """Получить ингредиент по тексту.

    Args:
        text: Текст сообщения.
        separator: Разделитель названия и значения. Если не указано то попробует 
            с несколькими из entity.

    Return: 
        Список ингредиентов
    """
    if separator is None:
        ingredients = _get_ingredients_unknown_separator(text=text)
    else:
        ingredients = _get_ingredients_known_separator(text=text, separator=separator)
    return ingredients