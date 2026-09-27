# Devcontainer

This repo runs on the shared **AI devcontainer platform**. The two private components — `.claude/`
and `devcontainers/` — are git **submodules** managed by `wsctl`.

> **First time here?** Set up `wsctl`, the token, and the submodules with **[INSTALL.md](INSTALL.md)**.

This page covers running **your own** containers alongside the platform workspace.

## Add your own services

Your repo can run its own containers — a database, a web app, anything — **alongside** the workspace,
without touching the `devcontainers/` platform. Two per-repo files:

**1. Declare it** in `.devcontainer/docker-compose.client.yaml` (merges over the platform stack; swap
`busybox` for your real image):

```yaml
services:
  my-service:
    image: busybox
    command: ["httpd", "-f", "-p", "8080"]
    networks: [central-gateway-internal]
```

**2. Turn it on** in `.devcontainer/devcontainer.json`, then **Rebuild Container**:

```jsonc
"runServices": ["workspace", "my-service"]
```

Add more services the same way.

## Reaching your service

| From                    | How                                             | Example                                   |
| ----------------------- | ----------------------------------------------- | ----------------------------------------- |
| your code (workspace)   | service **name** on the shared network          | `my-service:8080`                         |
| host / browser (HTTP)   | `‹service›.‹port›.‹project›.localhost:‹ingress›` | `my-service.8080.dev-jane.localhost:7700` |

- **TCP services** (e.g. a database) are reached by **name** from your code — no browser URL needed.
- **Web UIs** get a host URL automatically through the ingress, behind the admin `basic_auth` gate
  (user `admin`). `‹project›` = your `COMPOSE_PROJECT_NAME`, `‹ingress›` = your `DEVCONTAINER_INGRESS_PORT`.
- Everything joins `central-gateway-internal` (the sealed no-internet wall), so Docker DNS resolves
  service names for you.
