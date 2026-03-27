# Publish Checklist

Use this checklist before the first public push of `ASA-Observatory`.

## Final Local Review

- confirm that `README.md` matches the intended public framing
- confirm that the public repo scope is acceptable
- confirm that no private research notes were copied into the repo
- confirm that no internal-only datasets are present

## Quick Functional Check

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start API:

```powershell
python -m uvicorn api.asa3_api_graph_v4:app --host 127.0.0.1 --port 8000
```

Start dashboard:

```powershell
python -m streamlit run dashboard/asa3_dashboard_v4.py
```

Check:
- API health responds
- dashboard opens
- sample sessions load
- main views render correctly

## Recommended First Commit Scope

Keep the first public commit focused:
- `README.md`
- `LICENSE`
- `.gitignore`
- `requirements.txt`
- `start_ASA_Observatory.ps1`
- `api/`
- `core/`
- `dashboard/`
- `conversation/`
- `docs/`

## Recommended First Git Steps

Inside the local repo folder:

```powershell
git init
git branch -M main
git add .
git commit -m "Initial public research edition of ASA Observatory"
git remote add origin https://github.com/Krugers123/ASA-Observatory.git
git push -u origin main
```

## After First Push

- verify README rendering on GitHub
- pin a screenshot or short demo clip in the repo or post on X
- add one short release note or post describing the public edition
