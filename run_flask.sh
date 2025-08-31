#!/bin/bash
cd /home/user/webapp
exec gunicorn -b 0.0.0.0:5000 app:app --workers 1 --log-level info