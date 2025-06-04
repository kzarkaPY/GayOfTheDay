version: '3.8'

services:
  bot:
    build: .
    env_file: .env
    depends_on:
      - db
    restart: always
    networks:
      - bot_network

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - type: volume
        source: postgres_data
        target: /var/lib/postgresql/data
    restart: always
    networks:
      - bot_network

networks:
  bot_network:
    driver: bridge

volumes:
  postgres_data:
    driver: local 
