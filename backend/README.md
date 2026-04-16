# Backend

Paper2Lab backend is a FastAPI service that coordinates the four agents and exposes the REST API.

## Main areas
- `app/api/routes`: REST endpoints
- `app/agents`: Radar, Reader, Repro, LabOps
- `app/services`: orchestration and business logic
- `app/repositories`: database access
- `app/parsers`: paper source and PDF parsing
- `app/diagnostics`: log diagnosis rules
- `tests`: API and integration-style MVP tests

## Run
```bash
python -m pip install -r requirements.txt
python ../scripts/seed_demo.py
python ../scripts/run_backend.py
```

