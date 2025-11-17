from typing import List
import services.entity as entity
import fake_database


def insert_cart(cart: List[entity.CartElement]):
    fake_database.cart_list = cart


def get_cart() -> List[entity.CartElement]:
    cart_copy: List[entity.CartElement] = []
    for el in fake_database.cart_list:
        if el.is_ingredient_bought == False:
            cart_copy.append(el)

    return cart_copy


def update_item_bought(item_id: int) -> bool:
    for el in fake_database.cart_list:
        if el.cart_id == item_id:
            el.is_ingredient_bought = True
            return True
    return False
