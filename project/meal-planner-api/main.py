from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
import json
import os

app = FastAPI(title="Meal Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Gemini Client (Graceful mock fallback if no API key is present)
try:
    if os.environ.get("GEMINI_API_KEY"):
        client = genai.Client()
    else:
        client = None
except Exception:
    client = None

class Preferences(BaseModel):
    dietary: list[str]
    cook_days: int
    cook_hours_per_day: float

@app.get("/")
def read_root():
    return {"message": "Meal Planner API running successfully"}

@app.post("/api/preferences")
def update_preferences(prefs: Preferences):
    return {"status": "success", "data": prefs}

@app.post("/api/upload-receipt")
async def upload_receipt(receipt: UploadFile = File(...)):
    contents = await receipt.read()
    
    if not client:
        # Fallback Mock if no Gemini API Key is available in the environment
        return {
            "status": "mock",
            "items": [
                {"name": "Whole Milk 1L", "quantity": "1"},
                {"name": "Free Range Eggs 12pk", "quantity": "1"},
                {"name": "Artisan Sourdough Bread", "quantity": "1"},
                {"name": "Roma Tomatoes", "quantity": "4"},
                {"name": "Hass Avocado", "quantity": "2"}
            ]
        }

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                "Analyze this supermarket receipt and extract all food items. Return the output as valid JSON in this exact format: {\"items\": [{\"name\": \"Item Name\", \"quantity\": \"Quantity String\"}]}. Do not include markdown code block formatting, just the raw JSON object.",
                {'mime_type': receipt.content_type or 'image/jpeg', 'data': contents}
            ]
        )
        text_resp = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text_resp)
        return {"status": "success", "items": data.get("items", [])}
    except Exception as e:
        print("Gemini Parsing Error:", e)
        raise HTTPException(status_code=500, detail=str(e))

class PlanRequest(BaseModel):
    inventory: list[dict]
    preferences: dict

@app.post("/api/generate-plan")
def generate_plan(payload: PlanRequest):
    if not client:
        return {
            "status": "mock",
            "plan": [
                {"day": "Monday", "meal": "Avocado Toast with Eggs", "time": "15 min"},
                {"day": "Tuesday", "meal": "Sourdough Grilled Cheese & Tomato Soup", "time": "25 min"}
            ]
        }
    
    prompt = f"""
    You are an AI meal planning agent.
    Based on the following inventory: {payload.inventory}
    And the following user and time preferences: {payload.preferences}
    Generate a meal plan. Optimize for using the available ingredients and strict adherence to the time constraints. 
    Return the schedule as JSON only in this exact format:
    {{"plan": [{{"day": "String", "meal": "Meal name and description", "time": "Estimated prep/cook time in min"}}]}}
    Do not use markdown blocks.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        text_resp = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(text_resp)
        return {"status": "success", "plan": data.get("plan", [])}
    except Exception as e:
        print("Gemini Generate Error:", e)
        raise HTTPException(status_code=500, detail=str(e))
