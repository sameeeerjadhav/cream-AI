"""LangGraph agent with checkpointed memory and one approval gate."""

from typing import Any, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from app.agent_loop import run_agent


class AgentState(TypedDict, total=False):
    question: str
    calculator_args: dict[str, Any] | None
    approved: bool
    answer: dict[str, Any]
    status: str
    history: list[str]


def _approval_node(state: AgentState) -> AgentState:
    if state.get("calculator_args") is None:
        return {
            **state,
            "status": "approved",
            "history": [*state.get("history", []), "rag_route"],
        }
    history = [*state.get("history", []), "approval_requested"]
    if not state.get("approved", False):
        return {
            **state,
            "status": "approval_required",
            "history": history,
            "answer": {
                "mode": "calculator",
                "answer": "Approval is required before calculating the estimate.",
                "confidence": "high",
                "follow_up": "Review the inputs and resend with approved=true.",
            },
        }
    return {**state, "status": "approved", "history": [*history, "approved"]}


def _calculate_node(state: AgentState) -> AgentState:
    args = state.get("calculator_args")
    if args is None:
        answer = run_agent(state["question"])
    else:
        answer = run_agent(state["question"], calculator_args=args)
    return {
        **state,
        "answer": answer,
        "status": "completed",
        "history": [*state.get("history", []), "tool_called"],
    }


def _route_after_approval(state: AgentState) -> str:
    return "calculate" if state.get("status") == "approved" else END


_checkpointer = MemorySaver()
_builder = StateGraph(AgentState)
_builder.add_node("approval", _approval_node)
_builder.add_node("calculate", _calculate_node)
_builder.add_edge(START, "approval")
_builder.add_conditional_edges("approval", _route_after_approval)
_builder.add_edge("calculate", END)
agent_graph = _builder.compile(checkpointer=_checkpointer)


def run_graph(
    question: str,
    calculator_args: dict[str, Any] | None,
    approved: bool,
    thread_id: str,
) -> dict[str, Any]:
    """Run the graph using thread-scoped checkpointed memory."""
    state = agent_graph.invoke(
        {
            "question": question,
            "calculator_args": calculator_args,
            "approved": approved,
        },
        config={"configurable": {"thread_id": thread_id}},
    )
    return {
        "status": state.get("status", "unknown"),
        "answer": state.get("answer", {}),
        "memory": state.get("history", []),
        "thread_id": thread_id,
    }
