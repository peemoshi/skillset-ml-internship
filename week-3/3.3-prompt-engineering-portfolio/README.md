# 3.3 Prompt Engineering Portfolio

Prompt evaluation across four use cases: reasoning, extraction, summarization and coding. Each use case has a baseline prompt (V1) and an improved prompt (V2), tested on the same fixed inputs and scored against rules and answer keys written before running.

**Deliverable:** [`prompt_evaluation_sheet.xlsx`](prompt_evaluation_sheet.xlsx)

## Method

- Finance-themed test inputs, each with a checkable right answer.
- Same model for every run, in a fresh chat each time (model name is on the Summary tab).
- Test inputs identical across versions; scoring fixed before running.
- One run per prompt version.

## Results (V1 → V2)

| Use case | Content score | Format / constraint score |
|---|---|---|
| Reasoning | 3/3 → 3/3 | 0/3 → 3/3 |
| Extraction | 15/15 → 15/15 | 0/3 → 3/3 |
| Summarization | 9/9 → 9/9 | 0/3 → 3/3 |
| Coding | 4/5 → 5/5 | 0/2 → 2/2 |

## Findings

- Correctness was already at or near the ceiling in V1 for three of four use cases, so these tests could not separate prompts on accuracy.
- The gain from iteration was output control: exact answer lines, fixed JSON schemas, word limits and return-type contracts.
- The one correctness gap (coding) came from an unstated requirement, not faulty logic.
- Explicit null rules stopped the model inventing missing values in extraction.

## Limitations

One run per version on one model, small fixed test sets, and strict format scoring. Results show the effect of the prompt changes on these inputs, not how stable the outputs are.

## Sheet contents

| Tab | What it holds |
|---|---|
| Summary | Method, V1 vs V2 table, findings, limitations |
| Evaluation Log | One row per run: prompt design, scores, what changed, result |
| Rules & Keys | Scoring rules and gold answers |
| Prompts & Outputs | Full prompts and raw model outputs |
