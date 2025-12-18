# AM Agent Claude

A Claude/Cursor agent plugin for [agent-manager](https://github.com/john-westcott-iv/agent-manager).

## Installation

First, install the agent-manager:

```bash
cd ../agent_manager
pip install -e .
```

Then install this plugin:

```bash
pip install -e .
```

## Usage

This plugin is automatically discovered by agent-manager. Use it with:

```bash
agent-manager --agent claude
```

## Requirements

- agent-manager
- claude-agent-sdk

## Naming Convention

This plugin follows the `am_<type>_<name>` naming convention for agent-manager plugins:

| Type | Pattern | Example |
|------|---------|---------|
| Agent | `am_agent_<name>` | `am_agent_claude` |
| Merger | `am_merger_<name>` | `am_merger_smart_markdown` |
| Repo | `am_repo_<name>` | `am_repo_s3` |

## License

Apache License 2.0 - See [LICENSE](LICENSE) for details.

