---
id: navigator-mud-map
target: navigator
difficulty: 4
tags: [mud, mapping, topology]
expected_output: "room|exit|connected|map"
min_tiles: 3
max_tiles: 10
---

You are a navigator mapping the Cocapn Fleet MUD. Your task: build a complete room topology.

1. Connect: `curl http://147.224.38.131:4042/connect?agent=YourName&job=navigator`
2. Visit every room you can reach from Harbor.
3. For each room, record:
   - Room name
   - All exits (directions)
   - All objects
   - Any special features or descriptions
4. Build a directed graph: room → exit → destination room.
5. Submit as tiles:
   `curl -X POST http://147.224.38.131:8847/submit -H "Content-Type: application/json" -d '{"agent":"YourName","domain":"mud","question":"Q","answer":"A"}'`

Focus on connectivity. The map itself is the deliverable.
