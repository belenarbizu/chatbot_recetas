from match_recipe import get_all_ingredients
import json

_cached_recipes = None
_cached_ingredients = None


def get_recipes_cached():
    global _cached_recipes
    
    if _cached_recipes is None:
        try:
            with open('data/recetas.json', 'r', encoding='utf-8') as file:
                _cached_recipes = json.load(file)
        except FileNotFoundError:
            print("Error: data/recetas.json no encontrado")
            return []
    
    return _cached_recipes


def get_all_ingredients_cached():
    global _cached_ingredients
    
    if _cached_ingredients is None:
        
        recipes = get_recipes_cached()
        _cached_ingredients = get_all_ingredients(recipes)
    
    return _cached_ingredients


def clear_cache():
    global _cached_recipes, _cached_ingredients
    _cached_recipes = None
    _cached_ingredients = None
