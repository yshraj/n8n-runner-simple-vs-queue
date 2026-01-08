# n8n Simple Mode with Redis

This setup provides a simple n8n installation with Redis for use in your workflows.

## Architecture

- **n8n**: Main n8n application container
- **Redis**: Redis server container for use in n8n workflows
- Both containers are on the same Docker network (automatically created by docker-compose)

## Quick Start

1. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** and set your Redis password:
   ```
   REDIS_PASSWORD=your_secure_password_here
   ```

3. **Start the containers**:
   ```bash
   docker-compose up -d
   ```

4. **Access n8n**:
   - Open your browser and go to: `http://localhost:5678`
   - Set up your n8n account when prompted

5. **Stop the containers**:
   ```bash
   docker-compose down
   ```

6. **Stop and remove volumes** (⚠️ This will delete all data):
   ```bash
   docker-compose down -v
   ```

## Connecting to Redis in n8n Workflows

When using the Redis node in your n8n workflows, use the following connection details:

### Redis Connection Settings

In your n8n workflow, when adding a Redis node (like "Redis" or "Redis Trigger"), configure it with these settings:

| Field | Value | Description |
|-------|-------|-------------|
| **Host** | `redis` | The service name from docker-compose (Docker's internal DNS) |
| **Port** | `6379` | Default Redis port (internal port) |
| **Password** | (Your `.env` file value) | The password you set in `REDIS_PASSWORD` environment variable |
| **User** | (leave empty) | Redis doesn't require a username by default |
| **Database Number** | `0` | Default Redis database (0-15 available) |
| **SSL** | `false` | SSL is not enabled in this setup |

### Step-by-Step Configuration in n8n

1. **Add Redis Node**:
   - Drag and drop a Redis node into your workflow
   - Select the operation you want (e.g., GET, SET, LPUSH, etc.)

2. **Configure Connection**:
   - Click on "Credentials" or the connection settings
   - Enter the following:
     - **Host**: `redis`
     - **Port**: `6379`
     - **Password**: Enter the same password you set in your `.env` file (e.g., `your_secure_password_here`)
     - **User**: Leave empty
     - **Database Number**: `0` (or 1-15 if you want a different database)
     - **SSL**: Disabled/Off/False

3. **Save and Test**:
   - Save the credentials
   - Execute the node to test the connection

### Port Forwarding

**❌ Port Forwarding is NOT Required**

Since n8n and Redis are in the same Docker network, n8n can communicate with Redis directly using the service name `redis`. The containers communicate internally through Docker's network bridge.

- **Internal Communication**: n8n → `redis:6379` (no port forwarding needed)
- **External Access**: Only n8n's web interface is exposed on port `5678` to your host machine

### Example Workflow Usage

**Setting a value in Redis**:
- Operation: `SET`
- Key: `mykey`
- Value: `myvalue`

**Getting a value from Redis**:
- Operation: `GET`
- Key: `mykey`

**Using Lists**:
- Operation: `LPUSH` (add to list)
- Key: `mylist`
- Value: `item1`

### Security Notes

- ⚠️ **Keep your `.env` file secure** - it contains your Redis password
- ⚠️ **Never commit `.env` file to version control** - it's already in `.gitignore`
- 🔒 The Redis container is only accessible from within the Docker network
- 🔒 No external ports are exposed for Redis (only n8n's port 5678 is exposed)

### Troubleshooting

**Connection refused error**:
- Make sure both containers are running: `docker-compose ps`
- Check that the password matches what's in your `.env` file
- Verify the host is exactly `redis` (not `localhost` or `127.0.0.1`)

**Authentication error**:
- Double-check your password matches the `REDIS_PASSWORD` in `.env`
- Make sure you're using the password, not leaving it empty

**Container not starting**:
- Check logs: `docker-compose logs redis`
- Verify `.env` file exists and has `REDIS_PASSWORD` set

### Viewing Redis Data

To inspect Redis data from your host machine, you can use:

```bash
# Connect to Redis container
docker exec -it redis redis-cli -a your_password_here

# Or use redis-cli with password
docker exec -it redis redis-cli -a $REDIS_PASSWORD
```

Inside redis-cli:
- `KEYS *` - List all keys
- `GET keyname` - Get a value
- `TYPE keyname` - Check key type
- `EXIT` - Exit redis-cli


