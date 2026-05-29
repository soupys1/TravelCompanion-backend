import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.planner import TripState
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

def budget_node(state: TripState):
    budgetrange = state["budget_range"]
    

    message = [
    SystemMessage(content=f"""You are a travel budget expert. Based on budget range '{budgetrange}' and the research provided, create a detailed cost breakdown as plain readable text. 
    
    Include specific dollar amounts for:
    - Flights
    - Accommodation (per night and total)
    - Food (per day and total)  
    - Local transport
    - Activities and entrance fees
    - Total estimated cost

    Do NOT return JSON. Return plain text only."""),
        HumanMessage(content=state["plan"])
    ]

    response = model.invoke(message)
    return {"budget": response.content}