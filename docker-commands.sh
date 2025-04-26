#!/bin/bash

# Make this script executable with: chmod +x docker-commands.sh

# Function to display help information
show_help() {
  echo "Usage: ./docker-commands.sh [COMMAND]"
  echo ""
  echo "Commands:"
  echo "  build       Build the Docker images"
  echo "  up          Start the application with Docker Compose"
  echo "  down        Stop the application and remove containers"
  echo "  restart     Restart the application"
  echo "  logs        Show logs from the containers"
  echo "  db-shell    Access the PostgreSQL database shell"
  echo "  app-shell   Access the application container shell"
  echo "  clean       Remove all containers, images, and volumes"
  echo "  help        Show this help message"
}

# Process commands
case "$1" in
  build)
    docker-compose build
    ;;
    
  up)
    docker-compose up -d
    echo "Application started on http://localhost:5000"
    ;;
    
  down)
    docker-compose down
    echo "Application stopped"
    ;;
    
  restart)
    docker-compose down
    docker-compose up -d
    echo "Application restarted on http://localhost:5000"
    ;;
    
  logs)
    docker-compose logs -f
    ;;
    
  db-shell)
    docker-compose exec db psql -U postgres -d finhackers
    ;;
    
  app-shell)
    docker-compose exec web bash
    ;;
    
  clean)
    docker-compose down -v --rmi all
    echo "All containers, images, and volumes removed"
    ;;
    
  help|*)
    show_help
    ;;
esac