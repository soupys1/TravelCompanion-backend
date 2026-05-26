
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.search import search_tool
from rag.retriever import store_result, retrieve_context
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from agents.planner import TripState
from dotenv import load_dotenv
import os

load_dotenv()

model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)


def research_node(state : TripState):

    result = search_tool(state["destination"])
    store_result(result)
    context = retrieve_context(state["destination"])
    message = [
        SystemMessage(content= f" You are a travel reseacher, Use this context to complete your reserach :{context} "),
        HumanMessage(content=state["plan"])
    ]
    
    response = model.invoke(message)
    return {"research" : response.content }


