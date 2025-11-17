from typing import List
import services.entity as entity
meals: List[entity.Meal] = []
ingredients: List[entity.Ingredient] = []
quantity_types: List[entity.QuantityTypes] = [
    entity.QuantityTypes(quantity_id=0, quantity_label='гр.'),
    entity.QuantityTypes(quantity_id=1, quantity_label='шт.')
]
weekly_plan: List[entity.DailyMealPlan] = [
    entity.DailyMealPlan(entity.DayOfWeek.MONDAY, []),
    entity.DailyMealPlan(entity.DayOfWeek.TUESDAY, []),
    entity.DailyMealPlan(entity.DayOfWeek.WEDNESDAY, []),
    entity.DailyMealPlan(entity.DayOfWeek.THURSDAY, []),
    entity.DailyMealPlan(entity.DayOfWeek.FRIDAY, []),
    entity.DailyMealPlan(entity.DayOfWeek.SATURDAY, []),
    entity.DailyMealPlan(entity.DayOfWeek.SUNDAY, []),
]
cart_list: List[entity.CartElement] = []
