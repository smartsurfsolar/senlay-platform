# API Overview

Senlay exposes physical-world context through simple HTTP endpoints.

## Sense Endpoint

```bash
curl "https://senlay.world/api/v1/sense?lat=10.933&lon=108.287"
```

Purpose:

- give an AI agent a concise read of current physical conditions
- return context that can be used directly in a model prompt
- support quick integration with assistants, workflows, and tools

## Physical World Model Endpoint

```bash
curl "https://senlay.world/api/v1/pwm?lat=10.933&lon=108.287"
```

Purpose:

- return a richer physical-world model
- include current conditions and relevant modifiers
- support applications that need structured environmental context

## Agent Registration

Senlay supports agent-friendly onboarding so an AI agent can request a key without a human-style password flow.

See the public website docs for the current production details:

[https://senlay.world/docs.html](https://senlay.world/docs.html)

## Response Design

Responses are designed to be:

- readable by developers
- easy for an LLM to consume
- source-aware
- concise enough for prompt context
- structured enough for application logic

See:

- [`../examples/sense-response.json`](../examples/sense-response.json)
- [`../examples/agent-context.txt`](../examples/agent-context.txt)
