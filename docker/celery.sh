#!/bin/bash

celery -A app.tasks.core:celery worker --loglevel=INFO