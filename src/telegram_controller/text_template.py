"""Шаблоны сообщений ТГ бота"""
# Шаблоны шаблонов
INGREDIENT_TEMPLATE = '"Название: Количество"'

# Клавиши
KEYBOARD_YES = 'Да!'
KEYBOARD_NO = 'Нет 🥲.'
KEYBOARD_BUTTON_CANCEL = 'Завершить'

# Шаблоны сообщений
HELLO = 'Привет. Ты знаешь что делать, а если не знаешь уходи.\navailable_commands:\n'
START_RECIPE_CREATING = 'Хорошо, Давай начнем создавать рецепт. Напиши название рецепта'
ASK_FIRST_CREATE_INGREDIENT = 'Хочешь создать ингредиенты для рецепта?'
WANT_CREATE_INGREDIENT = 'Хорошо. Тогда напиши название ингредиента и его количество в '\
    f'граммах в виде. {INGREDIENT_TEMPLATE}'
NOT_WANT_CREATE_INGREDIENT = 'Ты хочешь добавить ингредиент в день?'
ERROR_WANT_CREATE_INGREDIENT = 'НАЖМИ НА КЛАВИАТУРЕ ДА ИЛИ НЕТ'
KEYBOARD_STOP_CREATE_INGREDIENT = 'ОСТАНОВИСЬ!!!!'
INCORRECT_INGREDIENT_MESSAGE = f'Некорректно написан ингедиент. Шаблон  {INGREDIENT_TEMPLATE}'
SUCCES_CREATE_INGREDIENT = 'Ингредиент успешно добавлен. Можешь продолжить писать ' \
    'ингредиенты по шаблону или нажми на появившуюся клавиатуру'
END_CREATING_INGREDIENT = 'Ингредиенты успешно созданы. Получившееся блюдо:\n'
END_CREATING_INGREDIENT_ENDING = 'Выберите на клавиатуре день недели, для добавления в базу данных.'
SUCCESS_ADD_RECIPE_TO_DAY = 'Успешно добавлен рецепт в день'
CANCEL_RECIPE_TO_DAY = 'Отменено добавление рецепта в день'
GET_RECIPES_LIST = 'Список рецептов:\n'
ADD_RECIPES_TO_DAY = 'Вызвана функция добавления рецептов. Напишите ID дня недели из списка'\
    'ниже, а также ID рецепта в формате: <b>day_id: recipe_id</b>.\n'
SUCCESS_ADD_MEAL_TO_DAY = 'Успешно добавлено блюдо в день'
GET_CART_LIT = 'Список покупок:\n'
END_CART_PROCESS = 'Завершено заполнение корзины.'
ADD_CART_ITEM = 'Напиши ингредиент в виде: Название: количество. Или нажми Отмена на клавиатуре.'
ERROR_CART_BUY = 'Ошибка при получении товара. Может быть некорректный ввод. ' \
                    'Для повторной попытки покупки вызови корзину назад.'