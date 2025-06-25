# Windmill MVP – Single KPI Audit

## Quick start (local)

```bash
git clone <repo>
cd windmill_mvp
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env .env  # fill secrets
export $(cat .env | xargs)  # or use `dotenv`
python scripts/gen_excel.py
```

The script reads `template.xlsx` (place your client template there) and writes `audit_out.xlsx`.

## Deploy to Windmill

1. In your workspace, create secrets matching the env var names.
2. Install the Windmill CLI (`npm i -g windmill-cli`) and add your workspace.
3. Push scripts:  

   ```bash
   wmill sync push windmill/
   ```

4. Open the *Conversion tracking active?* script in the web UI, upload the Excel template, set the Customer ID, click **Run**, then download the generated workbook.

## Project structure

```
packages/google_ads_kpi/  # reusable library
scripts/                  # local CLI helpers
windmill/scripts/         # cloud-deployed scripts
```

Extend by adding new KPI functions in `google_ads_kpi/kpi.py` and wrapping them similarly under `windmill/scripts/`.