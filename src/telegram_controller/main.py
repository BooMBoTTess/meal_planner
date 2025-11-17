"""Управление сервисом через тг бота"""
import src.basket_service
import main
import os
import logging
import sys
from typing import Any, Dict, List, Tuple

import telebot
from dotenv import load_dotenv
from telebot import types
from telebot import apihelper

import calendar_service
import services.entity as entity
import text_template
import recipe_service

logger = logging.getLogger('bot')
formatter = logging.Formatter(
    '%(asctime)s (%(filename)s:%(lineno)d %(threadName)s) %(levelname)s - %(name)s: "%(message)s"'
)


console_output_handler = logging.StreamHandler(sys.stdout)
console_output_handler.setFormatter(formatter)
logger.addHandler(console_output_handler)

logger.setLevel(logging.DEBUG)

load_dotenv()
BOT_TOKEN: str = os.getenv('BOT_TOKEN', default='NOT FOUND')

bot = telebot.TeleBot(BOT_TOKEN)


def create_yes_no_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_yes = types.KeyboardButton(
        text=text_template.KEYBOARD_YES)
    button_no = types.KeyboardButton(
        text=text_template.KEYBOARD_NO)
    keyboard.add(button_yes, button_no)  # type: ignore
    return keyboard


def create_stop_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton(
        text=text_template.KEYBOARD_STOP_CREATE_INGREDIENT)
    keyboard.add(button)  # type: ignore
    return keyboard


def create_days_keyboard() -> types.ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for day in entity.DayOfWeek:
        button = types.KeyboardButton(
            text=day.name
        )
        keyboard.add(button)  # type: ignore
    button = types.KeyboardButton(text=text_template.KEYBOARD_BUTTON_CANCEL)
    keyboard.add(button)  # type: ignore
    return keyboard


def create_cart_keyboard(cart: List[entity.CartElement]) -> types.ReplyKeyboardMarkup:
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for el in cart:
        button = types.KeyboardButton(
            text=str(el.cart_id) + ': ' + str(el.ingredient_label)
        )
        keyboard.add(button)  # type: ignore
    button = types.KeyboardButton(text=text_template.KEYBOARD_BUTTON_CANCEL)
    keyboard.add(button)  # type: ignore
    return keyboard


def _get_all_commands():
    """Получить все комманды от ручек"""
    handlers: List[Dict[str, Any]] = bot.message_handlers  # type: ignore
    commands: List[str] = []
    for handler in handlers:
        command = handler['filters']['commands']
        commands.extend(command)
    text_commands: List[str] = []
    for command in commands:
        text_commands.append('/' + command)
    logger.debug(text_commands)
    return text_commands


def create_start_keyboard() -> types.ReplyKeyboardMarkup:
    commands = _get_all_commands()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for command in commands:
        button = types.KeyboardButton(
            text=command
        )
        keyboard.add(button)  # type: ignore
    return keyboard


KEYBOARD_YES_NO = create_yes_no_keyboard()

KEYBOARD_STOP = create_stop_keyboard()

KEYBOARD_DAYS = create_days_keyboard()

KEYBOARD_START = create_start_keyboard()


@bot.message_handler(commands=['start'])  # type: ignore
def start_message(message: types.Message):
    """Привет!"""
    handlers: List[Dict[str, Any]] = bot.message_handlers  # type: ignore
    commands_list = _get_all_commands()
    msg_commands = ''
    for command in commands_list:
        msg_commands += f'- {command}\n'
    msg = text_template.HELLO + msg_commands
    bot.send_message(
        chat_id=message.chat.id,
        text=msg,
        reply_markup=KEYBOARD_START
    )


@bot.message_handler(commands=['create_recipe'])  # type: ignore
def start_recipe_creating(message: types.Message):
    """Процесс создания рецепта"""
    logger.info('start_recipe_creating')
    bot.send_message(message.chat.id, text_template.START_RECIPE_CREATING)
    bot.register_next_step_handler(  # type: ignore
        message=message, callback=create_recipe)


def create_recipe(message: types.Message):
    """Создать новый рецепт.

    Первый шаг создания рецепта.

    Название рецепта это текст из сообщения.
    """
    logger.info('create_recipe')
    if message.text is not None:
        meal = recipe_service.create_meal(message.text)
        logger.debug(meal)

        bot.send_message(chat_id=message.chat.id,
                         text=text_template.ASK_FIRST_CREATE_INGREDIENT,
                         reply_markup=KEYBOARD_YES_NO)
        bot.register_next_step_handler(  # type: ignore
            message=message, callback=branch_create_ingredient)

    else:
        bot.send_message(chat_id=message.chat.id,
                         text='Некорректный вид сообщения')


def branch_create_ingredient(message: types.Message):
    """Выбор пользователя о создании ингредиента"""
    text = message.text
    if text == text_template.KEYBOARD_YES:
        bot.send_message(
            chat_id=message.chat.id,
            text=text_template.WANT_CREATE_INGREDIENT,
            reply_markup=types.ReplyKeyboardRemove()
        )
        bot.register_next_step_handler(  # type: ignore
            message=message, callback=loop_create_ingredient)
    elif text == text_template.KEYBOARD_NO:
        bot.send_message(
            chat_id=message.chat.id,
            text=text_template.NOT_WANT_CREATE_INGREDIENT,
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        try:  # Проверка вдруг были отправлены ингредиенты
            text = str(message.text)
            ingredients = _get_ingredients_from_message(text)
        except ValueError:
            bot.send_message(
                chat_id=message.chat.id,
                text=text_template.ERROR_WANT_CREATE_INGREDIENT
            )
            bot.register_next_step_handler(  # type: ignore
                message=message, callback=branch_create_ingredient)
        else:
            _create_ingredient(message=message, ingredients=ingredients)


def _get_ingredients_from_message(text: str) -> List[entity.Ingredient]:
    ingredients: List[entity.Ingredient] = []
    lines = text.split('\n')
    for line in lines:
        name, value = line.split(':')
        value = int(value)
        ingredient = recipe_service.create_ingredient(
            label=name,
            quantity=value
        )
        ingredients.append(ingredient)
    return ingredients


def _create_ingredient(message: types.Message, ingredients: List[entity.Ingredient]):
    meal = recipe_service.get_last_user_meal()
    meal.add_ingredients(ingredients=ingredients)
    recipe_service.update_meal(meal=meal)
    bot.send_message(chat_id=message.chat.id,
                     text=text_template.SUCCES_CREATE_INGREDIENT,
                     reply_markup=KEYBOARD_STOP)
    bot.register_next_step_handler(  # type: ignore
        message=message, callback=loop_create_ingredient)
    logger.debug(meal)


def loop_create_ingredient(message: types.Message):
    """Цикл по созданию ингредиентов для блюда"""
    logger.info('loop_create_ingredient')
    text = str(message.text)
    if text != text_template.KEYBOARD_STOP_CREATE_INGREDIENT:
        # Добавляем ингредиент
        try:
            ingredients = _get_ingredients_from_message(text)
        except ValueError:
            bot.send_message(chat_id=message.chat.id,
                             text=text_template.INCORRECT_INGREDIENT_MESSAGE)
            bot.register_next_step_handler(  # type: ignore
                message=message, callback=loop_create_ingredient)
        else:
            # Успешное добавление
            _create_ingredient(message=message, ingredients=ingredients)
    else:
        # Конец добавление ингредиентов
        meal = recipe_service.get_last_user_meal()
        logger.debug(meal.format_ingredients_list())
        msg = meal.format_ingredients_list()
        msg = '<pre>' + msg + '</pre>'
        bot.send_message(
            chat_id=message.chat.id,
            text=text_template.END_CREATING_INGREDIENT +
            '\n' + msg + text_template.END_CREATING_INGREDIENT_ENDING,
            parse_mode='HTML',
            reply_markup=KEYBOARD_DAYS)
        bot.register_next_step_handler(  # type: ignore
            message=message, callback=add_last_meal_to_day)


def add_last_meal_to_day(message: types.Message):
    """После создания рецепта добавить его в день"""
    try:
        day = entity.DayOfWeek[message.text]  # type: ignore
        meal = recipe_service.get_last_user_meal()
        # TODO: Надо переделать дни недели
        calendar_service.add_meal_to_day(day.value, meal=meal)
        bot.send_message(chat_id=message.chat.id,
                         text=text_template.SUCCESS_ADD_RECIPE_TO_DAY,
                         reply_markup=types.ReplyKeyboardRemove()
                         )
        logger.debug(calendar_service.get_weekly_plan())
    except KeyError:
        bot.send_message(chat_id=message.chat.id,
                         text=text_template.CANCEL_RECIPE_TO_DAY,
                         reply_markup=types.ReplyKeyboardRemove()
                         )


def get_short_recipes(meals: List[entity.Meal]):
    res = ''
    for meal in meals:
        res += meal.format_short_data()
    return res


@bot.message_handler(commands=['get_recipes'])  # type: ignore
def get_recipes(message: types.Message):
    """Получить все рецепты"""
    meals = recipe_service.get_meals()
    msg = text_template.GET_RECIPES_LIST + get_short_recipes(meals)
    bot.send_message(
        chat_id=message.chat.id,
        text=msg
    )


@bot.message_handler(commands=['get_calendar'])  # type: ignore
def get_calendar(message: types.Message):
    """Получить все рецепты"""
    msg = calendar_service.get_formatted_weekly_plan()
    bot.send_message(
        chat_id=message.chat.id,
        text=msg
    )


@bot.message_handler(commands=['add_recipe_to_day'])  # type: ignore
def inform_add_recipe_to_calendar(message: types.Message):
    """Получить все рецепты"""
    meals = recipe_service.get_meals()
    msg_meals = 'Список рецептов:\n' + get_short_recipes(meals)
    msg_days = 'Список дней:\n'
    for day in entity.DayOfWeek:
        msg_days += f'{day.value}: {day.name}\n'
    msg = text_template.ADD_RECIPES_TO_DAY + '\n' + msg_meals + '\n' + msg_days
    bot.send_message(
        chat_id=message.chat.id,
        text=msg, parse_mode='HTML'
    )
    bot.register_next_step_handler(  # type: ignore
        message=message, callback=add_recipe_to_calendar)


def _split_message(text: str) -> Tuple[int, int]:
    """Проверить сообщения добавление рецепта в календарь"""
    day_id, meal_id = text.split(':')
    day_id, meal_id = int(day_id), int(meal_id)
    return day_id, meal_id


def add_recipe_to_calendar(message: types.Message):
    """Исполнение функции добавление рецепта в день"""
    text = str(message.text)
    day_id, meal_id = _split_message(text)
    meal = recipe_service.get_meal(meal_id=meal_id)
    calendar_service.add_meal_to_day(day_id, meal)
    bot.send_message(
        chat_id=message.chat.id,
        text=text_template.SUCCESS_ADD_MEAL_TO_DAY, parse_mode='HTML'
    )


@bot.message_handler(commands=['get_cart'])  # type: ignore
def get_cart_list(message: types.Message):
    """Получить все рецепты"""
    cart = basket_service.get_or_create_cart()
    msg = text_template.GET_CART_LIT + \
        basket_service.format_week_cart(cart_list=cart)
    cart_keyboart = create_cart_keyboard(cart)
    bot.send_message(
        chat_id=message.chat.id,
        text=msg,
        reply_markup=cart_keyboart
    )
    bot.register_next_step_handler(  # type: ignore
        message=message, callback=take_cart_element)


@bot.message_handler(commands=['create_new_cart'])  # type: ignore
def create_cart_list(message: types.Message):
    """Получить все рецепты"""
    cart = basket_service.create_week_ingrediend_list()
    msg = text_template.GET_CART_LIT + \
        basket_service.format_week_cart(cart_list=cart)
    bot.send_message(
        chat_id=message.chat.id,
        text=msg,
    )
    bot.register_next_step_handler(  # type: ignore
        message=message, callback=take_cart_element)


def take_cart_element(message: types.Message):
    """Убрать элемент из списка"""
    text = str(message.text)
    if text == text_template.KEYBOARD_BUTTON_CANCEL:
        bot.send_message(
            chat_id=message.chat.id,
            text=text_template.END_CART_PROCESS,
            reply_markup=KEYBOARD_START
        )
    else:
        item_id: int = int(text.split(':', maxsplit=1)[0])
        basket_service.buy_cart_item_by_id(item_id)
        cart = basket_service.get_cart()
        if cart:
            msg = text_template.GET_CART_LIT + \
                basket_service.format_week_cart(cart_list=cart)
            cart_keyboart = create_cart_keyboard(cart)
            bot.send_message(
                chat_id=message.chat.id,
                text=msg,
                reply_markup=cart_keyboart
            )
            bot.register_next_step_handler(  # type: ignore
                message=message, callback=take_cart_element)
        else:
            bot.send_message(
                chat_id=message.chat.id,
                text=text_template.END_CART_PROCESS,
                reply_markup=KEYBOARD_START
            )


KEYBOARD_START = create_start_keyboard()  # type: ignore

main.start()
logger.info('start bot polling')
try:
    bot.infinity_polling()  # type: ignore
except apihelper.ApiHTTPException:
    logger.error(msg='ApiHTTPException', exc_info=True)
