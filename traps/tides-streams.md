---
id: tides-streams
target: tides
difficulty: 4
tags: [rate-attention, streams, monitoring]
expected_output: "stream|rate|expected|divergence"
min_tiles: 2
max_tiles: 8
---

You are a tides agent monitoring the Rate-Attention system. Your task: catalog all data streams and identify anomalies.

1. Query: `curl http://147.224.38.131:4056/streams`
2. Extract: total streams, elevated streams, and the top 5 most divergent.
3. For each elevated stream:
   - Name, current rate, expected rate, divergence ratio
   - Whether it's a known pattern or a new anomaly
4. Submit as tiles:
   `curl -X POST http://147.224.38.131:8847/submit -H "Content-Type: application/json" -d '{"agent":"YourName","domain":"rate_attention","question":"Q","answer":"A"}'`

Focus on: streams that diverged most, whether any are zero-rate (dead), and which are elevated above threshold.
