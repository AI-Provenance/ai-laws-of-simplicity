# AI Laws of Simplicity

A standalone skill that guides AI agents to apply [John Maeda's 10 Laws of Simplicity](https://lawsofsimplicity.com/) throughout the software development lifecycle.

## Overview

This repository contains a skill for AI coding agents that helps them apply the principles from John Maeda's "The Laws of Simplicity" to software development. The skill provides actionable guidelines for each of the 10 Laws that agents can invoke at various stages of development to ensure simplicity principles are considered from planning through implementation and review.

## The 10 Laws of Simplicity

1. **REDUCE**: The simplest way to achieve simplicity is through thoughtful reduction.
2. **ORGANIZE**: Organization makes a system of many appear fewer.
3. **TIME**: Savings in time feel like simplicity.
4. **LEARN**: Knowledge makes everything simpler.
5. **DIFFERENCES**: Simplicity and complexity need each other.
6. **CONTEXT**: What lies in the periphery of simplicity is definitely not peripheral.
7. **EMOTION**: More emotions are better than less.
8. **TRUST**: In simplicity we trust.
9. **FAILURE**: Some things can never be made simple.
10. **THE ONE**: Simplicity is about subtracting the obvious, and adding the meaningful.

## Installation

To install this skill in your AI coding agent, use one of the following methods based on your platform:

### For OpenCode Users

Tell OpenCode to fetch and follow the installation instructions from this repository:
```
Fetch and follow instructions from https://raw.githubusercontent.com/AI-Provenance/ai-laws-of-simplicity/main/INSTALL.md
```

### For Other Platforms

See the [INSTALL.md](INSTALL.md) file for detailed, agent-agnostic installation instructions.

## Model Configuration

The experiment supports multiple LLM providers:

### Using Anthropic (Claude)

```bash
export ANTHROPIC_API_KEY="your-key-here"

uv run python -m experiment.runner \
  --model "anthropic/claude-3-5-sonnet-20241022" \
  --benchmarks swe_bench_lite \
  --num-tasks 5
```

### Using OpenAI (GPT)

```bash
export OPENAI_API_KEY="your-key-here"

uv run python -m experiment.runner \
  --model "openai/gpt-4-turbo" \
  --benchmarks swe_bench_lite \
  --num-tasks 5
```

### Using OpenRouter (Multi-Provider)

```bash
export OPENROUTER_API_KEY="your-key-here"

uv run python -m experiment.runner \
  --model "openrouter/anthropic/claude-3.5-sonnet" \
  --benchmarks swe_bench_lite \
  --num-tasks 5
```

### Programmatic Usage

```python
from experiment.config import ExperimentConfig
from experiment.runner import ExperimentRunner

config = ExperimentConfig(
    benchmarks=["swe_bench_lite"],
    num_tasks_per_benchmark=5,
    runner_type="api",
    model_string="anthropic/claude-3-5-sonnet-20241022",
)

runner = ExperimentRunner(config)
runner.run()
```

### Switching Back to OpenCode CLI

To use the original OpenCode integration:

```python
config = ExperimentConfig(
    runner_type="cli",
    agent_model="opencode-go/glm-5",
)
```

## Usage

Once installed, activate the skill in your agent:

```
skill laws-of-simplicity
```

The skill will provide guidance on applying the Laws of Simplicity to your current development task.

## When to Use This Skill

Consider invoking this skill:

1. At the beginning of any development task
2. Before making significant architectural decisions
3. When evaluating different implementation approaches
4. Before submitting code for review
5. After completing a task to reflect on simplicity principles applied

## Files in This Repository

- `skills/laws-of-simplicity/SKILL.md` - The skill file containing the Laws of Simplicity guidelines
- `INSTALL.md` - Generic installation guide for any AI coding agent

## License

This skill is based on "The Laws of Simplicity" by John Maeda. Please refer to the original work for licensing information.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.