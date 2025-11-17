"""Для запуска нужных сервисов и проверки"""
import calendar_service
from services.entity import DayOfWeek
import recipe_service
import basket_service


def start():
    meal = recipe_service.create_meal('Флоцки')
    i1 = recipe_service.create_ingredient('Макароны', 200)
    i2 = recipe_service.create_ingredient('Фарш', 200)
    i3 = recipe_service.create_ingredient('Соль', 150)

    meal1 = recipe_service.create_meal('Вафли')
    i4 = recipe_service.create_ingredient('Мука', 200)
    i5 = recipe_service.create_ingredient('Масло', 200)

    meal.add_ingredients(ingredients=[i1, i2, i3])
    # for i in range(100):
    #     rec = recipe_service.create_ingredient(f'Масло {i}', 200)
    #     meal.add_ingredient(rec)
    meal1.add_ingredients(ingredients=[i4, i5])
    print(meal.format_ingredients_list())

    bs = basket_service.get_or_create_cart()
    print(basket_service.format_week_cart(bs))

    calendar_service.add_meal_to_day(1, meal)
    calendar_service.add_meal_to_day(4, meal)
    bs = basket_service.create_week_ingrediend_list()
    calendar_service.add_meal_to_day(1, meal1)
    calendar_service.add_meal_to_day(0, meal)

    bs = basket_service.create_week_ingrediend_list()
    print(basket_service.format_week_cart(bs))

    basket_service.buy_cart_item_by_id(bs[0].cart_id)
    bs = basket_service.get_or_create_cart()
    print(basket_service.format_week_cart(bs))


if __name__ == '__main__':
    start()
