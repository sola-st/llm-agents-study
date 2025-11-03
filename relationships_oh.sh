source .venv/bin/activate

python stats/global_stats_oh.py openhands_csv/thought_action/
python stats/global_stats_oh.py openhands_csv/thought_thought/
python stats/global_stats_oh.py openhands_csv/action_action/
python stats/global_stats_oh.py openhands_csv/result_thought/
python stats/global_stats_oh.py openhands_csv/result_action/