from datetime import datetime

class Context:
    def __init__(self):
        self.reset()


    def reset(self):
        self.user_ingredients = []
        self.diet = None
        self.time = None
        self.difficulty = None
        self.type_food = None
        self.last_recipes = []
        self.last_intent = None
        self.last_update = datetime.now()


    def add_ingredients(self, ingredients):
        for ingredient in ingredients:
            if ingredient not in self.user_ingredients:
                self.user_ingredients.append(ingredient)
        self.last_update = datetime.now()


    def set_diet(self, diet):
        self.diet = diet
        self.last_update = datetime.now()

    
    def set_type_food(self, type_food):
        self.type_food = type_food
        self.last_update = datetime.now()


    def set_time(self, time):
        self.time = time
        self.last_update = datetime.now()


    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.last_update = datetime.now()
    

    def set_last_intent(self, intent):
        self.last_intent = intent
        self.last_update = datetime.now()


    def add_recipes(self, recipes):
        self.last_recipes = recipes
        self.last_update = datetime.now()


    def get_context_summary(self):
        return {
            "ingredients": self.user_ingredients,
            "diet": self.diet,
            "time": self.time,
            "difficulty": self.difficulty,
            "type_food": self.type_food,
            "last_recipes": self.last_recipes
        }


    def is_expired(self, timeout_minutes=30):
        time_diff = (datetime.now() - self.last_update).total_seconds()
        return time_diff > timeout_minutes * 60