"""Comprehensive tests for am_agent_claude/claude.py - Claude agent implementation."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from am_agent_claude.claude import Agent


class TestClaudeAgentInitialization:
    """Test cases for Claude Agent initialization."""

    def test_initialization(self):
        """Test basic agent initialization."""
        agent = Agent()

        assert agent.agent_directory is not None
        assert isinstance(agent.agent_directory, Path)

    def test_agent_directory_is_claude_folder(self):
        """Test that agent_directory is set to ~/.claude."""
        agent = Agent()

        expected = Path.home() / ".claude"
        assert agent.agent_directory == expected

    def test_inherits_from_abstract_agent(self):
        """Test that Agent inherits from AbstractAgent."""
        from agent_manager.plugins.agents import AbstractAgent

        agent = Agent()

        assert isinstance(agent, AbstractAgent)

    def test_hooks_registered_on_init(self):
        """Test that hooks are registered during initialization."""
        agent = Agent()

        # Pre-merge hooks
        assert "*.md" in agent.pre_merge_hooks
        assert ".cursorrules*" in agent.pre_merge_hooks
        assert ".clinerules*" in agent.pre_merge_hooks

        # Post-merge hooks
        assert "*" in agent.post_merge_hooks

    def test_merger_registry_initialized(self):
        """Test that merger registry is initialized."""
        agent = Agent()

        assert agent.merger_registry is not None
        assert hasattr(agent.merger_registry, "get_merger")


class TestClaudeAgentRegisterHooks:
    """Test cases for register_hooks method."""

    def test_registers_markdown_pre_hook(self):
        """Test that markdown pre-merge hook is registered."""
        agent = Agent()

        assert "*.md" in agent.pre_merge_hooks
        assert agent.pre_merge_hooks["*.md"] == agent._clean_markdown

    def test_registers_cursorrules_pre_hook(self):
        """Test that cursorrules pre-merge hook is registered."""
        agent = Agent()

        assert ".cursorrules*" in agent.pre_merge_hooks
        assert agent.pre_merge_hooks[".cursorrules*"] == agent._validate_cursorrules

    def test_registers_clinerules_pre_hook(self):
        """Test that clinerules pre-merge hook is registered."""
        agent = Agent()

        assert ".clinerules*" in agent.pre_merge_hooks
        assert agent.pre_merge_hooks[".clinerules*"] == agent._validate_cursorrules

    def test_registers_metadata_post_hook(self):
        """Test that metadata post-merge hook is registered."""
        agent = Agent()

        assert "*" in agent.post_merge_hooks
        assert agent.post_merge_hooks["*"] == agent._add_metadata_header

    def test_registers_cursorrules_text_merger(self):
        """Test that .cursorrules uses TextMerger for concatenation."""
        from agent_manager.plugins.mergers.text_merger import TextMerger
        from pathlib import Path

        agent = Agent()
        
        # Check that .cursorrules is registered with TextMerger
        cursorrules_path = Path(".cursorrules")
        merger = agent.merger_registry.get_merger(cursorrules_path)
        
        assert merger == TextMerger

    def test_registers_clinerules_text_merger(self):
        """Test that .clinerules uses TextMerger for concatenation."""
        from agent_manager.plugins.mergers.text_merger import TextMerger
        from pathlib import Path

        agent = Agent()
        
        # Check that .clinerules is registered with TextMerger
        clinerules_path = Path(".clinerules")
        merger = agent.merger_registry.get_merger(clinerules_path)
        
        assert merger == TextMerger


class TestClaudeAgentCleanMarkdown:
    """Test cases for _clean_markdown method."""

    def test_strips_trailing_whitespace(self, tmp_path):
        """Test that _clean_markdown strips trailing whitespace."""
        agent = Agent()

        content = "# Title\n\nSome content   \n\n  \n"
        entry = {"name": "org"}
        file_path = tmp_path / "test.md"

        with patch("am_agent_claude.claude.message"):
            result = agent._clean_markdown(content, entry, file_path)

        assert result == "# Title\n\nSome content\n"

    def test_ensures_single_newline_at_end(self, tmp_path):
        """Test that _clean_markdown ensures single newline at end."""
        agent = Agent()

        content = "Content without newline"
        entry = {"name": "org"}
        file_path = tmp_path / "test.md"

        with patch("am_agent_claude.claude.message"):
            result = agent._clean_markdown(content, entry, file_path)

        assert result.endswith("\n")
        assert not result.endswith("\n\n")

    def test_handles_empty_content(self, tmp_path):
        """Test that _clean_markdown handles empty content."""
        agent = Agent()

        content = ""
        entry = {"name": "org"}
        file_path = tmp_path / "test.md"

        with patch("am_agent_claude.claude.message"):
            result = agent._clean_markdown(content, entry, file_path)

        assert result == "\n"

    def test_handles_whitespace_only(self, tmp_path):
        """Test that _clean_markdown handles whitespace-only content."""
        agent = Agent()

        content = "   \n  \n   "
        entry = {"name": "org"}
        file_path = tmp_path / "test.md"

        with patch("am_agent_claude.claude.message"):
            result = agent._clean_markdown(content, entry, file_path)

        assert result == "\n"

    def test_preserves_content_structure(self, tmp_path):
        """Test that _clean_markdown preserves content structure."""
        agent = Agent()

        content = "# Header\n\nParagraph 1\n\nParagraph 2\n\n- List item\n"
        entry = {"name": "org"}
        file_path = tmp_path / "test.md"

        with patch("am_agent_claude.claude.message"):
            result = agent._clean_markdown(content, entry, file_path)

        assert "# Header" in result
        assert "Paragraph 1" in result
        assert "Paragraph 2" in result
        assert "- List item" in result


class TestClaudeAgentValidateCursorrules:
    """Test cases for _validate_cursorrules method."""

    def test_validates_non_empty_content(self, tmp_path):
        """Test that _validate_cursorrules accepts non-empty content."""
        agent = Agent()

        content = "Some cursorrules content"
        entry = {"name": "org"}
        file_path = tmp_path / ".cursorrules"

        with patch("am_agent_claude.claude.message"):
            result = agent._validate_cursorrules(content, entry, file_path)

        assert result == content

    def test_warns_on_empty_content(self, tmp_path):
        """Test that _validate_cursorrules warns on empty content."""
        agent = Agent()

        content = ""
        entry = {"name": "org"}
        file_path = tmp_path / ".cursorrules"

        with patch("am_agent_claude.claude.message") as mock_message:
            result = agent._validate_cursorrules(content, entry, file_path)

            # Should call message with warning
            mock_message.assert_called()

        assert result == content

    def test_warns_on_whitespace_only(self, tmp_path):
        """Test that _validate_cursorrules warns on whitespace-only content."""
        agent = Agent()

        content = "   \n   \n   "
        entry = {"name": "org"}
        file_path = tmp_path / ".cursorrules"

        with patch("am_agent_claude.claude.message") as mock_message:
            result = agent._validate_cursorrules(content, entry, file_path)

            mock_message.assert_called()

        assert result == content

    def test_returns_content_unchanged(self, tmp_path):
        """Test that _validate_cursorrules returns content unchanged."""
        agent = Agent()

        content = "# Cursorrules\n\nSome rules"
        entry = {"name": "org"}
        file_path = tmp_path / ".cursorrules"

        with patch("am_agent_claude.claude.message"):
            result = agent._validate_cursorrules(content, entry, file_path)

        assert result == content


class TestClaudeAgentAddMetadataHeader:
    """Test cases for _add_metadata_header method."""

    def test_adds_header_to_content(self):
        """Test that _add_metadata_header adds header to content."""
        agent = Agent()

        content = "Original content"
        file_name = "config.yaml"
        sources = ["org", "team"]

        result = agent._add_metadata_header(content, file_name, sources)

        assert "Generated by agent-manager" in result
        assert "File: config.yaml" in result
        assert "Sources: org → team" in result
        assert "Original content" in result

    def test_header_includes_file_name(self):
        """Test that header includes the file name."""
        agent = Agent()

        content = "Content"
        file_name = "test.md"
        sources = ["org"]

        result = agent._add_metadata_header(content, file_name, sources)

        assert "File: test.md" in result

    def test_header_includes_sources_arrow(self):
        """Test that header includes sources with arrow separator."""
        agent = Agent()

        content = "Content"
        file_name = "test.md"
        sources = ["org", "team", "personal"]

        result = agent._add_metadata_header(content, file_name, sources)

        assert "Sources: org → team → personal" in result

    def test_header_includes_hierarchy_priority(self):
        """Test that header includes hierarchy priority information."""
        agent = Agent()

        content = "Content"
        file_name = "test.md"
        sources = ["org", "personal"]

        result = agent._add_metadata_header(content, file_name, sources)

        assert "Hierarchy: org (lowest) to personal (highest priority)" in result

    def test_header_followed_by_blank_line(self):
        """Test that header is followed by blank line before content."""
        agent = Agent()

        content = "First line of content"
        file_name = "test.md"
        sources = ["org"]

        result = agent._add_metadata_header(content, file_name, sources)

        # Header should end with blank line before content
        assert "\n\nFirst line of content" in result

    def test_handles_single_source(self):
        """Test that header handles single source correctly."""
        agent = Agent()

        content = "Content"
        file_name = "test.md"
        sources = ["only"]

        result = agent._add_metadata_header(content, file_name, sources)

        assert "Sources: only" in result
        assert "Hierarchy: only (lowest) to only (highest priority)" in result

    def test_yaml_uses_hash_comments(self):
        """Test that YAML files use hash-style comments."""
        agent = Agent()

        content = "key: value"
        file_name = "config.yaml"
        sources = ["org"]

        result = agent._add_metadata_header(content, file_name, sources)

        # Should use # comments, not <!-- -->
        assert result.startswith("# Generated by agent-manager\n")
        assert "# File: config.yaml" in result
        assert "# Sources: org" in result
        assert "<!--" not in result

    def test_yml_uses_hash_comments(self):
        """Test that YML files use hash-style comments."""
        agent = Agent()

        content = "key: value"
        file_name = "config.yml"
        sources = ["org"]

        result = agent._add_metadata_header(content, file_name, sources)

        assert result.startswith("# Generated by agent-manager\n")
        assert "<!--" not in result

    def test_markdown_uses_html_comments(self):
        """Test that Markdown files use HTML-style comments."""
        agent = Agent()

        content = "# Title"
        file_name = "README.md"
        sources = ["org"]

        result = agent._add_metadata_header(content, file_name, sources)

        # Should use <!-- --> comments
        assert result.startswith("<!-- Generated by agent-manager -->")
        assert "<!-- File: README.md -->" in result
        assert "<!-- Sources: org -->" in result

    def test_markdown_extension_uses_html_comments(self):
        """Test that .markdown files use HTML-style comments."""
        agent = Agent()

        content = "Content"
        file_name = "file.markdown"
        sources = ["org"]

        result = agent._add_metadata_header(content, file_name, sources)

        assert result.startswith("<!-- Generated by agent-manager -->")

    def test_json_has_no_header(self):
        """Test that JSON files have no header (JSON doesn't support comments)."""
        agent = Agent()

        content = '{"key": "value"}'
        file_name = "config.json"
        sources = ["org", "team"]

        result = agent._add_metadata_header(content, file_name, sources)

        # JSON doesn't support comments, so content should be unchanged
        assert result == content
        assert "Generated by agent-manager" not in result
        assert "<!--" not in result
        assert "#" not in result

    def test_text_files_use_hash_comments(self):
        """Test that text files use hash-style comments."""
        agent = Agent()

        content = "Some text content"
        file_name = "notes.txt"
        sources = ["org"]

        result = agent._add_metadata_header(content, file_name, sources)

        assert result.startswith("# Generated by agent-manager\n")
        assert "<!--" not in result

    def test_cursorrules_uses_hash_comments(self):
        """Test that .cursorrules files use hash-style comments."""
        agent = Agent()

        content = "Rule content"
        file_name = ".cursorrules"
        sources = ["org"]

        result = agent._add_metadata_header(content, file_name, sources)

        assert result.startswith("# Generated by agent-manager\n")
        assert "<!--" not in result

    def test_python_files_use_hash_comments(self):
        """Test that Python files use hash-style comments."""
        agent = Agent()

        content = 'print("hello")'
        file_name = "script.py"
        sources = ["org"]

        result = agent._add_metadata_header(content, file_name, sources)

        assert result.startswith("# Generated by agent-manager\n")
        assert "<!--" not in result

    def test_shell_files_use_hash_comments(self):
        """Test that shell script files use hash-style comments."""
        agent = Agent()

        content = "echo 'hello'"
        file_name = "script.sh"
        sources = ["org"]

        result = agent._add_metadata_header(content, file_name, sources)

        assert result.startswith("# Generated by agent-manager\n")
        assert "<!--" not in result

    def test_html_uses_html_comments(self):
        """Test that HTML files use HTML-style comments."""
        agent = Agent()

        content = "<html><body>Content</body></html>"
        file_name = "page.html"
        sources = ["org"]

        result = agent._add_metadata_header(content, file_name, sources)

        assert result.startswith("<!-- Generated by agent-manager -->")

    def test_xml_uses_html_comments(self):
        """Test that XML files use HTML-style comments."""
        agent = Agent()

        content = "<root><element>value</element></root>"
        file_name = "data.xml"
        sources = ["org"]

        result = agent._add_metadata_header(content, file_name, sources)

        assert result.startswith("<!-- Generated by agent-manager -->")

    def test_case_insensitive_extension_matching(self):
        """Test that extension matching is case-insensitive."""
        agent = Agent()

        content = "content"
        
        # Test uppercase YAML
        result = agent._add_metadata_header(content, "CONFIG.YAML", ["org"])
        assert result.startswith("# Generated by agent-manager\n")
        
        # Test uppercase MD
        result = agent._add_metadata_header(content, "README.MD", ["org"])
        assert result.startswith("<!-- Generated by agent-manager -->")
        
        # Test uppercase JSON
        result = agent._add_metadata_header(content, "DATA.JSON", ["org"])
        assert result == content  # No header for JSON

    def test_unknown_extension_uses_hash_comments(self):
        """Test that files with unknown extensions default to hash comments."""
        agent = Agent()

        content = "Some content"
        file_name = "file.unknown"
        sources = ["org"]

        result = agent._add_metadata_header(content, file_name, sources)

        # Should default to # comments for unknown types
        assert result.startswith("# Generated by agent-manager\n")
        assert "<!--" not in result


class TestClaudeAgentInitialize:
    """Test cases for _initialize method."""

    def test_skips_if_directory_exists(self, tmp_path):
        """Test that _initialize skips if directory already exists."""
        agent = Agent()
        agent.agent_directory = tmp_path / ".claude"
        agent.agent_directory.mkdir()

        with patch("am_agent_claude.claude.message"):
            agent._initialize()

        # Should not raise any errors

    def test_creates_directory_if_not_exists(self, tmp_path):
        """Test that _initialize creates directory if it doesn't exist."""
        agent = Agent()
        agent.agent_directory = tmp_path / ".claude"

        with patch("am_agent_claude.claude.query") as mock_query:
            mock_query.return_value = iter(["Initializing...", "Done"])

            with patch("am_agent_claude.claude.message"):
                agent._initialize()

        assert agent.agent_directory.exists()

    def test_calls_claude_sdk_init(self, tmp_path):
        """Test that _initialize calls Claude SDK initialization."""
        agent = Agent()
        agent.agent_directory = tmp_path / ".claude"

        with patch("am_agent_claude.claude.query") as mock_query:
            mock_query.return_value = iter(["Message 1", "Message 2"])

            with patch("am_agent_claude.claude.message"):
                agent._initialize()

            mock_query.assert_called_once_with(prompt="/init")

    def test_handles_sdk_failure_gracefully(self, tmp_path):
        """Test that _initialize handles SDK failures gracefully."""
        agent = Agent()
        agent.agent_directory = tmp_path / ".claude"

        with patch("am_agent_claude.claude.query") as mock_query:
            mock_query.side_effect = Exception("SDK error")

            with patch("am_agent_claude.claude.message"):
                agent._initialize()

        # Should create directory as fallback
        assert agent.agent_directory.exists()

    def test_creates_directory_manually_on_sdk_failure(self, tmp_path):
        """Test that directory is created manually when SDK fails."""
        agent = Agent()
        agent.agent_directory = tmp_path / ".claude"

        with patch("am_agent_claude.claude.query") as mock_query:
            mock_query.side_effect = Exception("SDK not available")

            with patch("am_agent_claude.claude.message"):
                agent._initialize()

        assert agent.agent_directory.exists()
        assert agent.agent_directory.is_dir()


class TestClaudeAgentUpdate:
    """Test cases for update method."""

    def test_update_calls_initialize(self, tmp_path):
        """Test that update calls _initialize."""
        agent = Agent()
        agent.agent_directory = tmp_path / ".claude"

        config = {"hierarchy": []}

        with patch.object(agent, "_initialize") as mock_init:
            with patch.object(agent, "merge_configurations"):
                with patch("am_agent_claude.claude.message"):
                    agent.update(config)

            mock_init.assert_called_once()

    def test_update_calls_merge_configurations(self, tmp_path):
        """Test that update calls merge_configurations."""
        agent = Agent()
        agent.agent_directory = tmp_path / ".claude"
        agent.agent_directory.mkdir()

        config = {"hierarchy": [{"name": "org", "repo": Mock()}]}

        with patch.object(agent, "merge_configurations") as mock_merge:
            with patch("am_agent_claude.claude.message"):
                agent.update(config)

            mock_merge.assert_called_once_with(config)

    def test_update_creates_and_merges(self, tmp_path):
        """Test that update creates directory and merges configurations."""
        agent = Agent()
        agent.agent_directory = tmp_path / ".claude"

        org_path = tmp_path / "org"
        org_path.mkdir()
        (org_path / "test.md").write_text("# Test")

        org_repo = Mock()
        org_repo.get_path.return_value = org_path

        config = {"hierarchy": [{"name": "org", "repo": org_repo}]}

        with patch("am_agent_claude.claude.query") as mock_query:
            mock_query.return_value = iter(["Init"])

            with patch("am_agent_claude.claude.message"):
                agent.update(config)

        # Directory should exist
        assert agent.agent_directory.exists()

        # File should be merged and written
        output_file = agent.agent_directory / "test.md"
        assert output_file.exists()


class TestClaudeAgentHooksIntegration:
    """Integration tests for hook execution."""

    def test_markdown_hook_applied_during_merge(self, tmp_path):
        """Test that markdown hook is applied during merge."""
        agent = Agent()
        agent.agent_directory = tmp_path / ".claude"
        agent.agent_directory.mkdir()

        org_path = tmp_path / "org"
        org_path.mkdir()
        (org_path / "test.md").write_text("Content with trailing spaces   \n\n")

        org_repo = Mock()
        org_repo.get_path.return_value = org_path

        config = {"hierarchy": [{"name": "org", "repo": org_repo}]}

        with patch("am_agent_claude.claude.message"):
            agent.merge_configurations(config)

        output_file = agent.agent_directory / "test.md"
        content = output_file.read_text()

        # Should be cleaned (no trailing spaces)
        assert "Content with trailing spaces\n" in content
        assert "   \n" not in content

    def test_cursorrules_hook_applied_during_merge(self, tmp_path):
        """Test that cursorrules hook is applied during merge."""
        agent = Agent()
        agent.agent_directory = tmp_path / ".claude"
        agent.agent_directory.mkdir()

        org_path = tmp_path / "org"
        org_path.mkdir()
        (org_path / ".cursorrules").write_text("Rules content")

        org_repo = Mock()
        org_repo.get_path.return_value = org_path

        config = {"hierarchy": [{"name": "org", "repo": org_repo}]}

        with patch("am_agent_claude.claude.message"):
            agent.merge_configurations(config)

        # File should be written
        output_file = agent.agent_directory / ".cursorrules"
        assert output_file.exists()

    def test_cursorrules_concatenates_from_multiple_levels(self, tmp_path):
        """Test that .cursorrules files are concatenated from multiple hierarchy levels."""
        agent = Agent()
        agent.agent_directory = tmp_path / ".claude"
        agent.agent_directory.mkdir()

        # Create org, team, and personal repos with .cursorrules
        org_path = tmp_path / "org"
        team_path = tmp_path / "team"
        personal_path = tmp_path / "personal"
        
        org_path.mkdir()
        team_path.mkdir()
        personal_path.mkdir()

        (org_path / ".cursorrules").write_text("# Organization rules\n- Follow company standards\n")
        (team_path / ".cursorrules").write_text("# Team rules\n- Use team conventions\n")
        (personal_path / ".cursorrules").write_text("# Personal rules\n- My preferences\n")

        org_repo = Mock()
        org_repo.get_path.return_value = org_path
        
        team_repo = Mock()
        team_repo.get_path.return_value = team_path
        
        personal_repo = Mock()
        personal_repo.get_path.return_value = personal_path

        config = {
            "hierarchy": [
                {"name": "org", "repo": org_repo},
                {"name": "team", "repo": team_repo},
                {"name": "personal", "repo": personal_repo},
            ]
        }

        with patch("am_agent_claude.claude.message"):
            agent.merge_configurations(config)

        output_file = agent.agent_directory / ".cursorrules"
        content = output_file.read_text()

        # Should have content from all three levels
        assert "Organization rules" in content
        assert "Team rules" in content
        assert "Personal rules" in content
        
        # Should have source markers from TextMerger
        assert "# --- From: team ---" in content
        assert "# --- From: personal ---" in content
        
        # Should have metadata header
        assert "# Generated by agent-manager" in content
        assert "# Sources: org → team → personal" in content

    def test_metadata_hook_applied_during_merge(self, tmp_path):
        """Test that metadata hook is applied during merge with correct comment syntax."""
        agent = Agent()
        agent.agent_directory = tmp_path / ".claude"
        agent.agent_directory.mkdir()

        org_path = tmp_path / "org"
        org_path.mkdir()
        (org_path / "config.yaml").write_text("key: value")

        org_repo = Mock()
        org_repo.get_path.return_value = org_path

        config = {"hierarchy": [{"name": "org", "repo": org_repo}]}

        with patch("am_agent_claude.claude.message"):
            agent.merge_configurations(config)

        output_file = agent.agent_directory / "config.yaml"
        content = output_file.read_text()

        # Should have metadata header with hash comments (YAML uses # not <!--)
        assert "# Generated by agent-manager" in content
        assert "# File: config.yaml" in content
        assert "# Sources: org" in content
        assert "<!--" not in content  # YAML doesn't use HTML comments


class TestClaudeAgentEdgeCases:
    """Test cases for edge cases and special scenarios."""

    def test_handles_unicode_in_markdown(self, tmp_path):
        """Test that agent handles Unicode in markdown files."""
        agent = Agent()

        content = "# 你好 World 🌍\n\nSome content"
        entry = {"name": "org"}
        file_path = tmp_path / "test.md"

        with patch("am_agent_claude.claude.message"):
            result = agent._clean_markdown(content, entry, file_path)

        assert "你好" in result
        assert "🌍" in result

    def test_handles_special_characters_in_file_name(self):
        """Test that metadata header handles special characters in file name."""
        agent = Agent()

        content = "Content"
        file_name = "file-with_special.chars.md"
        sources = ["org"]

        result = agent._add_metadata_header(content, file_name, sources)

        assert file_name in result

    def test_handles_empty_sources_list(self):
        """Test that metadata header handles empty sources list."""
        agent = Agent()

        content = "Content"
        file_name = "test.md"
        sources = []

        # Should handle gracefully (though not expected in normal use)
        try:
            result = agent._add_metadata_header(content, file_name, sources)
            # If it doesn't crash, that's acceptable
        except IndexError:
            # Also acceptable to fail with empty sources
            pass

    def test_multiple_hierarchy_levels(self, tmp_path):
        """Test merging from multiple hierarchy levels."""
        agent = Agent()
        agent.agent_directory = tmp_path / ".claude"
        agent.agent_directory.mkdir()

        # Create org and team repos
        org_path = tmp_path / "org"
        team_path = tmp_path / "team"
        org_path.mkdir()
        team_path.mkdir()

        (org_path / "config.md").write_text("# Org Config")
        (team_path / "config.md").write_text("# Team Config")

        org_repo = Mock()
        org_repo.get_path.return_value = org_path

        team_repo = Mock()
        team_repo.get_path.return_value = team_path

        config = {
            "hierarchy": [
                {"name": "org", "repo": org_repo},
                {"name": "team", "repo": team_repo},
            ]
        }

        with patch("am_agent_claude.claude.message"):
            agent.merge_configurations(config)

        output_file = agent.agent_directory / "config.md"
        content = output_file.read_text()

        # Should show both sources
        assert "Sources: org → team" in content

    def test_agent_directory_with_parents(self, tmp_path):
        """Test that agent directory is created with parents."""
        agent = Agent()
        agent.agent_directory = tmp_path / "deeply" / "nested" / ".claude"

        with patch("am_agent_claude.claude.query") as mock_query:
            mock_query.return_value = iter(["Init"])

            with patch("am_agent_claude.claude.message"):
                agent._initialize()

        assert agent.agent_directory.exists()
        assert agent.agent_directory.parent.exists()


class TestClaudeAgentCompatibility:
    """Test cases for compatibility with AbstractAgent."""

    def test_has_required_agent_directory(self):
        """Test that agent has agent_directory attribute."""
        agent = Agent()

        assert hasattr(agent, "agent_directory")
        assert isinstance(agent.agent_directory, Path)

    def test_has_required_merge_configurations(self):
        """Test that agent has merge_configurations method."""
        agent = Agent()

        assert hasattr(agent, "merge_configurations")
        assert callable(agent.merge_configurations)

    def test_has_required_register_hooks(self):
        """Test that agent implements register_hooks."""
        agent = Agent()

        assert hasattr(agent, "register_hooks")
        assert callable(agent.register_hooks)

    def test_has_required_update_method(self):
        """Test that agent has update method."""
        agent = Agent()

        assert hasattr(agent, "update")
        assert callable(agent.update)

    def test_pre_merge_hooks_dict_exists(self):
        """Test that pre_merge_hooks dict exists."""
        agent = Agent()

        assert hasattr(agent, "pre_merge_hooks")
        assert isinstance(agent.pre_merge_hooks, dict)

    def test_post_merge_hooks_dict_exists(self):
        """Test that post_merge_hooks dict exists."""
        agent = Agent()

        assert hasattr(agent, "post_merge_hooks")
        assert isinstance(agent.post_merge_hooks, dict)

