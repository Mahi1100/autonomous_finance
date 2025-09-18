import io
import pandas as pd
from app.models.finance_models import FinancialModel

class ExcelService:
    def generate_excel(self, model: FinancialModel) -> bytes:
        output = io.BytesIO()
        df = pd.DataFrame([p.dict() for p in model.monthly_projections])
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Forecast", index=False)
            pd.DataFrame([model.assumptions]).to_excel(writer, sheet_name="Assumptions", index=False)
        output.seek(0)
        return output.read()
