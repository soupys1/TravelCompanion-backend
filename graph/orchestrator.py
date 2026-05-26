from langgraph.graph import StateGraph, START, END
from agents.planner import TripState, plannernode
from agents.research import research_node

graph = StateGraph(TripState)

graph.add_node("plannernode", plannernode)
graph.add_node("researchnode" , research_node)

graph.add_edge(START, "plannernode")
graph.add_edge("plannernode","researchnode")
graph.add_edge( "researchnode", END)

graph = graph.compile()
