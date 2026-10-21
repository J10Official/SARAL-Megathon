# WebRenPy Visual Novel Player

See the [repository overview](../README.md) for the project, lineage, and submission status. This directory contains the React player and the existing paper-generation workflow.

## Play the included content

Run from this directory (`Webrenpyvn`):

```bash
npm install
npm start
```

The development server normally opens at `http://localhost:3000`. The included scripts and translated assets are selected through [public/game.conf](public/game.conf). Preserve the configured content paths when switching papers or languages.

## Generate new content

Install Python dependencies from this directory:

```bash
python -m pip install -r requirements.txt
cd Assest_generation_pipeline
```

Follow the [pipeline README](Assest_generation_pipeline/README.md) for conversion and service configuration. The directory spelling is intentional here because it matches the checked-in path.

For language selection, generated-content placement, controls, and troubleshooting, use [LongReadme.md](LongReadme.md).
