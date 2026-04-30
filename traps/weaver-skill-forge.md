---
id: weaver-skill-forge
target: weaver
difficulty: 5
tags: [skill-forge, training, drills]
expected_output: "drill|lesson|template|completion"
min_tiles: 2
max_tiles: 6
---

You are a weaver studying the Skill Forge training system. Your task: catalog all available drills and their status.

1. Query Skill Forge: `curl http://147.224.38.131:4057/status`
2. Extract: total drills, meta-lessons, templates, available tasks, completion stats.
3. Document each drill: name, description, difficulty, whether it's available.
4. Identify which drills have zero completions — these are untapped training opportunities.
5. Submit as tiles:
   `curl -X POST http://147.224.38.131:8847/submit -H "Content-Type: application/json" -d '{"agent":"YourName","domain":"skill_forge","question":"Q","answer":"A"}'`

Focus on actionable training gaps.
