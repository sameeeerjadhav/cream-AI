# Prompt comparison

This evaluation compares `prompts/task_compare_v1.txt` with
`prompts/task_compare_v2.txt` on the 10 questions in
`docs/user_questions.md`. It is a manual evaluation plan: run each question
with the same retrieved records and provider settings, then score each answer
from 0 to 2 for factual grounding, directness, and usefulness.

| # | Question | V1 notes | V2 notes |
|---|---|---|---|
| 1 | Am I eligible for PMEGP if I am starting a new manufacturing business? |  |  |
| 2 | What is the maximum project cost for a PMEGP service business? |  |  |
| 3 | What subsidy is available under CMEGP for a rural applicant? |  |  |
| 4 | How much own contribution is needed for a general-category applicant? |  |  |
| 5 | Which scheme is suitable for a woman starting a greenfield enterprise? |  |  |
| 6 | Has my PMEGP loan application been approved, and when will the money arrive? |  |  |
| 7 | Can a family use PMEGP assistance for two different businesses? |  |  |
| 8 | Do I need an eighth-standard qualification for a larger PMEGP project? |  |  |
| 9 | What are the 2025 investment and turnover limits for a micro enterprise? |  |  |
| 10 | Is MUDRA available for a small food-processing or service business? |  |  |

Version 2 should generally score better because it requires evidence, avoids
approval promises, and asks a useful follow-up. Q6 should be marked as a
success only when the answer clearly says the dataset has no live application
status.
