from pydantic import BaseModel
from typing import List, Dict, Any
from app.models.finance_models import FinancialModel, RevenueDriver, MonthlyProjection

class QueryResponse(BaseModel):
    model_id: str
    revenue_drivers: List[RevenueDriver]
    monthly_projections: List[MonthlyProjection]
    excel_download_url: str
    assumptions_used: Dict[str, Any]
    business_logic: List[str]

class HealthResponse(BaseModel):
    status: str
    message: str
