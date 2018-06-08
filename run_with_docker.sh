#!/bin/bash
set -e

[ -z "$APLATAM_DATA" ] && echo "You need to set APLATAM_DATA variable first. See README.md" && exit 1
nvidia-docker run -ti -v $APLATAM_DATA:/data dymaxionlabs/ap-latam $@
