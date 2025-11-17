"""Модели используемые приложением"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


@dataclass
class QuantityTypes:
    """Ингредиент"""
    quantity_id: int
    quantity_label: str


@dataclass
class Ingredient:
    """Ингредиент"""
    ingredient_id: int
    ingredient_label: str
    ingredient_quantity: int
    ingredient_quantity_type: QuantityTypes


@dataclass
class Meal:
    """Блюдо"""
    meal_id: int
    meal_label: str
    meal_ingredients: List[Ingredient]

    def add_ingredient(self, ingredient: Ingredient):
        """Добавить в блюдо ингридиент"""
        self.meal_ingredients.append(ingredient)

    def add_ingredients(self, ingredients: List[Ingredient]):
        """Добавить несколько ингредиентов"""
        for el in ingredients:
            self.add_ingredient(el)

    def format_ingredients_list(self) -> str:
        res_message = ''
        list_meals = ''
        max_length_ingredient: int = max(
            [len(el.ingredient_label)
             for el in self.meal_ingredients]
        ) + 5

        name = f'Название блюда: {self.meal_label}\n'
        name_list_meals = 'Список ингредиентов:\n'

        for meal in self.meal_ingredients:
            ingredient_label = meal.ingredient_label + ':'
            list_meals += f'- {ingredient_label:<{max_length_ingredient}}'\
                f'{meal.ingredient_quantity} {meal.ingredient_quantity_type.quantity_label}\n'

        res_message += name + '\n' + name_list_meals + list_meals
        return res_message

    def format_short_data(self) -> str:
        """Показать короткую информацию о рецепте"""
        return f'{self.meal_id}: {self.meal_label}. Кол-во ингредиентов: '\
            f'{len(self.meal_ingredients)}\n'


class DayOfWeek(Enum):
    """Список дней недели"""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


@dataclass
class DailyMealPlan:
    """План питания на день"""
    day: DayOfWeek
    meals: List[Meal]

    def add_meal(self, meal: Meal):
        """Добавить блюдо в план дня"""
        self.meals.append(meal)

    def remove_meal(self, meal_id: int):
        """Удалить блюдо из плана дня по ID"""
        self.meals = [meal for meal in self.meals if meal.meal_id != meal_id]

    def clear_day(self):
        """Удалить все блюда со дня"""
        self.meals = []

    def get_meals(self) -> List[Meal]:
        """Получить все блюда дня"""
        return self.meals


@dataclass
class CartElement:
    cart_order: int
    ingredient_label: str
    total_value: int
    ingredient_type: str
    is_ingredient_bought: bool

    def __init__(
        self,
        cart_order: int,
        ingredient_label: Optional[str] = None,
        total_value: Optional[int] = None,
        ingredient_type: Optional[str] = None,
        ingredient: Optional[Ingredient] = None,
        is_ingredient_bought: bool = False
    ):
        self.cart_order = cart_order
        self.is_ingredient_bought = is_ingredient_bought
        if ingredient is not None:
            self.from_ingredient(ingredient=ingredient)
        else:
            if total_value is None or ingredient_type is None or ingredient_label is None:
                raise TypeError('Not found ingredient types')
            self.ingredient_label = ingredient_label
            self.total_value = total_value
            self.ingredient_type = ingredient_type

    def from_ingredient(self, ingredient: Ingredient):
        self.ingredient_label = ingredient.ingredient_label
        self.total_value = ingredient.ingredient_quantity
        self.ingredient_type = ingredient.ingredient_quantity_type.quantity_label

    def add_value(self, value: int, cart_type: str):
        if self.ingredient_type != cart_type:
            print('WARNING: not compatible type')
        self.total_value += value

    def is_ingredient_equal(self, ingredient: Ingredient) -> bool:
        return self.ingredient_label == ingredient.ingredient_label

AVAILABLE_SEPARATORS = [':', ';', '-']