#!/bin/bash

# This script contains helpful commands for managing the Docker containers

# Function to display help message
show_help() {
    echo "Usage: ./docker-commands.sh [command]"
    echo ""
    echo "Commands:"
    echo "  up              Start all containers in detached mode"
    echo "  down            Stop and remove all containers"
    echo "  restart         Restart all containers"
    echo "  logs [service]  View logs for a specific service or all services"
    echo "  ps              List all running containers"
    echo "  exec [service]  Execute a bash shell in a container"
    echo "  build           Rebuild all containers"
    echo "  clean           Remove all containers, images, and volumes"
    echo "  help            Display this help message"
    echo ""
    echo "Examples:"
    echo "  ./docker-commands.sh up"
    echo "  ./docker-commands.sh logs app"
    echo "  ./docker-commands.sh exec mcp-server"
}

# Check if the script is run with a command
if [ $# -lt 1 ]; then
    show_help
    exit 1
fi

# Process the command
case "$1" in
    up)
        echo "Starting all containers in detached mode..."
        docker-compose up -d
        ;;
    down)
        echo "Stopping and removing all containers..."
        docker-compose down
        ;;
    restart)
        echo "Restarting all containers..."
        docker-compose restart
        ;;
    logs)
        if [ $# -gt 1 ]; then
            echo "Viewing logs for $2..."
            docker-compose logs -f $2
        else
            echo "Viewing logs for all services..."
            docker-compose logs -f
        fi
        ;;
    ps)
        echo "Listing all running containers..."
        docker-compose ps
        ;;
    exec)
        if [ $# -gt 1 ]; then
            echo "Executing bash shell in $2..."
            docker-compose exec $2 bash
        else
            echo "Please specify a service name"
            echo "Usage: ./docker-commands.sh exec [service]"
            exit 1
        fi
        ;;
    build)
        echo "Rebuilding all containers..."
        docker-compose build
        ;;
    clean)
        echo "Removing all containers, images, and volumes..."
        docker-compose down -v
        docker system prune -af
        ;;
    help)
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac