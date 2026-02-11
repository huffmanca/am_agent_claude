"""Claude/Cursor agent plugin for hierarchical configuration management."""

import asyncio
from pathlib import Path

from agent_manager.output import MessageType, VerbosityLevel, message
from agent_manager.plugins.agents import AbstractAgent, ScopeConfig
from claude_agent_sdk import query


class Agent(AbstractAgent):
    """Agent for managing Claude/Cursor configuration from hierarchical repositories."""

    agent_directory: Path = Path.joinpath(AbstractAgent.home_directory, ".claude")

    @property
    def scopes(self) -> dict[str, ScopeConfig]:
        """Define available scopes for Claude agent.

        Scopes:
            default: Alias for 'user' scope
            user: User-level configuration at ~/.claude
            project: Project-specific configuration at <cwd>/.claude

        Returns:
            Dictionary mapping scope names to ScopeConfig objects
        """
        user_dir = Path.home() / ".claude"
        project_dir = Path.cwd() / ".claude"

        return {
            "default": ScopeConfig(
                directory=user_dir,
                description="User-level Claude configuration (alias for 'user')",
            ),
            "user": ScopeConfig(
                directory=user_dir,
                description="User-level Claude configuration (~/.claude)",
            ),
            "project": ScopeConfig(
                directory=project_dir,
                description="Project-specific Claude configuration (./.claude)",
            ),
        }

    def register_hooks(self) -> None:
        """Register Claude-specific hooks for file processing."""
        # Register TextMerger for .cursorrules and .clinerules files (concatenation)
        from agent_manager.plugins.mergers.text_merger import TextMerger

        self.merger_registry.register_filename(".cursorrules", TextMerger)
        self.merger_registry.register_filename(".clinerules", TextMerger)

        # Add validation hooks for cursorrules files
        self.pre_merge_hooks[".cursorrules*"] = self._validate_cursorrules
        self.pre_merge_hooks[".clinerules*"] = self._validate_cursorrules

    def _validate_cursorrules(self, content: str, entry: dict, file_path: Path) -> str:
        """Validate cursorrules/clinerules content.

        Args:
            content: File content
            entry: Hierarchy entry
            file_path: Path to source file

        Returns:
            Validated content
        """
        if not content.strip():
            message(f"    Empty cursorrules file in {entry['name']}", MessageType.WARNING, VerbosityLevel.ALWAYS)
        return content

    async def _run_claude_init(self) -> None:
        """Run Claude SDK initialization (async helper)."""
        async for msg in query(prompt="/init"):
            message(f"  {msg}", MessageType.INFO, VerbosityLevel.EXTRA_VERBOSE)

    def _initialize(self, scope: str | None = None) -> None:
        """Initialize the Claude agent directory using Claude SDK.

        Args:
            scope: Scope to initialize. If None, uses DEFAULT_SCOPE.
        """
        output_dir = self.get_scope_directory(scope)

        # Check if already initialized
        if output_dir.exists():
            message(
                f"Claude agent directory already exists: {output_dir}",
                MessageType.DEBUG,
                VerbosityLevel.DEBUG,
            )
            return

        message(
            f"Initializing Claude agent directory: {output_dir}",
            MessageType.INFO,
            VerbosityLevel.EXTRA_VERBOSE,
        )

        # Only run Claude SDK init for user scope (not project scope)
        if scope in (None, "default", "user"):
            message("Running Claude SDK initialization...", MessageType.INFO, VerbosityLevel.EXTRA_VERBOSE)
            try:
                # Use Claude SDK to initialize with all defaults
                asyncio.run(self._run_claude_init())

                # Ensure our directory exists for merged configurations
                output_dir.mkdir(parents=True, exist_ok=True)
                message(f"✓ Claude agent initialized at {output_dir}", MessageType.SUCCESS, VerbosityLevel.ALWAYS)
                return
            except Exception as e:
                message(f"Claude SDK initialization failed: {e}", MessageType.WARNING, VerbosityLevel.ALWAYS)
                message("Creating directory manually as fallback...", MessageType.INFO, VerbosityLevel.EXTRA_VERBOSE)

        # Create directory manually (for project scope or fallback)
        output_dir.mkdir(parents=True, exist_ok=True)
        message(f"✓ Created {output_dir}", MessageType.SUCCESS, VerbosityLevel.ALWAYS)
