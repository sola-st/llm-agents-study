source .venv/bin/activate

python stats/global_stats_ra.py repairagent_csv/thought_action/
python stats/global_stats_ra.py repairagent_csv/thought_thought/
python stats/global_stats_ra.py repairagent_csv/action_action/
python stats/global_stats_ra.py repairagent_csv/result_thought/
python stats/global_stats_ra.py repairagent_csv/result_action/