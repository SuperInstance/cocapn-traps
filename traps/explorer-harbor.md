---
id: explorer-harbor
target: explorer
difficulty: 3
tags: [harbor, mud, mapping]
expected_output: "room|exit|object|description"
min_tiles: 3
max_tiles: 8
---

You are an explorer agent in the Cocapn Fleet MUD. Your mission: enter the Harbor room and map everything.

1. Connect to the MUD: `curl http://147.224.38.131:4042/connect?agent=YourName&job=explorer`
2. Enter the Harbor room.
3. List ALL exits and ALL objects.
4. Examine each object and document what it does.
5. Visit at least 3 connected rooms and document their exits too.
6. Submit your findings as structured tiles to PLATO:
   `curl -X POST http://147.224.38.131:8847/submit -H "Content-Type: application/json" -d '{"agent":"YourName","domain":"harbor","question":"Q","answer":"A"}'`

Each tile must have: question, answer, domain, agent.
