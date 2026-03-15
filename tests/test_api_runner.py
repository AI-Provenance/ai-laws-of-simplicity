from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from experiment.utils.api_runner import APIRunner
from experiment.providers import ModelConfig, CompletionResponse


@pytest.fixture
def mock_provider():
    """Create a mock provider that returns fake responses."""
    provider = Mock()
    provider.get_model_name.return_value = "test/model"
    provider.complete.return_value = CompletionResponse(
        content="Test solution code",
        input_tokens=100,
        output_tokens=50,
        total_tokens=150,
        model="test/model",
    )
    return provider


def test_api_runner_without_skills(mock_provider):
    """Test APIRunner without any skills loaded."""
    with patch(
        "experiment.utils.api_runner.create_provider", return_value=mock_provider
    ):
        config = ModelConfig(provider="test", model="model")
        runner = APIRunner(config)

        ctx = runner.create_fresh_context(skills=None)
        assert ctx["skill_content"] == ""

        result = runner.run_agent(ctx, "Write hello world")

        assert result["input_tokens"] == 100
        assert result["output_tokens"] == 50
        assert result["iterations"] == 1
        assert "Test solution code" in result["output"]


def test_api_runner_with_skills(mock_provider, tmp_path):
    """Test APIRunner with skill injection."""
    skill_file = tmp_path / "test-skill.md"
    skill_file.write_text("# Test Skill\n\nAlways write clean code.")

    with patch(
        "experiment.utils.api_runner.create_provider", return_value=mock_provider
    ):
        config = ModelConfig(provider="test", model="model")
        runner = APIRunner(config)

        ctx = runner.create_fresh_context(skills=[skill_file])
        assert "Test Skill" in ctx["skill_content"]
        assert "clean code" in ctx["skill_content"]

        result = runner.run_agent(ctx, "Write hello world")

        call_args = mock_provider.complete.call_args
        assert call_args[1]["system_prompt"] is not None
        assert "Test Skill" in call_args[1]["system_prompt"]
