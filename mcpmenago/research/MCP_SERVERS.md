## MCP Server Strategy Brief

This document outlines the evaluation of three distinct MCP server architectures intended for a hybrid tool mixture. The goal is to separate deep, local codebase comprehension from ad-hoc remote documentation retrieval and up-to-date framework knowledge.

### 1. Local Use Case: `jcodemunch-mcp`
https://raw.githubusercontent.com/jgravelle/jcodemunch-mcp/refs/heads/main/README.md
**Primary Role:** Deep, deterministic codebase exploration and cross-language context mapping.
**Status:** Primary local server (Aligns with our established AST/Static Indexing vision).

* **Overview:** `jcodemunch-mcp` utilizes `tree-sitter` AST parsing to index the codebase once locally, enabling agents to retrieve exact symbols (functions, classes) rather than brute-reading entire files.
* **Data Quality (Excellent):** Provides surgically precise, compiler-level structured retrieval via stable symbol IDs and byte-offset addressing. It maps the exact boundaries of functions and classes without relying on fuzzy text matching.
* **Token Efficiency (Maximum):** Cuts code-reading token costs by up to 99%. For example, finding a specific function drops from ~40,000 tokens (raw file read) to ~200 tokens (exact symbol extraction).
* **Privacy:** 100% local execution. Code and queries never leave the host machine, making it safe for enterprise and proprietary development.

---

### 2. Remote Search Use Case: `GitMCP`
**Primary Role:** Manual, ad-hoc retrieval of external library documentation and public GitHub repositories.
**Status:** Optional remote connector for fetching dynamic docs not present in the local index.

* **Overview:** A zero-setup, remote MCP server (hosted via Cloudflare Workers) that transforms any public GitHub project into a documentation hub by searching `llms.txt`, `README.md`, and generic code chunks.
* **Data Quality (Moderate/Contextual):** GitMCP functions as a semantic search engine. It lacks compiler-level AST parsing and deterministic dependency graphs. If queried for complex cross-language mappings (e.g., Python to C++ in RDKit), it relies on blind text-searching rather than mathematical code relationships.
* **Token Efficiency (Good, but imprecise):** Utilizes vector embeddings to return semantically similar "chunks" of text. While better than loading full repositories, it cannot execute the byte-precise extraction (e.g., "Give me exactly lines 42-60") that a local AST database can.
* **Privacy (High Risk for Local Code):** Despite claiming a "privacy-first" design with no query storage, prompt data and searches must traverse the internet to hit a remote Cloudflare worker and the GitHub API. This introduces an unnecessary attack vector if used alongside proprietary code.

---

### 3. Local Additions: `Context7`
**Primary Role:** Injecting up-to-date, version-specific official documentation for fast-moving frameworks (Next.js, React, Supabase, etc.) directly into the AI's context.
**Status:** High-value supplementary server to prevent hallucination of third-party APIs.

* **Overview:** Developed by Upstash, `Context7` runs locally as an MCP server (e.g., via `npx @upstash/context7-mcp`) but acts as a bridge to a remote, continuously updated documentation database. It exposes tools like `resolve-library-id` and `get-library-docs` to fetch official, working code examples on demand.
* **Data Quality (Excellent for 3rd Party):** Completely eliminates the "stale training data" problem. By pulling curated documentation and verified code snippets straight from the source, it prevents the LLM from hallucinating deprecated APIs or syntax.
* **Token Efficiency (High):** Only fetches the specific topic requested (e.g., "stream trim in Redis") with a configurable token limit, rather than dumping entire documentation websites into the context window.
* **Privacy (Safe for Local Code):** While it fetches data remotely, it only transmits the library name and the specific API query (e.g., "Next.js routing"). Your proprietary local codebase is never sent to Upstash's servers.

---

### Strategy Summary & Responsibilities

| Concept / Area | Tool | Primary Responsibility | Data Quality | Token Cost | Privacy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Local Calls Only** | `jcodemunch-mcp` | Core proprietary codebase tasks, AST parsing, cross-language mapping. | Deterministic, byte-precise | Extremely Low (~200 tokens/query) | 100% Secure / Air-gapped |
| **2. Remote Calls Only** | `GitMCP` | Ad-hoc exploration of public GitHub repositories and unstructured readmes. | Fuzzy, chunk-based (Semantic) | Moderate (Semantic chunks) | High Risk (Remote execution) |
| **3. Local Additions** | `Context7` | Augmenting local knowledge with up-to-date, official 3rd-party framework docs. | Curated, version-specific | Low (Filtered snippets) | Safe (Only API queries sent) |

