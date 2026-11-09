# NSW Economy and Budget Dashboard

A public website showing the NSW economy and state budget in one place: jobs, prices, wages, housing, population, the 2026-27 Budget, debt and infrastructure, compared with the other states.

## How it works

- `index.html` is the page. It draws every figure and chart from the files in `data/` using [d3](https://d3js.org), with a small loader in `assets/dash.js`.
- `data/<source>.json` holds one data source each. `data/manifest.json` lists every source with its description and the time it was last updated.
- A scheduled refresh checks each source every day at 11:52am Sydney time (after the ABS's 11:30am release slot) and commits any new figures here. GitHub Pages republishes the site automatically after each commit.

## Sources

Australian Bureau of Statistics (Data API and State Accounts), Reserve Bank of Australia (cash rate, exchange rates, table F2.1), ASIC insolvency statistics, NSW Budget 2026-27 papers, NAB Monthly Business Survey and the Cotality Home Value Index. Full citations and data quality notes are on the site's Sources and notes tab.

## Updating the data by hand

```
python3 scripts/export_data.py DATASET_RECORDS_DIR NEW_FILES_DIR
```

copies new data files into `data/` and rebuilds `data/manifest.json`.
