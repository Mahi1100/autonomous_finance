from typing import Dict, Any
from app.services.llm_service import LLMService
from app.models.finance_models import FinancialModel, RevenueDriver, BusinessUnit
from app.utils.knowledge_base import KnowledgeBase
from app.utils.formula_engine import FormulaEngine
from app.models.response_models import QueryResponse

class FinanceService:
    def __init__(self):
        self.llm_service = LLMService()
        self.knowledge_base = KnowledgeBase()
        self.formula_engine = FormulaEngine()
        self.models_cache: Dict[str, FinancialModel] = {}

    async def process_query(self, user_query: str) -> QueryResponse:
        llm_result = await self.llm_service.process_natural_language_query(user_query)

        model = self._create_financial_model(user_query, llm_result)

        months = int(llm_result.get("time_horizon_months", 12))
        model.calculate_projections(months)

        self.models_cache[model.model_id] = model

        excel_url = f"/api/v1/export/excel/{model.model_id}"
        return QueryResponse(
            model_id=model.model_id,
            revenue_drivers=model.revenue_drivers,
            monthly_projections=model.monthly_projections,
            excel_download_url=excel_url,
            assumptions_used=model.assumptions,
            business_logic=self._get_business_logic_explanation(model)
        )

    def _create_financial_model(self, query: str, llm_response: Dict[str, Any]) -> FinancialModel:
        model = FinancialModel(query=query)
        model.assumptions = llm_response.get("assumptions", {})
        for d in llm_response.get("revenue_drivers", []):
            driver = RevenueDriver(**d)
            model.revenue_drivers.append(driver)
        kb = self.knowledge_base.get_saas_rules()
        for unit_name, unit_data in kb.get("business_units", {}).items():
            model.business_units[unit_name] = BusinessUnit(
                name=unit_name,
                go_to_market_strategy=unit_data.get("go_to_market", ""),
                assumptions=unit_data.get("assumptions", {}),
                revenue_formulas=list(unit_data.get("formulas", {}).values())
            )
        return model

    def get_model(self, model_id: str) -> FinancialModel | None:
        return self.models_cache.get(model_id)

    def get_available_revenue_drivers(self):
        kb = self.knowledge_base.get_saas_rules()
        return kb.get("revenue_drivers", [])

    def _get_business_logic_explanation(self, model: FinancialModel):
        logic = []
        if "large_customers" in model.business_units:
            logic.append("Large Customers: Direct sales approach with sales team growing monthly")
            logic.append("Each salesperson can acquire 1-2 large customers per month at $16,667/month revenue")
        if "small_medium_customers" in model.business_units:
            logic.append("Small/Medium Customers: Digital marketing with $200k monthly spend")
            logic.append("$1,500 CAC with 45% demo-to-customer conversion rate at $5,000/month revenue")
        return logic
