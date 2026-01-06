# n8n Local Setup

## 3 Modes

### 1. Simple Mode
```powershell
cd simple-n8n
docker-compose up -d
```

### 2. Queue Mode (Simple)
```powershell
cd queue-n8n
docker-compose up -d
```
(Starts n8n with queue mode, no workers)

### 3. Queue Mode (Scaling)
```powershell
cd queue-n8n
docker-compose up -d
```
(Starts n8n with queue mode + workers for horizontal scaling)

## Testing

Run performance test script:
```powershell
python test-webhook-performance.py
```

Results are stored in `results/` folder.

See `docs/webhook-testing.md` for details.

