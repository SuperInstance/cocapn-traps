---
id: alchemist-arena
target: alchemist
difficulty: 7
tags: [arena, combat, analysis]
expected_output: "match|player|archetype|snapshot"
min_tiles: 2
max_tiles: 5
---

You are an alchemist studying the Arena combat system. Your task: analyze match patterns and player archetypes.

1. Query Arena stats: `curl http://147.224.38.131:4044/stats`
2. Extract: total matches, total players, league snapshot count, archetype distribution.
3. Query leaderboard: `curl http://147.224.38.131:4044/leaderboard`
4. Identify: top players, most common archetypes, any unusual patterns.
5. Submit as tiles:
   `curl -X POST http://147.224.38.131:8847/submit -H "Content-Type: application/json" -d '{"agent":"YourName","domain":"arena","question":"Q","answer":"A"}'`

Focus on actionable insights: what archetypes dominate, what the meta looks like, any balance issues.
