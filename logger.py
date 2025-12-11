import os
from datetime import datetime
import json

class Logger():

    def __init__(self, path="logs/interactions.jsonl"):
        self.log_file = path
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)


    def log_interaction(self, user_input, bot_response, confidence, recipe_info=None):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "bot_response": bot_response,
            "confidence": float(confidence),
            "found_ingredients": list(recipe_info.get("matching_ingredients")) if recipe_info and recipe_info.get("matching_ingredients") else None,
            "found_main_ingredients": list(recipe_info.get("matching_main_ingredients")) if recipe_info and recipe_info.get("matching_main_ingredients") else None,
            "diet": recipe_info.get("diet") if recipe_info else None,
            "type_food": recipe_info.get("type_food") if recipe_info else None,
            "difficulty": recipe_info.get("difficulty") if recipe_info else None,
            "time": recipe_info.get("time") if recipe_info else None
        }

        try:
            with open(self.log_file, "a", encoding="utf-8") as file:
                file.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Error writing to log file: {e}")
    

    def get_statistics(self):
        stats = {
            "total_interactions": 0,
            "avg_confidence": 0.0,
            "most_searched_ingredients": {},
            "most_searched_diets": {}
        }

        try:
            with open(self.log_file, "r", encoding="utf-8") as file:
                total_confidence = 0.0
                for line in file:
                    stats["total_interactions"] += 1
                    entry = json.loads(line)
                    total_confidence += entry.get("confidence", 0.0)
                    for ingredient in entry.get("found_ingredients") or []:
                        if ingredient in stats["most_searched_ingredients"]:
                            stats["most_searched_ingredients"][ingredient] += 1
                        else:
                            stats["most_searched_ingredients"][ingredient] = 1
                    diets = entry.get("diet") or []
                    if isinstance(diets, str): # Handle case where diet is a single string
                        diets = [diets]
                    for diet_item in diets:
                        stats["most_searched_diets"][diet_item] = stats["most_searched_diets"].get(diet_item, 0) + 1
                
                if stats["total_interactions"] > 0:
                    stats["avg_confidence"] = total_confidence / stats["total_interactions"]
                
                if stats["most_searched_ingredients"]:
                    stats["most_searched_ingredients"] = dict(
                        sorted(stats["most_searched_ingredients"].items(),
                            key=lambda item: item[1], reverse=True)[:10]
                    )

                if stats["most_searched_diets"]:
                    stats["most_searched_diets"] = dict(
                        sorted(stats["most_searched_diets"].items(),
                            key=lambda item: item[1], reverse=True)[:3]
                    )

                return stats
        except Exception as e:
            print(f"Error reading log file: {e}")
            return None