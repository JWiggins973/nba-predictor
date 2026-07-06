#!/bin/bash

#starts backend and front end in background for testing locally quickly
(cd backend && ../venv/bin/uvicorn app:app --reload) &
BACKEND_PID=$!

(cd frontend && npm run dev) &
FRONTEND_PID=$!

trap "pkill -f 'uvicorn app:app'; pkill -f vite" EXIT

wait