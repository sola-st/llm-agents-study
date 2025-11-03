# Trajectories Analysis Source

This repository contains data and scripts used to study action trajectories from automated program-repair and issue-solving agents. It bundles annotations for three agents (AutoCodeRover, OpenHands/CodeActAgent, RepairAgent), plus Python utilities that aggregate the annotations into publication-ready figures and statistics.

## More about the study
For more details about the study and results, check: https://arxiv.org/abs/2506.18824

## Data Overview

- `autocoderover_csv`, `openhands_csv`, `repairagent_csv`: Per-agent folders containing CSV exports of annotated trajectories. Each folder exposes:
  - `actions_categories/`: Ordered action-category timelines (`iteration,category`).
  - `action_action/`, `thought_action/`, `thought_thought/`, `result_action/`, `result_thought/`: Labeled relationships.
- `rq1/`: Aggregated metrics used for research question 1 (iterations and token usage CSV files plus derived PNG plots).
- `rq2_stats/`: Generated outputs for research question 2 (histograms, venn diagrams, bar charts, unique 4-gram dumps). The `sequences/` subfolder is populated by `stats/top_sequences.py`.


## Environment Setup
The scripts assume Python 3.10+ and the packages listed in `requirements.txt`.

If you want to use the existing virtual environment:
```
source .venv/bin/activate
```

To recreate the environment from scratch:
```
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Usage Guide
All commands should be executed from the repository root after activating the virtual environment.

### Action Category Bar Chart
```
python stats/actions_bars.py
```
- Reads category CSV/JSON files for each agent.
- Prints per-agent totals and percentages to stdout.
- Saves `figures/actions_categories_bars.pdf` and displays it interactively.

### Stacked Density Histograms
```
python stats/stacked_histogram.py
```
- Loads action category sequences with agent-specific cleanup rules.
- Generates normalized stacked density histograms for each agent.
- Saves `rq2_stats/<Agent>_histogram.png` and opens the plots.

### Top Sequence Mining
```
python stats/top_sequences.py
```
- Mines 4-gram sequences from the resolved and unresolved subsets.
- Writes unique 4-grams to `rq2_stats/sequences/<Agent>_unique_4grams.txt`.
- Saves Venn diagrams (`rq2_stats/seq_<Agent>_venn.png`) and comparative bar charts (`rq2_stats/seq_<Agent>_bars.png`).

### Global Relationship Statistics
```
python stats/global_stats_acr.py autocoderover_csv/thought_action/
python stats/global_stats_oh.py openhands_csv/action_action/
python stats/global_stats_ra.py repairagent_csv/result_thought/
```
- Prints pooled counts/percentages for all, resolved, and unresolved instances.
- Optional flags: `--per-file` for detailed output, `--save-csv <path>` to export aggregates.
- Shell helpers (`relationships_acr.sh`, `relationships_oh.sh`, `relationships_ra.sh`) run the full suite for each agent.

### AutoCodeRover Instances
Resolved instances:
```
scikit-learn__scikit-learn-13497
django__django-15789
django__django-15814
scikit-learn__scikit-learn-13241
django__django-13315
django__django-13710
django__django-14752
django__django-15498
sphinx-doc__sphinx-8713
matplotlib__matplotlib-23964
```
Unresolved instances:
```
scikit-learn__scikit-learn-25638
sympy__sympy-11870
sympy__sympy-17655
sympy__sympy-22714
pydata__xarray-5131
django__django-13448
pytest-dev__pytest-7432
django__django-13660
django__django-11133
django__django-11099
mwaskom__seaborn-3010
sympy__sympy-16792
pytest-dev__pytest-5221
sympy__sympy-15345
pydata__xarray-4094
psf__requests-2148
matplotlib__matplotlib-22835
django__django-16139
pytest-dev__pytest-8906
django__django-13551
django__django-16046
django__django-14580
sympy__sympy-20442
matplotlib__matplotlib-23913
django__django-12470
sympy__sympy-24102
matplotlib__matplotlib-24149
django__django-16041
sympy__sympy-13915
mwaskom__seaborn-3190
```

### OpenHands / CodeActAgent Instances
Resolved instances:
```
django__django-12708
django__django-10924
django__django-12470
django__django-14017
django__django-12700
sympy__sympy-23117
sympy__sympy-17655
pytest-dev__pytest-5495
scikit-learn__scikit-learn-14087
scikit-learn__scikit-learn-13142
```
Unresolved instances:
```
django__django-11910
django__django-11283
django__django-11564
django__django-11905
astropy__astropy-14365
matplotlib__matplotlib-22711
sympy__sympy-20322
sympy__sympy-21612
django__django-12856
pytest-dev__pytest-8906
sphinx-doc__sphinx-11445
matplotlib__matplotlib-23563
pytest-dev__pytest-8365
sympy__sympy-17022
django__django-14155
matplotlib__matplotlib-23299
django__django-12308
sympy__sympy-13915
sympy__sympy-20639
mwaskom__seaborn-3407
django__django-13925
pylint-dev__pylint-7228
sympy__sympy-21171
django__django-14534
pydata__xarray-3364
sympy__sympy-14817
scikit-learn__scikit-learn-13497
django__django-15781
scikit-learn__scikit-learn-14092
django__django-14997
```

### RepairAgent Instances
Resolved instances:
```
Chart_13
Math_101
Math_65
Jsoup_16
Chart_17
Cli_11
Compress_13
Math_77
Jsoup_51
Mockito_34
```
Unresolved instances:
```
Closure_127
JacksonDatabind_67
Closure_145
Closure_141
Closure_135
Math_61
JacksonDatabind_44
Jsoup_67
Cli_39
Time_4
Closure_142
Closure_54
JacksonDatabind_85
JacksonDatabind_35
Compress_25
JxPath_9
Math_96
JacksonDatabind_3
Math_40
Lang_44
Jsoup_74
Closure_117
Closure_22
Closure_61
Jsoup_57
Math_28
Math_44
Closure_3
Closure_80
Lang_36
```

