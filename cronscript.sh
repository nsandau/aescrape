#!/bin/sh
docker run --rm -w /usr/workspace -v $(pwd):/usr/workspace aedocker python ae.py --country "Kroatien" --city "Split" --pickup "Split Airport" --pickupdate 29-JUNI-2022 --pickuptime 14 --dropoffdate 6-JULI-2022 --dropofftime 15
