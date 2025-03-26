from fastapi import FastAPI
from backend.app.api.routes import router # Import the router

# create fastapi app instance
app = FastAPI(title = "DiagnoAI API" , version="1.0.0")

# Register API routes
app.include_router(router)

# Root endpoint
@app.get("/")   
async def root():
    return {"message": "Welcome to DiagnoAI API!"}

# Run the server with uvicorn on port 8000 : uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# for test api , you can enter curl command , curl -X 'POST' \  'http://127.0.0.1:8000/chat' \  -H 'Content-Type: application/json' \  -d '{    "user_id": "223456",    "query": "I feel unwell"}'
