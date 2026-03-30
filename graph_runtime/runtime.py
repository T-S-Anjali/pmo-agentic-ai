"""
Graph Runtime — FastAPI Service Wrapper.
"""
from fastapi import FastAPI
from graph_runtime.graph import get_graph
from graph_runtime.state import PMOGraphState

app = FastAPI(title="PMO Graph Runtime")

# Initialize the default charter graph for the thin-slice
workflow = get_graph("project_intake_to_charter")

@app.get("/health")
def health():
    return {"status": "ok", "service": "graph-runtime"}

@app.post("/invoke")
async def invoke_graph(state: PMOGraphState):
    # This is a thin wrapper to invoke the compiled graph
    # For MVP, we'll just run it synchronously or via a task
    config = {"configurable": {"thread_id": state.get("workflow_id", "default")}}
    result = await workflow.ainvoke(state, config)
    return result
