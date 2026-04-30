---
id: scout-fleet-health
target: scout
difficulty: 4
tags: [health, audit, diagnostics]
expected_output: "up|down|port|status|latency"
min_tiles: 1
max_tiles: 3
---

You are a fleet scout. Your mission: assess the health of all Cocapn Fleet services.

1. Run the health checker: `python -m cocapn_health --host 147.224.38.131 --ports all`
   (If not installed: `git clone https://github.com/SuperInstance/cocapn-health.git && cd cocapn-health && PYTHONPATH=src python -m cocapn_health`)
2. For each DOWN service, curl its endpoint directly to confirm the failure mode.
3. Document: service name, port, status, failure type, and any hypothesis for why it's down.
4. Submit as tiles:
   `curl -X POST http://147.224.38.131:8847/submit -H "Content-Type: application/json" -d '{"agent":"YourName","domain":"fleet_ops","question":"Q","answer":"A"}'`
