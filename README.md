# Livestock Tracker Platform

This directory contains the replacement application: a Django modular monolith and a Nuxt/Vue frontend. The legacy microservices at the repository root remain unchanged while this platform is developed.

## Local development

1. Copy `.env.example` to `.env` and adjust values.
2. Run `docker compose up --build` from this directory.
3. Open the frontend at `http://localhost:3000` and the API at `http://localhost:8000/api/v1/`.

The first milestone covers authentication, farms, flocks, animals, and dashboard totals. Health, husbandry reminders, nutrition, and the assistant follow as separate modules.
