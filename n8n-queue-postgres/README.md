# n8n Queue Mode with PostgreSQL

This setup provides a production-ready n8n installation with:
- **PostgreSQL** database (instead of SQLite) for better performance and scalability
- **Redis** queue backend for job management
- **Queue mode** for horizontal scaling with multiple workers
- **Worker instance** to process queued executions

## Architecture

This setup includes:
- **PostgreSQL**: Database for storing workflows, executions, credentials, and all n8n data
- **Redis**: Queue backend for managing workflow execution jobs
- **n8n** (main instance): Web server that receives requests and enqueues executions
- **n8n-worker**: Dedicated worker that processes queued executions
- **pgAdmin**: Web-based PostgreSQL administration tool for database management

## Prerequisites

- Docker and Docker Compose installed
- Ports available: `5678` (n8n), `5433` (PostgreSQL external), `6379` (Redis), `5050` (pgAdmin)

## Quick Start

1. **Start all services:**
   ```powershell
   docker-compose up -d
   ```

2. **Wait for services to be ready** (especially PostgreSQL initialization):
   ```powershell
   docker-compose logs -f postgres
   ```
   Wait until you see: `database system is ready to accept connections`

3. **Verify n8n is running:**
   ```powershell
   docker-compose logs n8n | Select-String "Server started"
   ```

4. **Verify queue mode is active:**
   ```powershell
   docker-compose logs n8n | Select-String "Task Broker ready"
   ```

5. **Verify worker is running:**
   ```powershell
   docker-compose logs n8n-worker | Select-String "Task Broker ready"
   ```

6. **Access n8n:**
   - URL: http://localhost:5678
   - Username: `admin`
   - Password: `admin123`

7. **Access pgAdmin (Database UI):**
   - URL: http://localhost:5050
   - Email: `admin@n8n.local`
   - Password: `admin123`

## Accessing PostgreSQL with pgAdmin

pgAdmin is included in this setup for easy database management. Follow these steps to connect:

### Step 1: Access pgAdmin Web Interface

1. Open your web browser
2. Navigate to: **http://localhost:5050**
3. Log in with:
   - **Email**: `admin@n8n.local`
   - **Password**: `admin123`

### Step 2: Add PostgreSQL Server

1. **Right-click on "Servers"** in the left sidebar
2. Select **"Register"** → **"Server..."**

3. **In the "General" tab:**
   - **Name**: Enter any name (e.g., "n8n PostgreSQL" or "n8n-db")

4. **In the "Connection" tab:**
   - **Host name/address**: `postgres` (this is the Docker service name)
   - **Port**: `5432` (internal Docker port, not 5433)
   - **Maintenance database**: `n8n`
   - **Username**: `n8n`
   - **Password**: `n8n_password`
   - ✅ **Check "Save password"** (optional, for convenience)

5. Click **"Save"**

### Step 3: Browse Your Database

Once connected, you can:

- **Expand the server** → **Databases** → **n8n** → **Schemas** → **public** → **Tables**
- **View n8n tables** like:
  - `execution_entity` - Workflow execution history
  - `workflow_entity` - Your workflows
  - `credentials_entity` - Stored credentials
  - `execution_data` - Execution data
  - And many more...

### Step 4: Run Queries

1. **Right-click on the database** (n8n)
2. Select **"Query Tool"**
3. **Type your SQL query**, for example:
   ```sql
   SELECT * FROM workflow_entity LIMIT 10;
   ```
4. Click the **"Execute"** button (or press F5)

### Useful pgAdmin Features

- **View table data**: Right-click any table → "View/Edit Data" → "All Rows"
- **Export data**: Right-click table → "Backup..." to export
- **Run queries**: Query Tool for custom SQL
- **View table structure**: Right-click table → "Properties" → "Columns"
- **Monitor connections**: Tools → Server Status

### Troubleshooting pgAdmin

**Can't connect to server:**
- Make sure PostgreSQL container is running: `docker-compose ps postgres`
- Verify you're using `postgres` as hostname (not `localhost`)
- Check the port is `5432` (internal Docker port)

**pgAdmin won't load:**
- Check if pgAdmin container is running: `docker-compose ps pgadmin`
- View logs: `docker-compose logs pgadmin`
- Try restarting: `docker-compose restart pgadmin`

## Configuration

### Default Credentials

**n8n Web Interface:**
- Username: `admin`
- Password: `admin123`

**PostgreSQL:**
- Database: `n8n`
- User: `n8n`
- Password: `n8n_password`
- Port: `5433` (external, mapped from internal 5432)

**Redis:**
- Port: `6379`
- No authentication (internal network only)

**pgAdmin:**
- URL: http://localhost:5050
- Email: `admin@n8n.local`
- Password: `admin123`

### Customizing Credentials

Edit `docker-compose.yml` and update the following environment variables:

**For n8n authentication:**
```yaml
- N8N_BASIC_AUTH_USER=your_username
- N8N_BASIC_AUTH_PASSWORD=your_password
```

**For PostgreSQL:**
```yaml
# In postgres service:
- POSTGRES_DB=your_database_name
- POSTGRES_USER=your_user
- POSTGRES_PASSWORD=your_password

# In n8n and n8n-worker services:
- DB_POSTGRESDB_DATABASE=your_database_name
- DB_POSTGRESDB_USER=your_user
- DB_POSTGRESDB_PASSWORD=your_password
```

## Scaling Workers

To run multiple workers for parallel processing:

```powershell
docker-compose up -d --scale n8n-worker=3
```

This allows 3 concurrent workflow executions. You can scale to any number of workers based on your needs.

## Managing Services

**Stop all services:**
```powershell
docker-compose down
```

**Stop and remove volumes (⚠️ deletes all data):**
```powershell
docker-compose down -v
```

**View logs:**
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f n8n
docker-compose logs -f n8n-worker
docker-compose logs -f postgres
docker-compose logs -f redis
docker-compose logs -f pgadmin
```

**Restart a specific service:**
```powershell
docker-compose restart n8n
docker-compose restart n8n-worker
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

4. **Verify PostgreSQL connection:**
   ```powershell
   docker-compose logs n8n | Select-String "postgres"
   docker-compose logs n8n-worker | Select-String "postgres"
   ```

5. **Ensure `command: worker` is set** in docker-compose.yml for n8n-worker service

6. **Restart services:**
   ```powershell
   docker-compose down
   docker-compose up -d
   ```

### PostgreSQL Connection Issues

If n8n can't connect to PostgreSQL:

1. **Check PostgreSQL is healthy:**
   ```powershell
   docker-compose ps postgres
   ```
   Should show "healthy" status.

2. **Check PostgreSQL logs:**
   ```powershell
   docker-compose logs postgres
   ```

3. **Verify database credentials** match in both postgres service and n8n services

4. **Wait for PostgreSQL to fully initialize** (can take 10-30 seconds on first start)

### Database Migration

When switching from SQLite to PostgreSQL:

1. **Stop n8n services** (keep PostgreSQL running)
2. **Backup your SQLite database** (if you have existing data)
3. **Start n8n** - it will automatically create the PostgreSQL schema
4. **If you need to migrate data**, you'll need to export from SQLite and import to PostgreSQL manually

## Data Persistence

- **PostgreSQL data**: Stored in `postgres_data` Docker volume
- **Redis data**: Stored in `redis_data` Docker volume
- **n8n files**: Stored in `./n8n_data` directory (workflows, credentials, etc.)

To backup:
```powershell
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U n8n n8n > backup.sql

# Backup n8n_data directory
# Copy the ./n8n_data folder to a safe location
```

## Advantages of PostgreSQL over SQLite

- ✅ Better performance with large datasets
- ✅ Better concurrency for multiple users/workflows
- ✅ Production-ready for enterprise deployments
- ✅ Required for horizontal scaling (multiple n8n instances)
- ✅ Better backup and recovery options
- ✅ ACID compliance and data integrity
- ✅ Can handle high-volume workflow executions

## Port Conflicts

If ports are already in use, edit `docker-compose.yml` and change:

```yaml
ports:
  - "5678:5678"  # n8n
  - "5433:5432"  # PostgreSQL (external:internal)
  - "6379:6379"  # Redis
  - "5050:80"    # pgAdmin
```

Change the first number (host port) to an available port on your system.

**Note:** The PostgreSQL external port is set to `5433` by default to avoid conflicts with existing PostgreSQL installations. The internal port (5432) remains unchanged as n8n services connect via Docker's internal network.

