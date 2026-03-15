# Laws of Simplicity Experiment

This directory contains the experiment runner for the research paper "On the Impact of Laws of Simplicity Skill on the Efficiency of AI Coding Agents."

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run experiment
./scripts/run_experiment.sh

# Analyze results
python scripts/analyze_results.py
```

## Experiment Design

### A/B Controlled Study

- **Control:** Agent with default skills only
- **Treatment:** Agent with Laws of Simplicity skill loaded

Each task is run in both conditions with counterbalanced order to eliminate practice effects.

### Benchmarks

- **SWE-bench Lite:** 100 tasks (real-world GitHub issues)
- **HumanEval:** 100 tasks (function-level coding problems)

### Metrics

| Metric | Definition |
|--------|------------|
| Input tokens | Tokens sent to model |
| Output tokens | Tokens generated |
| Success rate | Tasks passing test suite |
| Time | Wall-clock time per task |
| Iterations | Number of agent reasoning cycles |

### Statistical Analysis

- **RQ1 (Token reduction):** Paired t-test, Cohen's d effect size
- **RQ2 (Success rate):** McNemar's test for paired binary outcomes
- **RQ3 (By difficulty):** Two-way ANOVA (Condition xComplexity)

## Directory Structure

```
ai-laws-of-simplicity/
├── experiment/
│   ├── runner.py           # Main orchestrator
│   ├── config.py           # Configuration
│   ├── harness/            # Benchmark harnesses│   │   ├── base.py         # Abstract base
│   │   ├── swe_bench.py    # SWE-bench implementation
│   │   └── humaneval.py    # HumanEval implementation
│   ├── metrics/            # Collection and analysis
│   │   ├── collector.py    # Metrics collection
│   │   └── analyzer.py     # Statistical analysis
│   └── utils/
│       └── isolation.py    # Process isolation
├── data/
│   ├── raw/                # Per-task JSON logs
│   └── results/            # Aggregated CSV
├── scripts/
│   ├── run_experiment.sh   # Entry point
│   └── analyze_results.py  # Post-processing
├── skills/
│   └── laws-of-simplicity/
│       └── SKILL.md        # The skill being tested
├── requirements.txt        # Python dependencies
└── Dockerfile              # Reproducibility container
```

## Reproducibility

### Docker

```bash
docker build -t simplicity-experiment .
docker run -v $(pwd)/data:/app/data simplicity-experiment
```

### Configuration

Edit `experiment/config.py` to modify:
- Number of tasks per benchmark
- Timeout settings
- Agent model
- Skill configurations

## Citation

If you use this experiment framework, please cite:

```bibtex
@article{simplicity2026,
  title={On the Impact of Laws of Simplicity Skill on the Efficiency of AI Coding Agents},
  author={...},
  journal={arXiv preprint},
  year={2026}
}
```

## License

MIT License