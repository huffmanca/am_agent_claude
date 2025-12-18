# AM Agent Claude - AI Assistant Guide

## Project Overview

**AM Agent Claude** is a plugin for Agent Manager that provides Claude AI integration. It implements the `AbstractAgent` interface to enable Claude-powered AI assistance with hierarchical configuration management.

### Purpose
This is a **reference implementation** and **working example** of an Agent Manager plugin. It demonstrates:
- How to implement the `AbstractAgent` interface
- How to use the merged configuration output
- How to integrate with external AI services (Claude/Anthropic)

## Naming Convention

This plugin follows the `am_<type>_<name>` pattern:
- **Package name**: `am_agent_claude`
- **Pip name**: `am-agent-claude`
- **Type**: `agent`
- **Name**: `claude`

## Architecture

### Single-File Plugin
This is intentionally a minimal, focused plugin:
```
am_agent_claude/
├── am_agent_claude/
│   ├── __init__.py         # Package initialization
│   └── claude.py           # Main plugin (~150 lines)
└── tests/
    ├── __init__.py
    └── test_claude.py      # Tests (~900 lines)
```

### Dependencies
- **Parent Framework**: Agent Manager (must be installed)
- **AI Service**: Claude Agent SDK
- **Key Libraries**: `claude-agent-sdk`, `agent_manager`

## Implementation Details

### Plugin Class: `Agent`

```python
from agent_manager.plugins.agents import AbstractAgent

class Agent(AbstractAgent):
    """Claude AI agent implementation."""
    
    agent_directory: Path = Path.home() / ".claude"
    
    def register_hooks(self) -> None:
        """Register Claude-specific hooks."""
        pass
    
    def update(self, config: dict) -> None:
        """Update configuration from hierarchy."""
        self._initialize()
        self.merge_configurations(config)
```

### Key Features

1. **Configuration Loading**: Reads merged files from `agent_directory`
2. **Hook System**: Pre/post-merge hooks for file processing
3. **Error Handling**: Graceful handling of SDK failures
4. **Output Integration**: Uses Agent Manager's output system for consistent logging

### Entry Point Configuration

In `pyproject.toml`:
```toml
[project.entry-points."agent_manager.agents"]
claude = "am_agent_claude.claude:Agent"
```

This registers the plugin with Agent Manager's discovery system.

## Development Guidelines

### Code Style
- **Formatter**: `ruff format` (matches parent project)
- **Type Hints**: Full type annotations
- **Docstrings**: Google-style docstrings
- **Keep It Simple**: This is a reference implementation

### Testing
- **Framework**: pytest (consistent with Agent Manager)
- **Coverage**: Comprehensive mocking of Claude SDK
- **Run Tests**: `pytest tests/ -v`

## Using the Plugin

### Installation

```bash
# Install Agent Manager first
cd agent-manager/agent_manager
pip install -e .

# Install Claude Agent
cd ../am_agent_claude
pip install -e .
```

### Configuration

```bash
# Initialize Agent Manager config
agent-manager config init

# Run Claude agent
agent-manager --agent claude
```

## Key Methods

### `register_hooks()`
Registers file-specific hooks:
- `.cursorrules` and `.clinerules` use TextMerger for concatenation
- `*.md` files get cleaned (trailing whitespace removed)
- All files get metadata headers added

### `update(config)`
Main entry point:
1. Initializes Claude agent directory
2. Calls `merge_configurations()` from AbstractAgent

### `_add_metadata_header(content, file_name, sources)`
Adds appropriate comment-style headers based on file type:
- YAML/Python/Shell: `# comment`
- Markdown/HTML/XML: `<!-- comment -->`
- JSON: No header (doesn't support comments)

## Output Integration

```python
from agent_manager.output import MessageType, VerbosityLevel, message

# User-facing messages
message("Initializing Claude...", MessageType.NORMAL, VerbosityLevel.ALWAYS)

# Success messages
message("✓ Claude ready", MessageType.SUCCESS, VerbosityLevel.ALWAYS)

# Progress (at -vv)
message("Loading configuration...", MessageType.INFO, VerbosityLevel.EXTRA_VERBOSE)

# Errors
message("SDK initialization failed", MessageType.WARNING, VerbosityLevel.ALWAYS)
```

## Testing

### Mock Strategy

Tests mock the Claude SDK to avoid real API calls:

```python
from unittest.mock import Mock, patch

def test_initialize(self, tmp_path):
    agent = Agent()
    agent.agent_directory = tmp_path / ".claude"

    with patch("am_agent_claude.claude.query") as mock_query:
        mock_query.return_value = iter(["Init"])
        
        with patch("am_agent_claude.claude.message"):
            agent._initialize()

    assert agent.agent_directory.exists()
```

### Test Coverage
- ✅ Agent initialization
- ✅ Hook registration
- ✅ Markdown cleaning
- ✅ Cursorrules validation
- ✅ Metadata header generation
- ✅ SDK failure handling
- ✅ Multi-level hierarchy merging

## Integration with Agent Manager

### Discovery
Agent Manager automatically discovers this plugin via entry points:
```python
# Agent Manager calls this during discovery
from am_agent_claude.claude import Agent
agents = discover_agent_plugins()  # Returns {'claude': Agent}
```

### Execution Flow
1. User runs: `agent-manager --agent claude`
2. Agent Manager loads configuration
3. Agent Manager updates repositories
4. Agent Manager calls: `Agent().update(config)`
5. Agent merges configurations to `~/.claude`
6. Files are ready for Claude/Cursor to use

## Important Files

### Core Implementation
- `am_agent_claude/claude.py` - Main plugin (~150 lines)
  - `Agent` class
  - Hook implementations
  - Metadata header generation

### Tests
- `tests/test_claude.py` - Comprehensive test suite (~900 lines)
  - Mock-based testing
  - All hook scenarios
  - Edge cases

### Configuration
- `pyproject.toml` - Package configuration
  - Entry point registration
  - Dependencies
  - Metadata

## Troubleshooting

### Common Issues

1. **Plugin Not Found**
   - Verify: `pip list | grep am-agent-claude`
   - Reinstall: `pip install -e .`
   - Check: `agent-manager agents list`

2. **Import Errors**
   - Ensure Agent Manager is installed first
   - Check Python path includes both packages

3. **Test Failures**
   - Update mocks if Claude SDK changes
   - Check Agent Manager output API compatibility

### Debug Mode

```bash
# Run with full debug output
agent-manager -vvv --agent claude

# See plugin discovery
agent-manager -vvv agents list
```

## Statistics

- **Core Code**: ~150 lines in 2 files
- **Tests**: ~900 lines in 2 files
- **Test-to-Code Ratio**: 6:1 (excellent!)
- **Dependencies**: 2 (claude-agent-sdk, agent_manager)

## Design Decisions

1. **Minimal Implementation**: Keep it simple as a reference
2. **Full Test Coverage**: Demonstrate proper testing practices
3. **Error-First Design**: Handle all error cases gracefully
4. **Output Integration**: Use parent framework's output system
5. **Configuration-Driven**: All behavior controlled by merged configs

## Related Documentation

### Agent Manager Docs
- `agent_manager/docs/CUSTOM_AGENTS.md` - Plugin development guide
- `agent_manager/docs/ARCHITECTURE.md` - System architecture
- `agent_manager/AGENTS.md` - Parent project guide

---

**Last Updated**: December 2025  
**Version**: 0.0.1  
**Python**: 3.12+  
**Parent Framework**: Agent Manager
**License**: Apache 2.0

