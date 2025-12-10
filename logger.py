import os
from datetime import datetime
import json

class Logger():

    def __init__(self, path="logs/interactions.jsonl"):
        self.log_file = path
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)


    def log_interaction(self, user_input, bot_response, confidence):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "bot_response": bot_response,
            "confidence": float(confidence)
        }

        try:
            with open(self.log_file, "a", encoding="utf-8") as file:
                file.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Error writing to log file: {e}")
    

    def get_statistics(self):
        stats = {
            "total_interactions": 0,
            "avg_confidence": 0.0
        }

        try:
            with open(self.log_file, "r", encoding="utf-8") as file:
                total_confidence = 0.0
                for line in file:
                    stats["total_interactions"] += 1
                    entry = json.loads(line)
                    total_confidence += entry.get("confidence", 0.0)
                
                if stats["total_interactions"] > 0:
                    stats["avg_confidence"] = total_confidence / stats["total_interactions"]
                
                return stats
        except Exception as e:
            print(f"Error reading log file: {e}")
            return None