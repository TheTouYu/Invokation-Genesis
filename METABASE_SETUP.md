# Metabase Setup for 七圣召唤 (Genshin Impact Card Game)

This document describes how to set up Metabase to visualize and analyze data from your 七圣召唤 application database.

## Prerequisites

- Docker and Docker Compose installed
- The 七圣召唤 application database (SQLite) must exist at `./instance/game.db`

## Docker Setup (Recommended)

1. **Configure Docker Registry Mirrors (for China users)**
   
   If you face issues pulling images from Docker Hub, configure Docker with registry mirrors:

   For Docker Desktop on macOS: Open Docker Desktop -> Settings -> Docker Engine and add:

   ```json
   {
     "registry-mirrors": [
       "https://docker.mirrors.ustc.edu.cn",
       "https://hub-mirror.c.163.com",
       "https://mirror.baidubce.com"
     ]
   }
   ```

2. **Start Metabase Container**

   ```bash
   cd /Users/wonder/bindolabs/ys_qs
   docker compose up -d
   ```

3. **Access Metabase**

   Once the container is running, access Metabase at:
   - URL: http://localhost:8888
   - The setup wizard will guide you through the initial configuration

4. **Configure Database Connection**

   During the setup wizard:
   - Select "SQLite" as the database type
   - For the file path, enter: `/app/data/db/game.db`
   - The database is already mounted in the container at this location

## Alternative Setup (Without Docker)

If Docker setup doesn't work for you, you can run Metabase directly:

1. **Download Metabase**
   
   Download the JAR file from https://www.metabase.com/start/jar.html

2. **Run Metabase**
   
   ```bash
   # Make sure Java is installed
   java -JXmx2g -jar metabase.jar
   ```

3. **Connect to Database**

   - Access Metabase at http://localhost:3000
   - Select "SQLite" as the database type
   - For the file path, enter the absolute path to your database: `/Users/wonder/bindolabs/ys_qs/instance/game.db`

## Database Schema Information

The 七圣召唤 application contains the following tables:

### users
- id: UUID (Primary Key)
- username: String
- email: String
- password_hash: String
- created_at: DateTime
- updated_at: DateTime
- is_active: Boolean

### card_data
- id: UUID (Primary Key)
- name: String
- card_type: String
- character_subtype: String
- element_type: String
- cost: JSON
- description: Text
- rarity: Integer
- version: String
- created_at: DateTime
- updated_at: DateTime
- is_active: Boolean
- health: Integer
- max_health: Integer
- energy: Integer
- max_energy: Integer
- weapon_type: String
- skills: JSON
- image_url: String

### decks
- id: UUID (Primary Key)
- name: String
- user_id: UUID (Foreign Key to users)
- cards: JSON
- is_public: Boolean
- created_at: DateTime
- updated_at: DateTime
- description: Text

### game_histories
- id: UUID (Primary Key)
- player1_id: UUID (Foreign Key to users)
- player2_id: UUID (Foreign Key to users)
- winner_id: UUID (Foreign Key to users)
- deck1_id: UUID (Foreign Key to decks)
- deck2_id: UUID (Foreign Key to decks)
- game_data: JSON
- game_result: String
- duration: Integer
- created_at: DateTime
- updated_at: DateTime

## Troubleshooting

1. **Database Connection Issues**
   - Ensure the database file exists and is readable
   - Check file permissions
   - Verify the path is correct in the Metabase configuration

2. **Container Won't Start**
   - Ensure Docker is running
   - Check that port 3000 is available
   - View logs with `docker logs metabase-ys-qs`

## Security Note

The database contains user information. Ensure that Metabase is deployed securely if accessed over a network, and consider using authentication and permissions to control data access.