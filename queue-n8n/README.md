# Queue Mode n8n Setup

## Architecture

This setup includes:
- **n8n** (main instance): Web server that receives requests and enqueues executions
- **n8n-worker**: Dedicated worker that processes queued executions (requires `command: worker`)
- **Redis**: Queue backend for job management

**Important**: The worker service must have `command: worker` to actually process jobs. Without it, the container runs in main mode and won't consume the queue.

## Steps

1. Start services:
   ```powershell
   docker-compose up -d
   ```

2. Verify queue mode:
   ```powershell
   docker-compose logs n8n | Select-String "Task Broker ready"
   ```

3. Verify worker is running:
   ```powershell
   docker-compose logs n8n-worker | Select-String "Task Broker ready"
   ```

4. Access n8n:
   - URL: http://localhost:5678
   - Username: admin
   - Password: admin123

5. Stop services:
   ```powershell
   docker-compose down
   ```

## Troubleshooting

### Jobs Queued but Not Processing

If executions show "Starting soon" and stay queued:

1. **Verify worker is running in worker mode:**
   ```powershell
   docker-compose logs n8n-worker | Select-String "worker"
   ```
   Should show worker-related messages, not web server startup.

2. **Check worker logs:**
   ```powershell
   docker-compose logs n8n-worker
   ```

3. **Verify Redis connection:**
   ```powershell
   docker-compose logs n8n-worker | Select-String "redis"
   ```

4. **Ensure `command: worker` is set** in docker-compose.yml for n8n-worker service

5. **Restart services:**
   ```powershell
   docker-compose down
   docker-compose up -d
   ```

### Scaling Workers

To run multiple workers for parallel processing:
```powershell
docker-compose up -d --scale n8n-worker=3
```

This allows 3 concurrent workflow executions.

