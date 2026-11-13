# Smart XI Dashboard

Interactive Streamlit companion for the Smart XI pressure-performance analysis.

## Files
- `app.py` — dashboard application
- `SmartXI_Analysis.xlsx` — source workbook used by the dashboard
- `requirements.txt` — Python dependencies

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this folder.
3. Run: `pip install -r requirements.txt`
4. Run: `streamlit run app.py`

## Publish online
1. Create a GitHub repository and upload all three files in this folder.
2. Open Streamlit Community Cloud and sign in with GitHub.
3. Create a new app, select the repository and branch, and set the main file to `app.py`.
4. Deploy. Copy the public app URL into the hackathon's Dashboard Link field only after deployment succeeds.

## Data consistency
The dashboard reads the ranking tables, scores, benchmarks, pressure definition and audit sheets directly from `SmartXI_Analysis.xlsx`. It does not independently recalculate player scores. Keep this workbook as the single source of truth and replace it only when the matching PDF report is also updated and checked.
