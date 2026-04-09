from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import json
import os
from typing import List

app = FastAPI()

# Allow frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "sales_data.csv"

class RecordUpdate(BaseModel):
    Year: int
    Month: str
    Revenue: int
    Expenses: int
    Quick_Ratio: float

def train_and_predict(df_full, year_selected):
    """
    Fits simple linear regression models to predict next month's metrics based on previous data.
    """
    # For prediction, we use the entire history up to the current selection to be more 'AI-like'
    # but for simplicity, we'll just predict the next month of the selected year's trend
    df_trend = df_full[df_full['Year'] <= year_selected].copy()
    df_trend['Month_Index'] = range(1, len(df_trend) + 1)
    
    X = df_trend[['Month_Index']].values
    predictions = {}
    
    for col in ['Revenue', 'Expenses', 'Net_Profit']:
        y = df_trend[col].values
        model = LinearRegression()
        model.fit(X, y)
        # Predict for the next month after the current dataset
        next_month_val = model.predict([[len(df_trend) + 1]])[0]
        predictions[col] = float(next_month_val)
        
    return predictions

@app.get("/api/data")
def get_dashboard_data(year: int = Query(2024)):
    if not os.path.exists(DATA_FILE):
        return {"error": "Data file not found"}
        
    df_full = pd.read_csv(DATA_FILE)
    
    # Available years for the dropdown
    available_years = sorted(df_full['Year'].unique().tolist(), reverse=True)
    
    # Filter for selected year
    df_year = df_full[df_full['Year'] == year].copy()
    
    if df_year.empty:
        return {"error": f"No data for year {year}", "available_years": available_years}

    # Generate ML Prediction
    predictions = train_and_predict(df_full, year)
    
    # Dynamic targets based on year average
    avg_revenue = df_year['Revenue'].mean()
    total_revenue_target = int(avg_revenue * 12.5) # 5% more than average year
    total_gross_profit_target = int(df_year['Gross_Profit'].mean() * 12.5)
    
    current_revenue = float(df_year['Revenue'].sum())
    current_gross_profit = float(df_year['Gross_Profit'].sum())
    
    return {
        "monthly_data": json.loads(df_year.to_json(orient='records')),
        "available_years": available_years,
        "kpi": {
            "total_revenue": current_revenue,
            "total_gross_profit": current_gross_profit,
            "total_ebit": float(df_year['Gross_Profit'].sum() * 0.75), 
            "total_net_profit": float(df_year['Net_Profit'].sum()),
            "total_expenses": float(df_year['Expenses'].sum()),
        },
        "targets": {
            "revenue_target": total_revenue_target,
            "gross_profit_target": total_gross_profit_target,
            "revenue_percentage": round((current_revenue / total_revenue_target) * 100, 1),
            "gross_profit_percentage": round((current_gross_profit / total_gross_profit_target) * 100, 1)
        },
        "ml_predictions": predictions
    }

@app.post("/api/update")
def update_data(record: RecordUpdate):
    if not os.path.exists(DATA_FILE):
        return {"error": "Data file not found"}
    
    df = pd.read_csv(DATA_FILE)
    
    # Find the row and update
    mask = (df['Year'] == record.Year) & (df['Month'] == record.Month)
    if not mask.any():
        return {"error": "Record not found"}
    
    df.loc[mask, 'Revenue'] = record.Revenue
    df.loc[mask, 'Expenses'] = record.Expenses
    df.loc[mask, 'Gross_Profit'] = record.Revenue - record.Expenses
    df.loc[mask, 'Net_Profit'] = int((record.Revenue - record.Expenses) * 0.6)
    df.loc[mask, 'Quick_Ratio'] = record.Quick_Ratio
    df.loc[mask, 'Current_Ratio'] = record.Quick_Ratio + 0.2
    
    df.to_csv(DATA_FILE, index=False)
    return {"message": "Data updated successfully", "year": record.Year}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
