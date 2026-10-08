from dotenv import load_dotenv
from langchain_core.globals import set_verbose, set_debug
from langchain_groq.chat_models import ChatGroq
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent

from agent.mcp_tools import load_coder_tools, reset_coder_tools_cache
from agent.prompts import *
from agent.states import *
from agent.tools import get_current_directory, list_files, read_file, set_project_root

_ = load_dotenv()

set_debug(False)
set_verbose(False)

llm = ChatGroq(model="openai/gpt-oss-120b")


def should_use_github_tools(state: dict) -> bool:
    """Keeps large GitHub MCP schemas out of local-only coding prompts."""
    text = " ".join(
        str(state.get(key, ""))
        for key in ("user_prompt", "review_feedback")
    ).lower()
    github_terms = ("github", "repository", "repo", "pull request", "issue", "branch", "commit")
    return any(term in text for term in github_terms)


def project_snapshot(max_chars_per_file: int = 4000) -> str:
    """Returns a compact file listing with content for reviewer context."""
    file_listing = list_files.run(".")
    if file_listing == "No files found." or file_listing.startswith("ERROR:"):
        return file_listing

    sections = []
    for filepath in file_listing.splitlines():
        content = read_file.run(filepath)
        if len(content) > max_chars_per_file:
            content = content[:max_chars_per_file] + "\n...[truncated]"
        sections.append(f"--- {filepath} ---\n{content}")
    return "\n\n".join(sections)


def planner_agent(state: dict) -> dict:
    """Converts user prompt into a structured Plan."""
    user_prompt = state["user_prompt"]
    resp = llm.with_structured_output(Plan).invoke(
        planner_prompt(user_prompt)
    )
    if resp is None:
        raise ValueError("Planner did not return a valid response.")
    return {**state, "plan": resp}


def architect_agent(state: dict) -> dict:
    """Creates TaskPlan from Plan."""
    plan: Plan = state["plan"]
    project_directory = set_project_root(plan.name)
    reset_coder_tools_cache()
    resp = llm.with_structured_output(TaskPlan).invoke(
        architect_prompt(plan=plan.model_dump_json())
    )
    if resp is None:
        raise ValueError("Planner did not return a valid response.")

    resp.plan = plan
    return {**state, "task_plan": resp, "project_directory": project_directory}


async def coder_agent(state: dict) -> dict:
    """LangGraph tool-using coder agent."""
    coder_tools = list(await load_coder_tools(include_github=should_use_github_tools(state)))
    react_agent = create_react_agent(llm, coder_tools)

    if state.get("needs_revision"):
        feedback = state.get("review_feedback", "")
        files = list_files.run(".")
        project_directory = get_current_directory.run({})
        user_prompt = (
            "The reviewer requested fixes.\n"
            f"Project directory: {project_directory}\n"
            f"Review feedback:\n{feedback}\n\n"
            f"Current files:\n{files}\n\n"
            "Inspect the relevant files, apply the requested fixes, and run validation if possible. "
            "When using MCP filesystem tools, write files with absolute paths inside the project directory."
        )
        await react_agent.ainvoke({"messages": [{"role": "system", "content": coder_system_prompt()},
                                                {"role": "user", "content": user_prompt}]},
                                  {"recursion_limit": 12})
        return {**state, "needs_revision": False, "status": "CODE_READY"}

    coder_state: CoderState = state.get("coder_state")
    if coder_state is None:
        coder_state = CoderState(task_plan=state["task_plan"], current_step_idx=0)

    steps = coder_state.task_plan.implementation_steps
    if coder_state.current_step_idx >= len(steps):
        return {**state, "coder_state": coder_state, "status": "CODE_READY"}

    current_task = steps[coder_state.current_step_idx]
    existing_content = read_file.run(current_task.filepath)
    project_directory = get_current_directory.run({})

    system_prompt = coder_system_prompt()
    user_prompt = (
        f"Task: {current_task.task_description}\n"
        f"File: {current_task.filepath}\n"
        f"Project directory: {project_directory}\n"
        f"Absolute file path to write: {project_directory}\\{current_task.filepath}\n"
        f"Existing content:\n{existing_content}\n"
        "Use the available filesystem tools to save your changes. "
        "When using MCP filesystem tools, use the absolute file path above."
    )

    await react_agent.ainvoke({"messages": [{"role": "system", "content": system_prompt},
                                            {"role": "user", "content": user_prompt}]},
                              {"recursion_limit": 12})

    coder_state.current_step_idx += 1
    return {**state, "coder_state": coder_state}


def reviewer_agent(state: dict) -> dict:
    """Reviews the generated project and requests repair passes when needed."""
    review_iteration = state.get("review_iteration", 0)
    max_review_iterations = state.get("max_review_iterations", 2)
    files = project_snapshot()
    resp = llm.with_structured_output(ReviewResult).invoke(
        reviewer_prompt(
            user_prompt=state["user_prompt"],
            plan=state["plan"].model_dump_json(),
            task_plan=state["task_plan"].model_dump_json(),
            file_listing=files,
        )
    )
    if resp is None:
        raise ValueError("Reviewer did not return a valid response.")

    if resp.approved or review_iteration >= max_review_iterations:
        return {
            **state,
            "approved": resp.approved,
            "review_feedback": resp.feedback,
            "status": "DONE",
        }

    return {
        **state,
        "approved": False,
        "needs_revision": True,
        "review_feedback": resp.feedback,
        "review_iteration": review_iteration + 1,
        "status": "NEEDS_REVISION",
    }


graph = StateGraph(dict)

graph.add_node("planner", planner_agent)
graph.add_node("architect", architect_agent)
graph.add_node("coder", coder_agent)
graph.add_node("reviewer", reviewer_agent)

graph.add_edge("planner", "architect")
graph.add_edge("architect", "coder")
graph.add_conditional_edges(
    "coder",
    lambda s: "reviewer" if s.get("status") == "CODE_READY" else "coder",
    {"reviewer": "reviewer", "coder": "coder"}
)
graph.add_conditional_edges(
    "reviewer",
    lambda s: "END" if s.get("status") == "DONE" else "coder",
    {"END": END, "coder": "coder"}
)

graph.set_entry_point("planner")
agent = graph.compile()
if __name__ == "__main__":
    import asyncio

    result = asyncio.run(agent.ainvoke({"user_prompt": "Build a colourful modern todo app in html css and js"},
                                       {"recursion_limit": 100}))
    print("Final State:", result)
