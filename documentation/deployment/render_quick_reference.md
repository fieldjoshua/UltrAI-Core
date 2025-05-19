# Render Deployment Quick Reference

## Essential Commands

### Build Command
```
pip install -r requirements-phase2.txt
```

### Start Command
```
gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-10000} app_with_database:app
```

## Key Files

1. `app_with_database.py` - Main application
2. `requirements-phase2.txt` - Dependencies
3. `render.yaml` - Deployment config

## Endpoints

- `/` - Status check
- `/health` - Health check  
- `/health/database` - Database connectivity

## Environment Variables

- `PORT` - Default: 10000
- `DATABASE_URL` - PostgreSQL connection string

## Performance Targets

- Response time: < 500ms ✓
- Build time: < 5 minutes ✓
- Error rate: 0% ✓

## Deployment Checklist

- [ ] Update render.yaml
- [ ] Commit and push to main
- [ ] Check Render dashboard
- [ ] Verify endpoints work
- [ ] Monitor logs

## Troubleshooting

1. Clear cache if endpoints return HTML
2. Check full gunicorn command in dashboard
3. Verify build completes successfully
4. Monitor deployment logs