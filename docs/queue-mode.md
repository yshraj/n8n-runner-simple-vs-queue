# Queue Mode Guide

## What is Queue Mode?

Queue mode allows n8n to process workflow executions through a Redis queue, enabling:
- Horizontal scaling with multiple workers
- Better performance under load
- Non-blocking execution processing

## Current Setup

- **Workers**: 1 (main instance acts as worker)
- **Redis**: Running on port 6379
- **Queue Mode**: Active

## Add More Workers

Edit `queue-n8n/docker-compose.yml` and add:

```yaml
n8n-worker:
  image: n8nio/n8n:latest
  volumes:
    - ../n8n_data:/home/node/.n8n
  environment:
    - EXECUTIONS_MODE=queue
    - QUEUE_BULL_REDIS_HOST=redis
    - QUEUE_BULL_REDIS_PORT=6379
    - TZ=Asia/Kolkata
  depends_on:
    - redis
  restart: unless-stopped
```

Then run:
```powershell
docker-compose up -d
```

