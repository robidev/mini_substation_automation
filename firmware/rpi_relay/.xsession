#!/bin/sh
#exec /usr/bin/python3 /home/user/rly_service/siprotec_320x480.py

systemctl --user start ui.service

exec openbox-session
