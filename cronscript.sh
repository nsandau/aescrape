cd /home/dietpi/aescrape
docker run --rm -w /usr/workspace -v $(pwd):/usr/workspace aedocker python ae.py --country "Kroatien" --city "Split" --pickup "Split Airport" --pickupdate 24-MAJ-2022 --pickuptime 14 --dropoffdate 1-JUNI-2022 --dropofftime 15
