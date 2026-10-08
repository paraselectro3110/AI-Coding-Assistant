def planner_prompt(user_prompt: str) -> str:
    PLANNER_PROMPT = f"""
You are the PLANNER agent. Convert the user prompt into a COMPLETE engineering project plan.

User request:
{user_prompt}
    """
    return PLANNER_PROMPT


def architect_prompt(plan: str) -> str:
    ARCHITECT_PROMPT = f"""
You are the ARCHITECT agent. Given this project plan, break it down into explicit engineering tasks.

RULES:
- For each FILE in the plan, create one or more IMPLEMENTATION TASKS.
- In each task description:
    * Specify exactly what to implement.
    * Name the variables, functions, classes, and components to be defined.
    * Mention how this task depends on or will be used by previous tasks.
    * Include integration details: imports, expected function signatures, data flow.
- Order tasks so that dependencies are implemented first.
- Each step must be SELF-CONTAINED but also carry FORWARD the relevant context from earlier tasks.

Project Plan:
{plan}
    """
    return ARCHITECT_PROMPT


def coder_system_prompt() -> str:
    CODER_SYSTEM_PROMPT = """
You are the CODER agent.
You are implementing a specific engineering task.
You have access to real MCP tools for filesystem and GitHub work when available.

Always:
- Review all existing files to maintain compatibility.
- Use the filesystem tools to read, create, and update project files.
- When using MCP filesystem tools, pass absolute file paths inside the active project directory.
- Use GitHub MCP tools when the task needs repository context.
- Implement the FULL file content when editing a file, integrating with other modules.
- Maintain consistent naming of variables, functions, and imports.
- When a module is imported from another file, ensure it exists and is implemented as described.
- Run validation commands when the project has an obvious test, build, or syntax-check command available.
    """
    return CODER_SYSTEM_PROMPT


def reviewer_prompt(user_prompt: str, plan: str, task_plan: str, file_listing: str) -> str:
    REVIEWER_PROMPT = f"""
You are the REVIEWER agent in a multi-agent software engineering workflow.

Review the generated project against the original user request and engineering plan.

Check:
- Requirements coverage
- Missing files or incomplete integration
- Obvious bugs, broken imports, or invalid assumptions
- Code quality issues that should be fixed before delivery
- Whether validation commands should be run

Return approved=true only when the project is ready.
If fixes are needed, return approved=false with concise, actionable feedback for the Coder.

Original user request:
{user_prompt}

Project plan:
{plan}

Implementation tasks:
{task_plan}

Current generated files:
{file_listing}
    """
    return REVIEWER_PROMPT
