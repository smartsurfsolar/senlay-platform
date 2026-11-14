# API Overview

Senlay exposes physical-world context through simple HTTP endpoints.

## Sense Endpoint

```bash
curl -H "Authorization: Bearer $SENLAY_API_KEY" "https://senlay.cloud/api/v1/sense?lat=10.933&lng=108.287"
```

Purpose:

- give an AI agent a concise read of current physical conditions
- return context that can be used directly in a model prompt
- include nearby signed station observations when available
- include descriptive local historical baselines when enough checked station samples exist
- support quick integration with assistants, workflows, and tools

## Physical World Model Endpoint

```bash
curl -H "Authorization: Bearer $SENLAY_API_KEY" "https://senlay.cloud/api/v1/pwm?lat=10.933&lng=108.287"
```

Purpose:

- return a richer physical-world model
- include current conditions and relevant modifiers
- compare current signed station readings with descriptive historical baselines when available
- support applications that need structured environmental context

## Open Network Operations

Station owners can create providers, register stations, rotate station secrets, disable compromised stations, and dry-run a signed observation before publishing live data.

See:

- [`NETWORK_PROTOCOL.md`](NETWORK_PROTOCOL.md)
- [`../openapi/senlay.public.yaml`](../openapi/senlay.public.yaml)

## Agent Registration

Senlay supports agent-friendly onboarding so an AI agent can request a key without a human-style password flow.

See the public website docs for the current production details:

[https://senlay.cloud/docs.html](https://senlay.cloud/docs.html)

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

Local memory is descriptive historical context, not a trained location-specific forecast. Availability depends on eligible observations and coverage.
