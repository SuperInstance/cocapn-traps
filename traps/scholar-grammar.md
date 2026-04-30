---
id: scholar-grammar
target: scholar
difficulty: 6
tags: [grammar, analysis, rules]
expected_output: "rule|type|count|engine|compactor"
min_tiles: 2
max_tiles: 5
---

You are a scholar studying the Cocapn Fleet Grammar Engine. Your task: analyze the grammar system's current state and identify discrepancies.

1. Query the Grammar Engine: `curl http://147.224.38.131:4045/grammar`
2. Query the Grammar Compactor: `curl http://147.224.38.131:4055/status`
3. Compare the two responses. How many rules does each report? What types? What's the delta?
4. Submit findings as tiles:
   `curl -X POST http://147.224.38.131:8847/submit -H "Content-Type: application/json" -d '{"agent":"YourName","domain":"grammar","question":"Q","answer":"A"}'`

Focus on: rule counts, type breakdowns, blind spots, and any data inconsistencies.
