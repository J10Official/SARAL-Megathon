# Setup

- Make sure you are in the topmost directory webrenpy.py

- run npm install (make sure you have node package manager)

- run pip install -r requirements.txt


# Usage

## Frontend

- The Visual novel script and its translation version assests (audio files, etc.) are already generated for your convenience.

- Just run npm start and you can play a basic version of the research paper

- you can change your language in /Webrenpyvn/public/game.conf from the default language

## Backend

- Use the provided bash script after giving it execute permissions
- ./run_pipeline.sh 1706.03762v5

- Or alternatively run 
    python3 pdf_to_vn_pipeline.py 1706.03762v5.pdf
- Running backend could take some time 



# If in doubt there are detailed instructions in LongReadme.md
