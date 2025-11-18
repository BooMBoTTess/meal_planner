"""Управление сервисом через тг бота"""
from logger_wrapper import wrap_logger
from services import basket_service, calendar_service, recipe_service
import os
import logging
import sys
from typing import Any, Dict, List, Tuple

import telebot
from dotenv import load_dotenv
from telebot import types

import services.entity as entity
from services.recipe_service import get_ingredients_from_text
from telegram_controller import text_template

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
            text=str(el.cart_order) + ': ' + str(el.ingredient_label)
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
        try:
            command = handler['filters']['commands']
            commands.extend(command)
        except:
            pass
    text_commands: List[str] = []
    for command in commands:
        text_commands.append('/' + command)
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
@wrap_logger
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
@wrap_logger
def start_recipe_creating(message: types.Message):
    """Процесс создания рецепта"""
    bot.send_message(message.chat.id, text_template.START_RECIPE_CREATING)
    bot.register_next_step_handler(  # type: ignore
        message=message, callback=create_recipe)

@wrap_logger
def create_recipe(message: types.Message):
    """Создать новый рецепт.

    Первый шаг создания рецепта.

    Название рецепта это текст из сообщения.
    """
    if message.text is not None:
        recipe_service.create_meal(message.text)
        bot.send_message(chat_id=message.chat.id,
                         text=text_template.ASK_FIRST_CREATE_INGREDIENT,
                         reply_markup=KEYBOARD_YES_NO)
        bot.register_next_step_handler(  # type: ignore
            message=message, callback=branch_create_ingredient)

    else:
        bot.send_message(chat_id=message.chat.id,
                         text='Некорректный вид сообщения')

@wrap_logger
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
            ingredients = get_ingredients_from_text(text=text, separator=':')
        except ValueError:
            bot.send_message(
                chat_id=message.chat.id,
                text=text_template.ERROR_WANT_CREATE_INGREDIENT
            )
            bot.register_next_step_handler(  # type: ignore
                message=message, callback=branch_create_ingredient)
        else:
            _create_ingredient(message=message, ingredients=ingredients)

def _create_ingredient(message: types.Message, ingredients: List[entity.Ingredient]):
    meal = recipe_service.get_last_user_meal()
    meal.add_ingredients(ingredients=ingredients)
    recipe_service.update_meal(meal=meal)
    bot.send_message(chat_id=message.chat.id,
                     text=text_template.SUCCES_CREATE_INGREDIENT,
                     reply_markup=KEYBOARD_STOP)
    bot.register_next_step_handler(  # type: ignore
        message=message, callback=loop_create_ingredient)

@wrap_logger
def loop_create_ingredient(message: types.Message):
    """Цикл по созданию ингредиентов для блюда"""
    text = str(message.text)
    if text != text_template.KEYBOARD_STOP_CREATE_INGREDIENT:
        # Добавляем ингредиент
        try:
            ingredients = get_ingredients_from_text(text)
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

@wrap_logger
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
    except KeyError:
        bot.send_message(chat_id=message.chat.id,
                         text=text_template.CANCEL_RECIPE_TO_DAY,
                         reply_markup=types.ReplyKeyboardRemove()
                         )

@wrap_logger
def get_short_recipes(meals: List[entity.Meal]):
    res = ''
    for meal in meals:
        res += meal.format_short_data()
    return res


@bot.message_handler(commands=['get_recipes'])  # type: ignore
@wrap_logger
def get_recipes(message: types.Message):
    """Получить все рецепты"""
    meals = recipe_service.get_meals()
    msg = text_template.GET_RECIPES_LIST + get_short_recipes(meals)
    bot.send_message(
        chat_id=message.chat.id,
        text=msg
    )


@bot.message_handler(commands=['get_calendar'])  # type: ignore
@wrap_logger
def get_calendar(message: types.Message):
    """Получить все рецепты"""
    msg = calendar_service.get_formatted_weekly_plan()
    bot.send_message(
        chat_id=message.chat.id,
        text=msg
    )


@bot.message_handler(commands=['add_recipe_to_day'])  # type: ignore
@wrap_logger
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

@wrap_logger
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
@wrap_logger
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
@wrap_logger
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

@wrap_logger
def take_cart_element(message: types.Message):
    """Убрать элемент из списка"""
    text = str(message.text)
    if text == text_template.KEYBOARD_BUTTON_CANCEL: # Нажал отмену
        bot.send_message(
            chat_id=message.chat.id,
            text=text_template.END_CART_PROCESS,
            reply_markup=KEYBOARD_START
        )
    elif text.find(':') != -1: # Нормальная работа
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
    else:
            bot.send_message(
                chat_id=message.chat.id,
                text=text_template.ERROR_CART_BUY,
                reply_markup=types.ReplyKeyboardRemove()
            )
@bot.message_handler(commands=['add_cart_item'])  # type: ignore
@wrap_logger
def add_cart_item_command(message: types.Message):
    """Команда на добавление ингредиента в корзину"""
    msg = text_template.ADD_CART_ITEM
    bot.send_message(
        chat_id=message.chat.id,
        text=msg,
        reply_markup=create_cart_keyboard(cart=[]) # TODO: Переделать на клавиатуру отмены
    )
    bot.register_next_step_handler(  # type: ignore
        message=message, callback=add_cart_item)

@wrap_logger
def add_cart_item(message: types.Message):
    text = str(message.text)
    cart = basket_service.get_cart()
    label, quantity = text.split(':', maxsplit=1)
    quantity = int(quantity)
    ingredient = recipe_service.create_ingredient(label=label, quantity=quantity)
    basket_service.add_ingredient_to_cart(
        cart_elements=cart, 
        ingredient=ingredient
        )
    
    bot.send_message(
    chat_id=message.chat.id,
    text=f'Успешно Добавлен ингредиент: {label, quantity}',
    reply_markup=types.ReplyKeyboardRemove()
)
    

KEYBOARD_START = create_start_keyboard()  # type: ignore