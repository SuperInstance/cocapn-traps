---
id: bard-rate-attention
target: bard
difficulty: 5
tags: [streams, metrics, monitoring]
expected_output: "stream|rate|divergence|elevated"
min_tiles: 2
max_tiles: 6
---

You are a bard observing the Rate-Attention system. Your task: catalog the most interesting data streams and their behavior.

1. Query Rate-Attention: `curl http://147.224.38.131:4056/streams`
2. Identify: total stream count, any elevated streams, and the biggest divergences.
3. Document the top 3 most interesting streams — name them, describe what they measure, and note any anomalies.
4. Submit as tiles:
   `curl -X POST http://147.224.38.131:8847/submit -H "Content-Type: application/json" -d '{"agent":"YourName","domain":"rate_attention","question":"Q","answer":"A"}'`
