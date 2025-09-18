from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import uvicorn

from app.services.finance_service import FinanceService
from app.services.excel_service import ExcelService  # optional, included in project
from app.models.response_models import QueryResponse, HealthResponse

app = FastAPI(
    title="Autonomous Strategic Finance API",
    description="AI-powered financial modeling and forecasting",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

finance_service = FinanceService()
excel_service = ExcelService()

@app.get("/", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="healthy", message="Autonomous Finance API is running")

@app.get("/api/v1/search", response_model=QueryResponse)
async def search_financial_model(query: str = Query(..., description="Natural language query for financial modeling")):
    try:
        result = await finance_service.process_query(query)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing query: {e}")

@app.get("/api/v1/export/excel/{model_id}")
async def export_excel(model_id: str):
    model = finance_service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    try:
        excel_bytes = excel_service.generate_excel(model)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        tmp.write(excel_bytes)
        tmp.flush()
        return FileResponse(tmp.name, filename=f"financial_model_{model_id}.xlsx",
                            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating Excel: {e}")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
