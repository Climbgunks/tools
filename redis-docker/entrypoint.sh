#!/bin/bash

cd /tmp
redis-server &
tail -f /dev/null
