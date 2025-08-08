#!/bin/bash


if [[ "$OSTYPE" == linux-gnu* ]]; then
    echo "OS: $OSTYPE"
    python -m gunicorn core.wsgi:application
elif [[ "$OSTYPE" == darwin* ]]; then
    echo "OS: Mac OSX ($OSTYPE)"
    python -m gunicorn core.wsgi:application
elif [[ "$OSTYPE" == cygwin* ]]; then
    echo "OS: Cygwin ($OSTYPE)"
    # Gunicorn not supported; fallback
    python server.py
elif [[ "$OSTYPE" == msys* ]]; then
    echo "OS: Windows-MinGW ($OSTYPE)"
    python server.py
else
    echo "Unknown OS type: $OSTYPE"
fi
