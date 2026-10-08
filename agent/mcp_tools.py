import os

from agent.tools import get_current_directory, get_project_root, list_files, read_file, run_cmd, write_file


LOCAL_FALLBACK_TOOLS = [read_file, write_file, list_files, get_current_directory, run_cmd]
_CACHED_CODER_TOOLS = {}


def _mcp_server_config(include_github: bool = True) -> dict:
    """Build MCP server config for the generated project workspace."""
    project_root = get_project_root().resolve()
    servers = {
        "filesystem": {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-filesystem",
                str(project_root),
            ],
            "transport": "stdio",
        }
    }

    github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN") or os.getenv("GITHUB_PAT")
    if include_github and github_token:
        servers["github"] = {
            "command": "docker",
            "args": [
                "run",
                "-i",
                "--rm",
                "-e",
                "GITHUB_PERSONAL_ACCESS_TOKEN",
                "ghcr.io/github/github-mcp-server",
            ],
            "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": github_token},
            "transport": "stdio",
        }

    return servers


async def _load_mcp_tools_async(include_github: bool = True):
    from langchain_mcp_adapters.client import MultiServerMCPClient

    get_project_root().mkdir(parents=True, exist_ok=True)
    tools = []
    for name, config in _mcp_server_config(include_github=include_github).items():
        try:
            client = MultiServerMCPClient({name: config}, tool_name_prefix=True)
            tools.extend(await client.get_tools())
        except Exception as exc:
            print(f"[MCP] Skipping {name} server because startup failed: {exc}")

    if not tools:
        raise RuntimeError("No MCP servers started successfully.")

    return tools


async def load_coder_tools(include_github: bool = True) -> tuple:
    """Load real MCP tools, falling back to local tools if server startup fails."""
    global _CACHED_CODER_TOOLS
    cache_key = (str(get_project_root().resolve()), include_github)
    if cache_key in _CACHED_CODER_TOOLS:
        return _CACHED_CODER_TOOLS[cache_key]

    try:
        _CACHED_CODER_TOOLS[cache_key] = tuple(await _load_mcp_tools_async(include_github=include_github))
    except Exception as exc:
        print(f"[MCP] Falling back to local tools because MCP startup failed: {exc}")
        _CACHED_CODER_TOOLS[cache_key] = tuple(LOCAL_FALLBACK_TOOLS)

    return _CACHED_CODER_TOOLS[cache_key]


def reset_coder_tools_cache() -> None:
    """Forces MCP tools to reload after the project root changes."""
    global _CACHED_CODER_TOOLS
    _CACHED_CODER_TOOLS = {}
