from typing import List
import fake_database
import services.entity as entity
import basket_manager


def create_week_ingrediend_list() -> List[entity.CartElement]:
    """Создать новую корзину"""
    meals: List[entity.Meal] = []
    ingredients: List[entity.Ingredient] = []
    for el in fake_database.weekly_plan:
        meals.extend(el.get_meals())
    for el in meals:
        ingredients.extend(el.meal_ingredients)
    cart: List[entity.CartElement] = []
    for ingredient in ingredients:
        cart = add_ingredient_to_cart(
            cart_elements=cart, ingredient=ingredient)
    basket_manager.insert_cart(cart)
    return cart


def get_cart() -> List[entity.CartElement]:
    """Получить корзину"""
    return basket_manager.get_cart()


def get_or_create_cart() -> List[entity.CartElement]:
    """Получить или создать список ингредиентов на неделю"""
    cart = get_cart()
    if not cart:
        cart = create_week_ingrediend_list()
    return cart


def format_week_cart(cart_list: List[entity.CartElement]) -> str:
    """Отформатировать недельную корзину"""
    msg = ''
    for el in cart_list:
        msg += f'{el.cart_id}: {el.ingredient_label}: {el.total_value} {el.cart_type}\n'
    return msg


def _find_cart_index(cart_elements: List[entity.CartElement], ingredient: entity.Ingredient):
    for i in range(len(cart_elements)):
        if cart_elements[i].is_ingredient_equal(ingredient=ingredient):
            return i
    return -1


def add_ingredient_to_cart(cart_elements: List[entity.CartElement], ingredient: entity.Ingredient):
    cart_index = _find_cart_index(
        cart_elements=cart_elements, ingredient=ingredient)
    if cart_index == -1:
        tmp = entity.CartElement(ingredient=ingredient)
        cart_elements.append(tmp)
    else:
        cart_elements[cart_index].add_value(
            ingredient.ingredient_quantity, ingredient.ingredient_quantity_type.quantity_label)

    return cart_elements


def buy_cart_item_by_id(item_id: int):
    """Купить ингредиент из корзины"""
    basket_manager.update_item_bought(item_id)
