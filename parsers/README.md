# parsers

Parses raw agent logs into the five `thought/action/result` text views under `trajectories/<agent>/parsed/`.

```
python -m parsers acr --raw-root <dir of <instance>_<timestamp>/ folders> --out trajectories/autocoderover/parsed
python -m parsers oh  --jsonl <output.jsonl>                              --out trajectories/openhands/parsed
python -m parsers ra  --logs-dir <dir of RepairAgent text logs>           --out trajectories/repairagent/parsed
```
