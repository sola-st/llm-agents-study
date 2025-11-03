source .venv/bin/activate

python stats/global_stats_acr.py autocoderover_csv/thought_action/
python stats/global_stats_acr.py autocoderover_csv/thought_thought/
python stats/global_stats_acr.py autocoderover_csv/action_action/
python stats/global_stats_acr.py autocoderover_csv/result_thought/
python stats/global_stats_acr.py autocoderover_csv/result_action/