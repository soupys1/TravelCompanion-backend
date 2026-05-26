
from typing import List, TypedDict
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
import json
load_dotenv()

model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

class TripState(TypedDict):
    user_input : str
    destination : str
    duration : int
    budget_range : str
    preferences : list[str]
    plan : str
    messages : list[str]
    research : str
    budget : str


def plannernode(state:TripState) :
    message = [
        SystemMessage(content="""You are a travel planner. Extract trip details from the user input and return ONLY a JSON object with no extra text, no markdown, no backticks. Use exactly these fields:
    {
        "destination": "city/country name",
        "duration": 7,
        "budget_range": "low/medium/high",
        "preferences": ["food", "temples"],
        "plan": "detailed day by day itinerary here",
        "budget" : "based on the plan distribute the budget",
    }"""),
        HumanMessage(content = state["user_input"])
    ]
    
    response = model.invoke(message)
    data = json.loads(response.content)
    return {
        "destination": data["destination"],
        "duration": data["duration"],
        "budget_range": data["budget_range"],
        "preferences": data["preferences"],
        "plan": data["plan"],
        "budget":data["budget"],
    }



