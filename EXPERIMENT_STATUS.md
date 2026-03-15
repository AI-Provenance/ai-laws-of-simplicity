# Laws of Simplicity Experiment Status

**Last Updated:** 2026-03-15
**Status:** ✅ **READY FOR EXECUTION**

---

## Recent Changes

### 2026-03-15: Direct API Integration

Switched from OpenCode CLI integration to direct LLM API calls:

- **Why**: OpenCode doesn't support batch mode; needed clean token tracking
- **What**: Added provider abstraction layer supporting Anthropic, OpenAI, OpenRouter
- **How**: Created `experiment/providers/` module with unified interface
- **Impact**: Can now run experiments with any LLM provider/model with accurate token tracking

### Provider Architecture

```
experiment/providers/
├── base.py              # LLMProvider abstract base class
├── config.py            # ModelConfig for flexible model selection
├── anthropic_provider.py
├── openai_provider.py
├── litellm_provider.py  # Universal provider via LiteLLM
└── __init__.py          # Factory: create_provider()
```

### Migration from CLI to API

**Before**:
- Calls `opencode --no-tui` subprocess
- Extracts tokens from OpenCode SQLite database
- Limited to OpenCode-supported models

**After**:
- Direct SDK calls (anthropic, openai, litellm)
- Tokens from API response objects
- Any model/provider supported

---

## Summary

Complete implementation of an automated A/B experiment runner to measure the impact of the Laws of Simplicity skill on AI coding agent token efficiency.

## Implementation Complete

| Component | Status | Description |
|-----------|--------|-------------|
| Package Management | ✅ | uv-based, Python 3.11+, all dependencies installed |
| Configuration | ✅ | ExperimentConfig with power analysis (n=100, d=0.3) |
| Benchmark Harnesses | ✅ | SWE-bench Lite & HumanEval support |
| Metrics Collection | ✅ | Token, time, success, iteration tracking |
| Statistical Analysis | ✅ | Paired t-test, McNemar's, two-way ANOVA |
| Token Extraction | ✅ | OpenCode SQLite database integration |
| Process Isolation | ✅ | Fresh context per run |
| Entry Scripts | ✅ | `scripts/run_experiment.sh`, `scripts/analyze_results.py` |
| Docker | ✅ | Reproducibility container |
| Documentation | ✅ | README, experiment/README.md, TOKEN_EXTRACTION.md |

## Validation Results

```
✓ All module imports successful
✓ Class instantiation works
✓ Analysis pipeline: Paired t-test, McNemar's, ANOVA
✓ Token extraction from OpenCode database
✓ Metrics collection and CSV export
✓ Mock experiment flow validated
```

## Research Design

### A/B Controlled Study

- **Control:** Agent with default skills only
- **Treatment:** Agent with Laws of Simplicity skill loaded (`skills/laws-of-simplicity/SKILL.md`)
- **Counterbalancing:** `hash(task_id) % 2` determines condition order
- **Sample Size:** 100 tasks per benchmark (powered for Cohen's d=0.3)

### Benchmarks

- **SWE-bench Lite:** Real-world GitHub issues
- **HumanEval:** Function-level coding problems

### Metrics

| Metric | Type | Measurement |
|--------|------|-------------|
| Input tokens | Primary | OpenCode database query |
| Output tokens | Primary | OpenCode database query |
| Success rate | Secondary | Test suite verification |
| Time-to-completion | Secondary | Wall-clock time |
| Iterations | Secondary | Agent reasoning cycles |

### Statistical Analysis

- **RQ1 (Token reduction):** Paired t-test, Cohen's d, bootstrap 95% CI
- **RQ2 (Success rate):** McNemar's test for paired binary outcomes
- **RQ3 (By difficulty):** Two-way ANOVA (Condition × Complexity)
- **Time distribution:** Mann-Whitney U test, rank-biserial correlation

## Running the Experiment

### Quick Start

```bash
# Navigate to project directory
cd ai-laws-of-simplicity

# Run experiment (full 100 tasks per benchmark)
uv run python -m experiment.runner

# Or use the shell script
./scripts/run_experiment.sh

# Analyze results and generate figures
uv run python scripts/analyze_results.py
```

### Configuration

Edit `experiment/config.py` to modify:
- Number of tasks per benchmark
- Timeout settings (default: 600s)
- Agent model
- Skill configurations

### Docker (Reproducible)

```bash
docker build -t simplicity-experiment .
docker run -v $(pwd)/data:/app/data simplicity-experiment
```

## Output Files

After running the experiment:

```
data/
├── raw/
│   ├── task_0_control.json      # Per-task JSON logs
│   ├── task_0_treatment.json
│   └── ...
└── results/
    ├── aggregate_results.csv    # Combined results
    ├── task_metadata.json        # Task difficulty, repo, etc.
    ├── analysis.json             # Statistical analysis
    └── figures/
        ├── figure1_token_distribution.png
        └── figure2_time_distribution.png
```

## Known Limitations

### Benchmark Data Availability

- **HumanEval:** Dataset `openai/humaneval` not available on HuggingFace Hub
  - **Workaround:** Focus on SWE-bench Lite only, or download HumanEval separately
- **SWE-bench:** Uses `princeton-nlp/SWE-bench_Lite` (available)

### Token Extraction

- Relies on OpenCode SQLite database at `~/.local/share/opencode/opencode.db`
- Query returns messages created after `start_time`
- Cache read/write tokens tracked separately (not included in primary analysis)

### Verification Stubs

- `verify_solution()` in both harnesses requires real benchmark test runners
- Current implementation returns success based on return code only
- **Action needed:** Integrate with actual SWE-bench/HumanEval test harnesses

## Next Steps

### 1. Pilot Experiment (Recommended)

Run a small pilot to validate end-to-end:

```bash
# Create a test configuration
uv run python -c "
from experiment.config import ExperimentConfig
from experiment.runner import ExperimentRunner

config = ExperimentConfig(
    benchmarks=['swe_bench_lite'],
    num_tasks_per_benchmark=5,  # Just 5 tasks
    timeout_seconds=300,  # 5 minutes per task
)

runner = ExperimentRunner(config)
runner.run()
runner.analyze()
"
```

### 2. Full Experiment

After validating the pilot:

```bash
uv run python -m experiment.runner
```

Expected runtime:
- 100 tasks × 2 conditions × 600s timeout = ~33 hours maximum
- Actual time likely 10-15 hours depending on task complexity

### 3. Analysis & Paper

After experiment completion:

```bash
# Generate figures and statistical analysis
uv run python scripts/analyze_results.py

# Review results
cat data/results/analysis.json
```

Then proceed to:
- Write paper sections (Introduction, Background, Results, Discussion)
- Create additional figures as needed
- Submit to arXiv

## Troubleshooting

### No tokens recorded

- Check OpenCode database exists: `ls ~/.local/share/opencode/opencode.db`
- Verify messages are being created: `sqlite3 ~/.local/share/opencode/opencode.db "SELECT COUNT(*) FROM message;"`
- Check logs in `data/raw/` for error messages

### Tasks timing out

- Increase `timeout_seconds` in config
- Check task difficulty distribution: `cat data/results/task_metadata.json`

### Analysis fails

- Ensure paired data exists for all tasks
- Check CSV has both control and treatment rows per task_id
- Verify metadata JSON is valid

## Contact

For issues or questions about the experiment framework:
- Create an issue in the repository
- Check `experiment/README.md` for detailed documentation
- Review `TOKEN_EXTRACTION.md` for token tracking details

---

**Ready to proceed with experiment execution.**
