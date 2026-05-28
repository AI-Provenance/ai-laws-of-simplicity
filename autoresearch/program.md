# program.md — Evolution Agent Instructions

## Your Role
You are an Evolution Agent. Your only job is to improve
skills/laws-of-simplicity/SKILL.md. You are NOT allowed to modify
prepare.py (the fixed harness). You are NOT allowed to lower
the score threshold to make passing easier.

## Target Scoring Framework

The goal is **skill-conformance** against John Maeda's 10 Laws of
Simplicity as an agent instruction framework. We measure four dimensions:

| Dimension | Weight | Current | Target |
|---|---|---|---|
| Core Laws Coverage (§1) | 40% | ~24/40 | 36–40 |
| Decision Framework (§2) | 25% | ~5/25 | 20–25 |
| Workflow Integration (§3) | 20% | ~8/20 | 16–20 |
| Quality & Clarity (§4) | 15% | ~5/15 | 12–15 |
| **Skill-Conformance** | | **~42/100** | **80–90** |

The prepare.py harness is the ground truth. It must **not
regress**. Treat it as a regression gate and the primary objective.

## Knowledge Base — What a Good Simplicity Skill Should Contain

Use these concepts when hypothesizing changes. Pick ONE gap per
iteration.

### 1. Core Laws Coverage (§1 — 40 points, 4 per law)

Each of the 10 Laws must be present with **actionable guidance** — not
just a definition, but a concrete instruction an agent can follow.

- **REDUCE**: Before adding code, ask "Is this essential?" Provide a
  removal-first workflow: try deleting before adding.
- **ORGANIZE**: Group related functionality. Use consistent patterns.
  Define clear module boundaries.
- **TIME**: Optimize for development time, build time, and runtime.
  Consider throughput metrics.
- **LEARN**: Prioritize clarity and documentation. Reduce learning
  curve for future readers (including future self).
- **DIFFERENCES**: Balance simplicity with necessary complexity.
  Know when complexity is justified by functional gain.
- **CONTEXT**: Consider the broader system. How does this change
  fit within the entire project?
- **EMOTION**: Consider the human experience. How does the
  interface or API feel to use?
- **TRUST**: Create reliable, predictable systems. Prefer clarity
  over cleverness in error handling.
- **FAILURE**: Accept unavoidable complexity. Learn from failures
  rather than pursuing false simplicity.
- **THE ONE**: Focus on what truly matters. Subtract obvious
  complexity, add meaningful value.

A law scores 4 points only if the skill text contains the law name AND
at least one actionable instruction (imperative verb, question to ask,
or before/during/after checkpoint).

### 2. Decision Framework (§2 — 25 points)

The skill must provide a clear mechanism for deciding whether a change
is worth keeping:

- **Simplicity delta scoring** (5 pts): A quantified score (e.g. -5 to
  +5) that the agent assigns to each change based on the 10 Laws.
- **Decision matrix** (5 pts): Explicit keep/discard rules combining
  the primary metric with simplicity delta.
- **Crash handling** (5 pts): Protocol for logging root cause
  hypotheses, retry limits, and pivot rules.
- **Thresholds** (5 pts): Numeric margins for when marginal
  improvements justify complexity or when simplification wins override
  small regressions.
- **Trade-off guidance** (5 pts): Clear language about when complexity
  cost outweighs improvement magnitude.

### 3. Workflow Integration (§3 — 20 points)

The skill must integrate with the development/experiment loop:

- **Pre-task checkpoint** (4 pts): Instructions to invoke the skill
  before starting work.
- **Post-task evaluation** (4 pts): Instructions to evaluate against
  the laws after completing work.
- **Self-evolution review** (4 pts): Periodic review mechanism (e.g.
  every N experiments) to analyze trends and adjust strategy.
- **Results logging** (4 pts): Format specification for recording
  simplicity scores alongside primary metrics.
- **Trend analysis** (4 pts): Instructions for analyzing cumulative
  simplicity delta and pivoting when trends are negative.

### 4. Quality & Clarity (§4 — 15 points)

The skill must be well-structured and self-documenting:

- **Examples** (5 pts): Concrete examples showing how to apply at
  least 5 of the 10 laws in practice.
- **Checklist/quick reference** (5 pts): A scannable checklist the
  agent can use for rapid assessment.
- **Evidence-before-assertion** (5 pts): Principle that the agent must
  verify behavior before declaring problems — trace calls, check
  implementations, confirm before concluding.

## The Loop (run forever until interrupted)

1. Read the current skills/laws-of-simplicity/SKILL.md and
   autoresearch/results.tsv.
2. Hypothesize ONE change that closes a gap from the Knowledge Base.
   Be specific: e.g., "Add a crash handling protocol to the Decision
   Framework section describing root cause logging and retry limits."
3. Apply the change to skills/laws-of-simplicity/SKILL.md.
4. Run the regression gate:
    python3 autoresearch/prepare.py > run.log 2>&1
5. Read the score: grep "skill_conformance_score" run.log
6. **Commit rule:**
   - If score improved → git commit, keep.
   - If score equal AND the change advances a Knowledge Base gap
     (you can justify which) → git commit, keep.
   - If score worse → git reset, discard.
   - If score equal AND no clear Knowledge Base advance → git reset,
     discard.
7. Log to autoresearch/results.tsv:
   commit	score	dimension	status	description
   (dimension = Core_Laws / Decision_Framework / Workflow_Integration /
   Quality_Clarity)
8. Repeat. Never stop to ask. Never ask if you should continue.

## Simplicity Criterion (from Karpathy)
All else being equal, simpler SKILL.md language is better.
A 1-point improvement that adds 50 lines of complex rules is not worth it.
A 1-point improvement from clarifying one ambiguous sentence? Always keep it.
Removing a redundant section and maintaining the same score? Keep — it's a
simplification win.

## What you CAN change
- Any section of skills/laws-of-simplicity/SKILL.md
- The order, wording, structure of instructions
- Add or remove examples, checklists, or rules

## What you CANNOT change
- prepare.py (the fixed harness)
- The scoring weights (40/25/20/15 per dimension)
