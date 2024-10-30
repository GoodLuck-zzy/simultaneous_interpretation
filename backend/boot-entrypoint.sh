#!/bin/bash

ldconfig
python3 -m commands.init_database
gunicorn -c gunicorn.py run:app