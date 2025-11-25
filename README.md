# Multi-Agent Runner

A simple, robust Python-based concurrent task orchestrator with zero external dependencies (stdlib-only).

## Features

- **Concurrent Execution**: Run multiple agents in parallel using `ThreadPoolExecutor`
- **Two Agent Types**:
  - `noop`: No-op agent for testing/demo
  - `shell`: Execute shell commands with timeout and retry support
- **Configuration**: Load agents from JSON or YAML config files
- **Structured Logging**: Timestamped info/warning/error logs to stdout
- **Graceful Shutdown**: Respond to `SIGINT` and `SIGTERM` signals
- **JSON Output**: Export results for integration with other tools
- **Retry Mechanism**: Built-in retry support per agent with backoff
- **Timeout Support**: Kill long-running agents after configurable timeout
- **Minimal Dependencies**: Pure Python stdlib (PyYAML optional for YAML configs)

## Installation

No installation needed — just Python 3.7+.

```bash
git clone https://github.com/Exn0x/Rz2.git
cd Rz2
python3 multi_agent_runner.py --help
```

Optional: Install PyYAML if you want to use `.yaml` config files:
```bash
pip install pyyaml
```

## Quick Start

### Run Default Demo
```bash
python3 multi_agent_runner.py
```
Output: Two noop agents run concurrently.

### Run with Config
```bash
python3 multi_agent_runner.py --config agents.json
```

### Get JSON Output
```bash
python3 multi_agent_runner.py --config agents.json --json
```

### Control Concurrency
```bash
python3 multi_agent_runner.py --config agents.json --workers 2
```

## Configuration

Create a JSON or YAML file with agent definitions.

### agents.json (Example)
```json
{
  "agents": [
    {
      "name": "check-python",
      "type": "shell",
      "cmd": "python3 --version",
      "timeout": 5,
      "retries": 0
    },
    {
      "name": "list-files",
      "type": "shell",
      "cmd": "ls -la /workspaces/Rz2",
      "timeout": 10,
      "retries": 1
    },
    {
      "name": "demo",
      "type": "noop"
    }
  ]
}
```

### Config Schema

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | required | Agent identifier |
| `type` | string | required | `noop` or `shell` |
| `cmd` | string | — | Shell command (required for `shell` type) |
| `timeout` | float | None | Max execution time in seconds |
| `retries` | int | 0 | Number of retry attempts |

## Usage Examples

### CI/CD Pipeline
```json
{
  "agents": [
    {"name": "build", "type": "shell", "cmd": "npm run build", "timeout": 60, "retries": 1},
    {"name": "test", "type": "shell", "cmd": "npm test", "timeout": 120, "retries": 0},
    {"name": "deploy", "type": "shell", "cmd": "npm run deploy", "timeout": 300, "retries": 2}
  ]
}
```

### Health Checks
```json
{
  "agents": [
    {"name": "api-health", "type": "shell", "cmd": "curl -f http://localhost:3000/health || exit 1", "timeout": 5},
    {"name": "db-health", "type": "shell", "cmd": "curl -f http://localhost:5432 || exit 1", "timeout": 5},
    {"name": "cache-health", "type": "shell", "cmd": "redis-cli ping", "timeout": 5}
  ]
}
```

### Data Processing
```json
{
  "agents": [
    {"name": "process-data-1", "type": "shell", "cmd": "python3 process.py --file data1.csv"},
    {"name": "process-data-2", "type": "shell", "cmd": "python3 process.py --file data2.csv"},
    {"name": "process-data-3", "type": "shell", "cmd": "python3 process.py --file data3.csv"}
  ]
}
```

## Output

### Default (Human-Readable)
```
2025-11-25 17:28:31,956 INFO Running 4 agents with up to 4 workers
2025-11-25 17:28:31,956 INFO Starting agent check-python (type=shell)
2025-11-25 17:28:31,850 INFO Agent check-python succeeded in 0.009s
2025-11-25 17:28:31,850 INFO Agent result: {'name': 'check-python', 'status': 'ok', 'attempts': 1}
2025-11-25 17:28:31,859 INFO Run finished. Results: [...]
```

### JSON Format (`--json`)
```json
[
  {"name": "check-python", "status": "ok", "attempts": 1, "duration": 0.009},
  {"name": "list-root", "status": "ok", "attempts": 1, "duration": 0.008},
  {"name": "get-date", "status": "ok", "attempts": 1, "duration": 0.015},
  {"name": "demo-noop", "status": "ok", "attempts": 1}
]
```

## Programmatic Usage

```python
from pathlib import Path
from multi_agent_runner import Runner, load_config

# Load config
agents = load_config(Path("agents.json"))

# Create runner
runner = Runner(agents, max_workers=4)

# Execute
results = runner.run()

# Process results
for result in results:
    print(f"{result['name']}: {result['status']}")
```

## Error Handling

Agents that fail are logged with details and can be retried automatically:

```json
{
  "name": "unreliable-task",
  "type": "shell",
  "cmd": "flaky-command",
  "retries": 3,
  "timeout": 10
}
```

On failure, the agent result includes:
```json
{
  "name": "unreliable-task",
  "status": "failed",
  "error": "command failed with exit code 1",
  "attempts": 4
}
```

## Signal Handling

The runner gracefully responds to:
- `SIGINT` (Ctrl+C): Stops accepting new agents; waits for in-flight agents
- `SIGTERM` (kill): Same as SIGINT

## Command-Line Options

```
usage: multi_agent_runner.py [-h] [--config CONFIG] [--workers WORKERS] [--json]

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        JSON/YAML config file with agents
  --workers WORKERS, -w WORKERS
                        Max concurrent agents (default: 4)
  --json                Print results as JSON
```

## Architecture

- **AgentSpec**: Dataclass representing a single agent configuration
- **Runner**: Main orchestrator that manages concurrent execution
- **load_config()**: Parses JSON/YAML and returns list of AgentSpecs
- **run_agent()**: Executes a single agent with retry/timeout logic

## Testing

Run the provided `agents.json` sample:
```bash
python3 multi_agent_runner.py --config agents.json
python3 multi_agent_runner.py --config agents.json --json
python3 multi_agent_runner.py --config agents.json --workers 2
```

## Future Enhancements

- [ ] HTTP/webhook agent type
- [ ] Python callable agent type
- [ ] Persistent logging to file
- [ ] Agent dependencies (run agent B after agent A succeeds)
- [ ] Rate limiting / throttling
- [ ] Metrics/observability (OpenTelemetry)
- [ ] Web UI dashboard
- [ ] REST API wrapper

## License

MIT

## Author

Exn0x