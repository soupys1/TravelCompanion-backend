from fastapi import FastAPI, status, HTTPException
from fastapi import WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from dotenv import load_dotenv
from tools.search import search_tool
import graph.orchestrator as graph
import asyncio
import uvicorn
import os

load_dotenv()

model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
executor = ThreadPoolExecutor(max_workers=4)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://travel-companion-frontend-sandy.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TripRequest(BaseModel):
    user_input: str


# ── Keep-warm ping (hit this with UptimeRobot every 5 min) ──────────────────
@app.get("/ping")
def ping():
    return {"status": "ok"}


# ── Root ────────────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "message": "Travel Companion API"}


# ── Health ──────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    groq_key   = os.getenv("GROQ_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    if groq_key and tavily_key:
        return {
            "status": "ok",
            "message": "API is healthy",
            "timestamp": datetime.now().isoformat(),
        }
    raise HTTPException(status_code=503, detail="Missing API keys")


# ── Plan (async + thread executor so it never blocks the server) ─────────────
@app.post("/plan", status_code=status.HTTP_200_OK)
async def plan_trip(request: TripRequest):
    try:
        loop   = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            executor,
            graph.graph.invoke,
            {"user_input": request.user_input},
        )
        return {
            "plan":     result["plan"],
            "research": result["research"],
            "budget":   result["budget"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── WebSocket live stream ────────────────────────────────────────────────────
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        messages = [
            SystemMessage(content="You are a travel planner. Help the user plan the perfect trip."),
            HumanMessage(content=data),
        ]
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            executor,
            lambda: list(model.stream(messages)),
        )
        for chunk in response:
            await websocket.send_text(chunk.content)
        await websocket.send_text("[DONE]")
    except Exception as e:
        await websocket.send_text(f"ERROR: {str(e)}")


# ── Destinations ─────────────────────────────────────────────────────────────
@app.get("/destinations")
async def destinations():
    try:
        loop    = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            executor,
            search_tool,
            "top travel destinations in the world 2025",
        )
        return {"destinations": results["results"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)