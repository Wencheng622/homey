# homey

## 📋 Prerequisites

Before running this project, make sure the following tools are installed:

- Docker Desktop installed and running
- Docker Compose (usually comes with Docker Desktop)
- PostgreSQL installed locally (for pgAdmin access)
- Git (to clone the repository)

# 🔗🚀 Quick Start

## 1. Clone and Setup

```bash
# Clone the repository (if not already done)
git clone <your-repo-url>
cd homey

# Copy environment file
cp env.example .env
```

## 2. Local PostgreSQL Setup

### Option: Manual setup by SQL Shell (psql)

Connect to PostgreSQL using psql:

```bash
Server [localhost]: localhost
Database [postgres]: postgres
Port [5432]: 5432
Username [postgres]: postgres
User postgres password: your_postgres_password
```

Execute the following PSQL commands:

```
create database homey-dev;
CREATE USER homey_user WITH PASSWORD 'homey_password';
GRANT ALL PRIVILEGES ON DATABASE homey-dev TO homey_user;
\c homey-dev;
GRANT CREATE ON SCHEMA public TO homey_user;
GRANT USAGE ON SCHEMA public TO homey_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO homey_user;
exit
```
