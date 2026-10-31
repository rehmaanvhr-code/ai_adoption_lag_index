# AI Adoption Lag Index

A composite index that puts AI adoption speed and governance readiness on the same scale, by country and by sector, and measures the gap between them. A positive gap means firms are adopting faster than the rules and the regulators are keeping up. A negative gap means governance is ahead of actual use, which can be its own problem if it is slowing adoption that would have paid off.

## Connection to the research

This is the measurement companion to "The Governance Lag: Why Slow AI Adoption Is the Larger Risk" (Rehman, 2026). The paper argues that the usual framing of AI governance, where the risk is that adoption outruns the rules, misses the cost of the opposite case. If governance readiness is high but adoption is low, the economy pays the cost of waiting described in "Who Bears the Cost of Waiting: The Uneven Price of Slow AI Adoption" (Rehman, 2026). An index only makes sense if both sides are measured. This repo does that with a transparent weighting that can be argued with, and a sensitivity test that shows which rankings survive when the weights move.

## Why it matters for AI governance in financial services

Finance and insurance is one of the sectors in the data, and it is the one where sector specific guidance, model risk rules and a high share of firms with an AI policy coexist with fast adoption growth. The sector chart shows where finance sits relative to less regulated sectors. For a governance team the useful question is whether the firm's own controls are proportionate to how fast the firm is actually deploying, and this gives a simple way to frame that comparison for a board or a regulator.

## How it works

Country level indicators are split into an adoption side (firm adoption rate, AI investment per capita, AI talent concentration) and a governance side (count of national AI policies and strategies, a score for binding regulation in force, and a regulator capacity score). Each indicator is min max normalised across the countries, investment is log transformed first because it is heavily skewed. Weighted averages give an adoption score and a governance score, and the lag gap is the difference. `sensitivity` perturbs the weights two hundred times and records each country's mean rank and how often it lands in the top three gap, so the reader can see which positions hold up under different weightings.

Sector level uses the growth in adoption between 2023 and 2025 against the share of firms with an AI policy and whether the sector has sector specific guidance.

## Run

```
pip install -r requirements.txt
python index.py
pytest
```

Outputs in `outputs/`: `adoption_vs_governance.png` is the country scatter with a diagonal, points above the line have adoption ahead of governance. `sector_gap.png` is a bar chart of the sector gap. `index_table.csv` and `sector_table.csv` hold the scores and the sensitivity results.

In the default run Singapore and the United States have the largest positive gap and are top three under almost every weighting. Germany and France have the largest negative gap, which is what you would expect with the EU AI Act in force. Canada sits close to the line, slightly on the governance ahead side, which matches the paper's reading of the AIDA period. Regulated sectors (finance, health, public administration, utilities) all show negative gaps, the information and professional services sectors show the largest positive gaps.

## Data and sources

The values in `data/adoption_indicators.csv` and `data/sector_adoption.csv` are approximate and were assembled by hand from the kinds of sources below. They are meant to make the method runnable, not to be cited as data. Refresh them from the sources before using the numbers for anything.

Firm adoption rates: Statistics Canada, Canadian Survey on Business Conditions (AI use questions, 2023 to 2025); US Census Bureau, Business Trends and Outlook Survey (BTOS) AI supplement; Eurostat ICT usage in enterprises.
Investment and talent: Stanford HAI, AI Index Report 2025.
Policy counts, regulation and capacity: OECD.AI Policy Observatory national strategies and policy database, plus a judgement score for regulator capacity.

## Limitations

Twelve countries and twelve sectors is a small panel. The regulator capacity score is a judgement call and the binding regulation score is a coarse ordinal. Min max normalisation is sensitive to the extremes (Singapore and the United States pull the adoption scale). The sector data is Canadian and does not cover other countries. The sensitivity test varies weights but not the input values.

## Author

Saif Rehman, MMAI, Smith School of Business, Queen's University.
