# Research Paper to Visual Novel — SARAL Megathon

A Megathon project that converts research papers into playable visual-novel experiences, with generated dialogue, translated content, and audio. The repository includes a React player, a Python asset-generation pipeline, and sample outputs.

## Start with the included visual novel

From the repository root:

```bash
cd Webrenpyvn
npm install
npm start
```

Open the development-server URL, normally `http://localhost:3000`. The included content and [public/game.conf](Webrenpyvn/public/game.conf) select the paper and language for playback. New paper conversion is a separate workflow and can require external services.

## Repository guide

| Path | Purpose |
|---|---|
| [Webrenpyvn/](Webrenpyvn/) | React player, configuration, and included content |
| [Webrenpyvn/LongReadme.md](Webrenpyvn/LongReadme.md) | Detailed setup, configuration, controls, and troubleshooting |
| [Webrenpyvn/Assest_generation_pipeline/](Webrenpyvn/Assest_generation_pipeline/) | PDF-to-visual-novel scripts; directory spelling is preserved |
| [Webrenpyvn/requirements.txt](Webrenpyvn/requirements.txt) | Python dependencies |
| [Webrenpyvn/outputs/](Webrenpyvn/outputs/) | Generated paper content |
| [Webrenpyvn/public/](Webrenpyvn/public/) | Assets served by the player |

### Generate content for another paper

Install Python dependencies from `Webrenpyvn`:

```bash
python -m pip install -r requirements.txt
cd Assest_generation_pipeline
```

Follow the pipeline's [README](Webrenpyvn/Assest_generation_pipeline/README.md) and the [full workflow](Webrenpyvn/LongReadme.md) for input placement, required service configuration, conversion, and copying generated content to the player. Language and content configuration live at the existing paths documented there.

## Project lineage and status

This is the canonical implemented Megathon project. [Final-mega-submit](https://github.com/J10Official/Final-mega-submit) and [Megathon](https://github.com/J10Official/Megathon) are historical submission/placeholder repositories.

The related [SARAL fork](https://github.com/J10Official/SARAL) originates from [DemocratiseResearch/SARAL](https://github.com/DemocratiseResearch/SARAL), which converts papers into educational videos. This repository's visual-novel implementation is a distinct project direction. Preserve upstream attribution and the included [MIT license](LICENSE).

Generated media and historical artifacts remain in their existing locations so player and pipeline paths continue to resolve.

## AI assistance disclosure

AI assistance was used during development. Assistance-session links are omitted from this public overview.
