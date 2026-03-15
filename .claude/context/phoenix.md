# Phoenix Observability
*Component documentation — shared across agent sessions*

## Scope
Observability for the **RDKit MCP server only**. Not for Claude Code itself (Pro plan has no API key to instrument).

## What We Track
Custom OpenTelemetry spans emitted by `rdkit_mcp.py`, sent to local Phoenix instance.

| Metric | Type | Why |
|--------|------|-----|
| Tool call name | span attribute | Which tool was invoked |
| Tier resolved (1/2/3) | span attribute | Is context-routing working or falling through to full search? |
| Result count | span attribute | Are searches returning too many/few results? |
| Source type (python/cpp/all) | span attribute | How often is C++ source accessed? |
| Duration | span timing | Latency per tool call |

## Stack
- `opentelemetry-api` + `opentelemetry-sdk` — span creation and export
- `opentelemetry-exporter-otlp-proto-grpc` — send to Phoenix
- Phoenix (`phoenix serve`) — UI dashboard on `localhost:6006`, OTLP receiver on `localhost:4317`

## Integration in rdkit_mcp.py
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint="localhost:4317", insecure=True)))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("rdkit-mcp")

@mcp.tool()
def search_code(query: str, source: str = "python", context_file: str | None = None) -> str:
    with tracer.start_as_current_span("search_code") as span:
        span.set_attribute("query", query)
        span.set_attribute("source", source)
        span.set_attribute("tier_resolved", tier)
        span.set_attribute("result_count", len(results))
        # ... tool logic
```

## What This Does NOT Cover
- **Claude Code cost tracking** — requires Anthropic API key, not available on Pro plan
- **Claude Code session traces** — `settings.json` telemetry is separate, not needed for MCP server
- **Auto-instrumentation** — no `openinference-instrumentation-anthropic`, we instrument manually

## Developer Workflow
```
Terminal 1: phoenix serve                        # UI at localhost:6006
Terminal 2: claude                               # MCP server auto-spawns via .mcp.json
            → use rdkit tools → spans appear in Phoenix dashboard
```

## Improvement Loop
1. Tier 3 hit often → index is missing modules, rebuild
2. Tier 1 rarely used → `context_file` not being passed, fix tool descriptions
3. High result counts → tighten ripgrep filters
4. C++ source accessed often → consider making it default

## Open Questions
1. Should Phoenix be a required or optional dependency for the MCP server?
2. Graceful degradation — if Phoenix is not running, server should still work (just no spans)?
