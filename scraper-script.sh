#!/bin/bash

# This is use to run all the scraper script in parallel
source ../venvScraper/bin/activate
python site-code\furupo-com.py &
python site-code\furusato-ana-co-jp.py &
python site-code\furusato-wowma-jp.py &
python site-code\furusatohonpo-jp.py &
python site-code\tokyu-furusato-jp.py &
wait
deactivate
