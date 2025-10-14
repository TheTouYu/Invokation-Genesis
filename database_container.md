# host: 127.0.0.1

# port: '35432'

# user: postgres

# password: postgres

# name: stateless_service

# services

services:
  mysql:
    image: mysql:5.7.18
    container_name: mysql_5.7.18_
    environment:
      MYSQL_ROOT_PASSWORD: mysql
      MYSQL_DATABASE: mysql
      MYSQL_USER: mysql
      MYSQL_PASSWORD: mysql
    ports:
      - "3306:3306"
    volumes:
      #- mysql_5.7.18:/var/lib/mysql
      - ./data/mysql_backup/volume/:/var/lib/mysql
  postgres:
    image: postgres:16
    container_name: postgres_16_
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_USER: postgres
      POSTGRES_DB: postgres
    ports:
      - "35432:5432"
    volumes:
      # - postgres_16:/var/lib/postgresql/data
      - ./data/postgres_backup/volume/:/var/lib/postgresql/data

  pgvector:
    image: pgvector/pgvector:pg17
    container_name: pgvector
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_USER: postgres
      POSTGRES_DB: postgres
    ports:
      - "35431:5432"
    volumes:
      # - postgres_16:/var/lib/postgresql/data
      - ./data/pgvector_backup/volume/:/var/lib/postgresql/data

  redis:
    image: redis:7.2
    container_name: redis_7.2_
    ports:
      - "6379:6379"
    volumes:
      - ./data/redis_backup/volume/:/data
    command: redis-server --appendonly yes # 启用 AOF 持久化（可选）

# volumes

# postgres_16

# mysql_5.7.18
