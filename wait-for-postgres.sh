#!/usr/bin/env bash

# If DATABASE_URL is set, try to extract host and port
if [ -n "$DATABASE_URL" ]; then
  # Extract host (text after '@' and before ':')
  db_host=$(echo "$DATABASE_URL" | sed -E 's/.*@([^:]+):.*/\1/')

  # Extract port (text after ':' and before '/')
  db_port=$(echo "$DATABASE_URL" | sed -E 's/.*:([0-9]+)\/.*/\1/')
fi

# Positional args override DATABASE_URL values if provided
host="${1:-$db_host}"
port="${2:-$db_port}"

maxwait=${3:-15}
shift 3

if [ -z "$host" ] || [ -z "$port" ]; then
  echo "Error: host and port not provided and could not parse DATABASE_URL"
  exit 1
fi

echo "Waiting for $host:$port"
seconds=0

until nc -z "$host" "$port"; do
  sleep 1
  seconds=$((seconds + 1))
  if [ "$seconds" -ge "$maxwait" ]; then
    echo "Timed out"
    break
  fi
done

exec $@
