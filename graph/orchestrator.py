from langgraph.graph import StateGraph, START, END
from agents.planner import TripState, plannernode
from agents.research import research_node
from agents.budget import budget_node

def parallel_node(state: TripState):
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        research_future = executor.submit(research_node, state)
        budget_future   = executor.submit(budget_node, state)
        
        try:
            research_result = research_future.result()
        except Exception as e:
            print("RESEARCH FAILED:", e)
            research_result = {"research": "Research unavailable."}
        
        try:
            budget_result = budget_future.result()
        except Exception as e:
            print("BUDGET FAILED:", e)
            budget_result = {"budget": "Budget unavailable."}
            
    return {**research_result, **budget_result}

graph = StateGraph(TripState)
graph.add_node("plannernode", plannernode)
graph.add_node("parallel_node", parallel_node)
graph.add_edge(START, "plannernode")
graph.add_edge("plannernode", "parallel_node")
graph.add_edge("parallel_node", END)
graph = graph.compile()