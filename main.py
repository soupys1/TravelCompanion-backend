from fastapi import FastAPI, status, HTTPException
import uvicorn , os
import graph.orchestrator as graph
from datetime import datetime
from pydantic import BaseModel
from fastapi import WebSocket
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from fastapi.middleware.cors import CORSMiddleware
from dotenv import dotenv_values
from tools.search import search_tool

model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)



app = FastAPI()

origins = [ "http://localhost",
    "http://localhost:3000","https://travel-companion-frontend-sandy.vercel.app/"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TripRequest(BaseModel):
    user_input : str
   
@app.get("/")
def root():
    return {"status" : "ok" , "message" : "Travel Companion API"}

@app.get("/health")
def health():
    api_groq = os.getenv("GROQ_API_KEY")
    api_tavil = os.getenv("TAVILY_API_KEY")
    if api_groq and api_tavil:
        return {"status": "ok", "message": "API is healthy", "timestamp": datetime.now().isoformat()}
    else:
        raise HTTPException(status_code=404, detail="Plan was not generated ")
        
@app.post("/plan", status_code=status.HTTP_200_OK)
def plan_trip(request : TripRequest):
    try:

        result = graph.graph.invoke({"user_input" : request.user_input})
        return {"plan" : result["plan"] , "research" : result["research"], "budget" : result["budget"]}
    except:
        raise HTTPException(status_code=404, detail="Plan was not generated ")
        
@app.websocket("/ws")
async def websocket_endpoint(websocket : WebSocket):
    try:

        await websocket.accept()
        data = await websocket.receive_text()
        message = [
            SystemMessage(content="You are a travel planner.You will be helping the user plan and execute the perfect travel"),
            HumanMessage(content = data)
        ]
        response  = model.stream(message)
        for res in response:
            await websocket.send_text(res.content)
        await websocket.send_text("[DONE]")
    except Exception as e:
        await websocket.send_text(f"ERROR: {str(e)}")

@app.get("/destinations")
def destinations():
    results = search_tool("top travel destinations in the world 2025")
    return {"destinations" : results["results"]}

port = 8000

if __name__ == "__main__":
    uvicorn.run("main:app", port = port, log_level="info", reload=True)

