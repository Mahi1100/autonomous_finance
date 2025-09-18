import json
from typing import Dict, Any
import openai
from app.config.settings import get_settings

settings = get_settings()
if settings.openai_api_key:
    openai.api_key = settings.openai_api_key

class LLMService:
    def __init__(self):
        # client can use openai SDK functions directly
        self.client = openai

    async def process_natural_language_query(self, user_query: str) -> Dict[str, Any]:
        
        prompt = self._build_financial_prompt(user_query)
        try:
            # Use a completions/chat call; adapt to installed openai version
            resp = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a CFO's financial modelling assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000,
            )
            content = resp.choices[0].message.content
            # Expect LLM to return JSON — parse
            return json.loads(content)
        except Exception:
            # fallback rule-based quick parse
            return self._fallback_parsing(user_query)

    def _build_financial_prompt(self, user_query: str) -> str:
        kb_snippet = (
            "SaaS rules: two business units (large customers, small/medium). "
            "Large: direct sales $16,667/mo per customer, 1-2 customers per salesperson/month. "
            "SMB: digital marketing, default CAC $1,500, conversion 45%, avg $5,000/mo per customer. "
            "Default marketing spend $200,000/mo, sales inquiries 160/mo."
        )
        return (
            f"Analyze this financial modelling request and return ONLY valid JSON.\n\n"
            f"User Query: \"{user_query}\"\n\nContext: {kb_snippet}\n\n"
            "Return JSON with keys: time_horizon_months (int), revenue_drivers (list of {name,type,value,unit}), "
            "assumptions (dict), business_focus (list), special_instructions (list).\n\n"
            "Example:\n"
            '{"time_horizon_months":12, "revenue_drivers":[{"name":"number_of_sales_people","type":"input","value":2,"unit":"#"}], '
            '"assumptions":{"initial_sales_people":1,"marketing_spend_monthly":200000}, "business_focus":["large_customers","small_medium_customers"], "special_instructions":[] }'
        )

    def _fallback_parsing(self, user_query: str) -> Dict[str, Any]:
        # Very simple regex-based parser for quick fallback
        import re
        q = user_query.lower()
        months = 12
        m = re.search(r'(\d+)\s*month', q)
        if m:
            months = int(m.group(1))
        sales_people = 1
        m2 = re.search(r'(\d+)\s*(salespeople|sales people|salesperson)', q)
        if m2:
            sales_people = int(m2.group(1))
        # assemble basic json
        return {
            "time_horizon_months": months,
            "revenue_drivers": [
                {"name": "number_of_sales_people", "type": "input", "value": sales_people, "unit": "#"}
            ],
            "assumptions": {
                "initial_sales_people": sales_people,
                "sales_people_growth_rate": 1,
                "marketing_spend_monthly": 200000,
                "large_customer_revenue_monthly": 16667,
                "small_customer_revenue_monthly": 5000
            },
            "business_focus": ["large_customers", "small_medium_customers"],
            "special_instructions": []
        }
