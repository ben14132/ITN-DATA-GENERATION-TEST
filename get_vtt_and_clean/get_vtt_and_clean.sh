#!/bin/bash

env=env.json
python get_vtt.py --json $env
python vtt_normalize.py --json $env