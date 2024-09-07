#!/bin/bash

windows_ip=$(ip route | grep default | awk '{print $3}')

if [ -z "$windows_ip" ]; then
    echo "Could not detect Windows IP."
    exit 1
fi

echo "Detected Windows IP: $windows_ip"

anki_connect_url="ANKI_CONNECT_URL=\"http://$windows_ip:8765\""

if [ ! -f .env ]; then
    echo ".env file not found, creating one..."
    touch .env
fi

if grep -q "^ANKI_CONNECT_URL=" .env; then
    sed -i "s|^ANKI_CONNECT_URL=.*|$anki_connect_url|" .env
else
    echo "$anki_connect_url" >> .env
fi

echo ".env file has been updated with: $anki_connect_url"
