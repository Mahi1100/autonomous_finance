import json
import os

class KnowledgeBase:
    def __init__(self, path: str = "data/knowledge_base.json"):
        self.path = path
        self.data = {}
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                self.data = json.load(f)

    def get_saas_rules(self):
        return self.data.get("saas_company", {})
