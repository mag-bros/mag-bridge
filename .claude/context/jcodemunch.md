# jCodeMunch MCP

jCodeMunch MCP is a Model Context Protocol (MCP) server that dramatically reduces AI agent token consumption when exploring codebases. Instead of dumping entire files into context windows, jCodeMunch indexes repositories once using tree-sitter AST parsing and allows agents to retrieve only the exact symbols they need — functions, classes, methods, and constants — with byte-level precision. This structured retrieval approach can reduce token costs by up to 99% compared to brute-force file reading.

The server supports 13+ programming languages including Python, JavaScript, TypeScript, Go, Rust, Java, PHP, C/C++, C#, Dart, Elixir, and Ruby. It works with any MCP-compatible client (Claude Desktop, Claude Code, VS Code, Cursor, Google Antigravity) and stores indexes locally at `~/.code-index/`. Every tool response includes a `_meta` envelope with timing, token savings, and cost avoided metrics to help track efficiency gains.

## Installation

### Install via pip

```bash
pip install jcodemunch-mcp

# Verify installation
jcodemunch-mcp --help
```

### Configure Claude Code

```bash
# Add to user scope (available in all projects)
claude mcp add jcodemunch uvx jcodemunch-mcp

# Or add to specific project only
claude mcp add --scope project jcodemunch uvx jcodemunch-mcp

# With optional environment variables
claude mcp add jcodemunch uvx jcodemunch-mcp \
  -e GITHUB_TOKEN=ghp_... \
  -e ANTHROPIC_API_KEY=sk-ant-...
```

### Configure Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "jcodemunch": {
      "command": "uvx",
      "args": ["jcodemunch-mcp"],
      "env": {
        "GITHUB_TOKEN": "ghp_...",
        "ANTHROPIC_API_KEY": "sk-ant-..."
      }
    }
  }
}
```

Config file locations:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

## index_repo

Indexes a GitHub repository by fetching files via the GitHub API, parsing ASTs with tree-sitter, extracting symbols, generating AI summaries (optional), and saving the index locally. Supports incremental indexing to only re-parse changed files on subsequent calls.

```json
// Index a public repository
{
  "url": "fastapi/fastapi",
  "use_ai_summaries": true,
  "incremental": true
}

// Response
{
  "success": true,
  "repo": "fastapi/fastapi",
  "indexed_at": "2024-01-15T10:30:00Z",
  "file_count": 245,
  "symbol_count": 1847,
  "languages": {"python": 230, "typescript": 15},
  "files": ["fastapi/__init__.py", "fastapi/applications.py", "..."],
  "_meta": {
    "timing_ms": 4523.2,
    "powered_by": "jcodemunch-mcp by jgravelle"
  }
}
```

## index_folder

Indexes a local folder with full security filtering including path traversal prevention, symlink escape protection, secret detection, and binary filtering. Respects `.gitignore` patterns and supports additional custom ignore patterns.

```json
// Index a local project
{
  "path": "/home/user/myproject",
  "use_ai_summaries": true,
  "extra_ignore_patterns": ["*.generated.*", "coverage/"],
  "follow_symlinks": false,
  "incremental": true
}

// Response
{
  "success": true,
  "repo": "local/myproject-a1b2c3d4",
  "folder_path": "/home/user/myproject",
  "indexed_at": "2024-01-15T10:35:00Z",
  "file_count": 156,
  "symbol_count": 892,
  "languages": {"python": 120, "javascript": 36},
  "discovery_skip_counts": {
    "gitignore": 45,
    "skip_pattern": 12,
    "secret": 2,
    "wrong_extension": 89
  },
  "_meta": {
    "timing_ms": 2341.5
  }
}
```

## list_repos

Lists all indexed repositories with symbol counts, file counts, languages, and index metadata. Local folder indexes include `display_name` and `source_root` for identification.

```json
// Request (no parameters required)
{}

// Response
{
  "repositories": [
    {
      "repo": "fastapi/fastapi",
      "indexed_at": "2024-01-15T10:30:00Z",
      "file_count": 245,
      "symbol_count": 1847,
      "languages": {"python": 230, "typescript": 15}
    },
    {
      "repo": "local/myproject-a1b2c3d4",
      "display_name": "myproject",
      "source_root": "/home/user/myproject",
      "indexed_at": "2024-01-15T10:35:00Z",
      "file_count": 156,
      "symbol_count": 892,
      "languages": {"python": 120, "javascript": 36}
    }
  ],
  "_meta": {"timing_ms": 12.3}
}
```

## get_repo_outline

Returns a high-level overview of an indexed repository including top-level directories, file counts, language breakdown, and symbol kind distribution. Lighter than `get_file_tree` for initial exploration.

```json
// Request
{
  "repo": "fastapi/fastapi"
}

// Response
{
  "repo": "fastapi/fastapi",
  "indexed_at": "2024-01-15T10:30:00Z",
  "file_count": 245,
  "symbol_count": 1847,
  "languages": {"python": 230, "typescript": 15},
  "directories": {
    "fastapi/": 89,
    "tests/": 120,
    "docs_src/": 36
  },
  "symbol_kinds": {
    "function": 523,
    "class": 89,
    "method": 1012,
    "constant": 156,
    "type": 67
  },
  "_meta": {
    "timing_ms": 8.2,
    "tokens_saved": 48153,
    "total_tokens_saved": 1280837,
    "cost_avoided": {"claude_opus": 1.20, "gpt5_latest": 0.48}
  }
}
```

## get_file_tree

Returns a hierarchical file tree with per-file language and symbol count annotations. Optionally filter by path prefix and include file-level summaries.

```json
// Request
{
  "repo": "fastapi/fastapi",
  "path_prefix": "fastapi/",
  "include_summaries": false
}

// Response
{
  "repo": "fastapi/fastapi",
  "path_prefix": "fastapi/",
  "tree": [
    {
      "path": "fastapi/__init__.py",
      "type": "file",
      "language": "python",
      "symbol_count": 12
    },
    {
      "path": "fastapi/routing/",
      "type": "dir",
      "children": [
        {
          "path": "fastapi/routing/__init__.py",
          "type": "file",
          "language": "python",
          "symbol_count": 8
        },
        {
          "path": "fastapi/routing/router.py",
          "type": "file",
          "language": "python",
          "symbol_count": 45
        }
      ]
    }
  ],
  "_meta": {
    "timing_ms": 15.4,
    "file_count": 89,
    "tokens_saved": 12500
  }
}
```

## get_file_outline

Returns all symbols in a file with hierarchical structure (classes contain their methods), signatures, and summaries. Use to understand a file's API surface before retrieving full source code.

```json
// Request
{
  "repo": "fastapi/fastapi",
  "file_path": "fastapi/applications.py"
}

// Response
{
  "repo": "fastapi/fastapi",
  "file": "fastapi/applications.py",
  "language": "python",
  "file_summary": "Core FastAPI application class and routing configuration",
  "symbols": [
    {
      "id": "fastapi/applications.py::FastAPI#class",
      "kind": "class",
      "name": "FastAPI",
      "signature": "class FastAPI(Starlette)",
      "summary": "Main application class for creating FastAPI web applications",
      "line": 45,
      "children": [
        {
          "id": "fastapi/applications.py::FastAPI.__init__#method",
          "kind": "method",
          "name": "__init__",
          "signature": "def __init__(self, *, debug: bool = False, routes: List[BaseRoute] = None, ...)",
          "summary": "Initialize FastAPI application with configuration options",
          "line": 67
        },
        {
          "id": "fastapi/applications.py::FastAPI.add_api_route#method",
          "kind": "method",
          "name": "add_api_route",
          "signature": "def add_api_route(self, path: str, endpoint: Callable, **kwargs)",
          "summary": "Add an API route to the application",
          "line": 120
        }
      ]
    }
  ],
  "_meta": {
    "timing_ms": 5.2,
    "symbol_count": 23,
    "tokens_saved": 3840,
    "total_tokens_saved": 1284677
  }
}
```

## search_symbols

Search for symbols across the entire repository with weighted scoring across name, signature, summary, keywords, and docstring. Filter by kind, language, and file pattern.

```json
// Request
{
  "repo": "fastapi/fastapi",
  "query": "authenticate",
  "kind": "function",
  "language": "python",
  "file_pattern": "fastapi/**/*.py",
  "max_results": 10
}

// Response
{
  "repo": "fastapi/fastapi",
  "query": "authenticate",
  "result_count": 3,
  "results": [
    {
      "id": "fastapi/security/oauth2.py::authenticate_user#function",
      "kind": "function",
      "name": "authenticate_user",
      "file": "fastapi/security/oauth2.py",
      "line": 89,
      "signature": "def authenticate_user(db: Session, username: str, password: str) -> Optional[User]",
      "summary": "Authenticate a user by username and password",
      "score": 28
    },
    {
      "id": "fastapi/security/api_key.py::authenticate_api_key#function",
      "kind": "function",
      "name": "authenticate_api_key",
      "file": "fastapi/security/api_key.py",
      "line": 34,
      "signature": "def authenticate_api_key(api_key: str) -> bool",
      "summary": "Validate an API key for authentication",
      "score": 25
    }
  ],
  "_meta": {
    "timing_ms": 12.8,
    "total_symbols": 1847,
    "truncated": false,
    "tokens_saved": 5200,
    "total_tokens_saved": 1289877
  }
}
```

## get_symbol

Retrieve the full source code of a specific symbol using O(1) byte-offset seeking. Optionally verify content hash to detect source drift and include surrounding context lines.

```json
// Request
{
  "repo": "fastapi/fastapi",
  "symbol_id": "fastapi/security/oauth2.py::authenticate_user#function",
  "verify": true,
  "context_lines": 3
}

// Response
{
  "id": "fastapi/security/oauth2.py::authenticate_user#function",
  "kind": "function",
  "name": "authenticate_user",
  "file": "fastapi/security/oauth2.py",
  "line": 89,
  "end_line": 102,
  "signature": "def authenticate_user(db: Session, username: str, password: str) -> Optional[User]",
  "decorators": [],
  "docstring": "Authenticate a user by username and password.\n\nArgs:\n    db: Database session\n    username: User's username\n    password: User's password\n\nReturns:\n    User object if authenticated, None otherwise",
  "content_hash": "a1b2c3d4e5f6...",
  "source": "def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:\n    \"\"\"Authenticate a user by username and password.\"\"\"\n    user = db.query(User).filter(User.username == username).first()\n    if not user:\n        return None\n    if not verify_password(password, user.hashed_password):\n        return None\n    return user",
  "context_before": "\n\nfrom .utils import verify_password",
  "context_after": "\n\ndef create_access_token(data: dict):\n    ...",
  "_meta": {
    "timing_ms": 2.1,
    "content_verified": true,
    "tokens_saved": 3950,
    "total_tokens_saved": 1293827,
    "cost_avoided": {"claude_opus": 0.10, "gpt5_latest": 0.04}
  }
}
```

## get_symbols

Batch retrieve multiple symbols in a single call. More efficient than repeated `get_symbol` calls when loading related symbols.

```json
// Request
{
  "repo": "fastapi/fastapi",
  "symbol_ids": [
    "fastapi/applications.py::FastAPI.__init__#method",
    "fastapi/applications.py::FastAPI.add_api_route#method",
    "fastapi/routing/router.py::APIRouter#class"
  ]
}

// Response
{
  "symbols": [
    {
      "id": "fastapi/applications.py::FastAPI.__init__#method",
      "kind": "method",
      "name": "__init__",
      "file": "fastapi/applications.py",
      "line": 67,
      "end_line": 95,
      "signature": "def __init__(self, *, debug: bool = False, ...)",
      "source": "def __init__(self, *, debug: bool = False, ...):\n    ..."
    },
    {
      "id": "fastapi/applications.py::FastAPI.add_api_route#method",
      "kind": "method",
      "name": "add_api_route",
      "file": "fastapi/applications.py",
      "line": 120,
      "end_line": 145,
      "signature": "def add_api_route(self, path: str, endpoint: Callable, **kwargs)",
      "source": "def add_api_route(self, path: str, ...):\n    ..."
    }
  ],
  "errors": [],
  "_meta": {
    "timing_ms": 4.5,
    "symbol_count": 3,
    "tokens_saved": 8200,
    "total_tokens_saved": 1302027
  }
}
```

## get_file_content

Retrieve cached file content with optional line range slicing. Useful for reading specific sections of a file.

```json
// Request - read lines 20-40 of a file
{
  "repo": "fastapi/fastapi",
  "file_path": "fastapi/applications.py",
  "start_line": 20,
  "end_line": 40
}

// Response
{
  "repo": "fastapi/fastapi",
  "file": "fastapi/applications.py",
  "language": "python",
  "file_summary": "Core FastAPI application class and routing configuration",
  "start_line": 20,
  "end_line": 40,
  "line_count": 250,
  "content": "from starlette.applications import Starlette\nfrom starlette.routing import BaseRoute\n...",
  "_meta": {
    "timing_ms": 1.8,
    "tokens_saved": 2100,
    "total_tokens_saved": 1304127
  }
}
```

## search_text

Full-text search across all indexed file contents. Use when symbol search misses — for string literals, comments, configuration values, or patterns not captured as symbols.

```json
// Request
{
  "repo": "fastapi/fastapi",
  "query": "TODO",
  "file_pattern": "*.py",
  "max_results": 20,
  "context_lines": 2
}

// Response
{
  "repo": "fastapi/fastapi",
  "query": "TODO",
  "context_lines": 2,
  "result_count": 5,
  "results": [
    {
      "file": "fastapi/routing/router.py",
      "matches": [
        {
          "line": 145,
          "text": "# TODO: Add support for WebSocket routes",
          "before": ["    def add_route(self, path: str):", "        ..."],
          "after": ["    def include_router(self, router):", "        ..."]
        }
      ]
    },
    {
      "file": "fastapi/security/oauth2.py",
      "matches": [
        {
          "line": 67,
          "text": "# TODO: Implement token refresh logic",
          "before": ["def create_token(data: dict):", "    encoded = jwt.encode(data)"],
          "after": ["    return encoded", ""]
        }
      ]
    }
  ],
  "_meta": {
    "timing_ms": 45.2,
    "files_searched": 230,
    "truncated": false,
    "tokens_saved": 18500,
    "total_tokens_saved": 1322627
  }
}
```

## invalidate_cache

Delete the index and cached files for a repository. Forces a full re-index on the next `index_repo` or `index_folder` call.

```json
// Request
{
  "repo": "fastapi/fastapi"
}

// Response
{
  "success": true,
  "message": "Cache invalidated for fastapi/fastapi",
  "_meta": {"timing_ms": 5.2}
}

// Force re-index after invalidation
{
  "url": "fastapi/fastapi",
  "incremental": false
}
```

## Symbol ID Format

Symbol IDs follow a stable format that remains consistent across re-indexing:

```
{file_path}::{qualified_name}#{kind}
```

Examples:
- `src/main.py::UserService#class`
- `src/main.py::UserService.login#method`
- `src/utils.py::authenticate#function`
- `config.py::MAX_RETRIES#constant`
- `types.py::UserRole#type`

Symbol IDs are returned by `get_file_outline` and `search_symbols`, and are passed to `get_symbol` or `get_symbols` to retrieve source code.

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `GITHUB_TOKEN` | GitHub API authentication for private repos and higher rate limits |
| `ANTHROPIC_API_KEY` | AI summaries via Claude Haiku (takes priority) |
| `ANTHROPIC_MODEL` | Override Claude model (default: `claude-haiku-4-5-20251001`) |
| `GOOGLE_API_KEY` | AI summaries via Gemini Flash (fallback) |
| `GOOGLE_MODEL` | Override Gemini model (default: `gemini-2.5-flash-lite`) |
| `CODE_INDEX_PATH` | Custom storage path (default: `~/.code-index/`) |
| `JCODEMUNCH_MAX_INDEX_FILES` | Maximum files to index per repo (default: 10000) |
| `JCODEMUNCH_LOG_LEVEL` | Logging level: DEBUG, INFO, WARNING, ERROR |
| `JCODEMUNCH_LOG_FILE` | Log file path (recommended for debugging) |

## Supported Languages

| Language | Extensions | Symbol Types |
|----------|------------|--------------|
| Python | `.py` | function, class, method, constant, type |
| JavaScript | `.js`, `.jsx` | function, class, method, constant |
| TypeScript | `.ts`, `.tsx` | function, class, method, constant, type |
| Go | `.go` | function, method, type, constant |
| Rust | `.rs` | function, type, impl, constant |
| Java | `.java` | method, class, type, constant |
| PHP | `.php` | function, class, method, type, constant |
| C# | `.cs` | class, method, type, record |
| C | `.c` | function, type, constant |
| C++ | `.cpp`, `.cc`, `.h` | function, class, method, type, constant |
| Dart | `.dart` | function, class, method, type |
| Elixir | `.ex`, `.exs` | class, type, method, function |
| Ruby | `.rb`, `.rake` | class, type, method, function |

## Summary

jCodeMunch MCP transforms how AI agents explore codebases by replacing brute-force file reading with precision symbol retrieval. The typical workflow is: index a repository once with `index_repo` or `index_folder`, get a high-level overview with `get_repo_outline`, browse the file structure with `get_file_tree`, understand file APIs with `get_file_outline`, search for specific functionality with `search_symbols` or `search_text`, and finally retrieve exact implementations with `get_symbol` or `get_symbols`. This structured approach typically saves 80-99% of tokens compared to traditional file-dumping methods.

The server integrates seamlessly with any MCP-compatible client through simple JSON configuration. For agent-driven workflows, the recommended pattern is: start broad (repo outline), narrow down (file tree, file outline), search when needed (symbol search, text search), and retrieve precisely (get symbol). Every response includes token savings metrics so you can track efficiency gains. The local-first architecture ensures your code never leaves your machine, while optional AI summaries (via Claude Haiku or Gemini Flash) provide human-readable descriptions of every symbol.
