from typing import List, Dict, Any
from app.models.finance_models import MonthlyProjection, RevenueDriver

class FormulaEngine:
    def calculate_monthly_projections(self, months: int, assumptions: Dict[str, Any], drivers: List[RevenueDriver]):
        projections = []
        sales_people = assumptions.get("initial_sales_people", 1)
        marketing_spend = assumptions.get("marketing_spend_monthly", 200000)
        rev_large = assumptions.get("large_customer_revenue_monthly", 16667)
        rev_small = assumptions.get("small_customer_revenue_monthly", 5000)

        large_cum = 0
        small_cum = 0

        for m in range(1, months + 1):
            large_new = sales_people
            large_cum += large_new
            large_rev = large_cum * rev_large

            small_new = int(marketing_spend / 1500 * 0.45)
            small_cum += small_new
            small_rev = small_cum * rev_small

            total = large_rev + small_rev

            projections.append(MonthlyProjection(
                month=m,
                sales_people=sales_people,
                large_customers_acquired=large_new,
                large_customers_cumulative=large_cum,
                large_customer_revenue=large_rev,
                small_customers_acquired=small_new,
                small_customers_cumulative=small_cum,
                small_customer_revenue=small_rev,
                total_revenue=total,
                marketing_spend=marketing_spend
            ))

            sales_people += assumptions.get("sales_people_growth_rate", 1)

        return projections
