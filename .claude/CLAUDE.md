## MagBridge
This project is an innovative state-of-the-art cross-platform desktop app designed to fill key gaps in current chemical molecular magnetic data workflows. Built around user experience and powered by the industry-standard RDKit library, using SDF file formats in a streamlined workflow that helps researchers focus on discovery.

## Project Most Important Directories
1. module: [core]: `src/core/` - RDKit - absolute foundation. The whole project is one big "wrapper" around the library. This is where the development is most intensive at the moment.
2. module: [backend]: `backend/` - FastAPI - backend app, very basic and to be enhanced in the future
3. module: [frontend]: `frontend/` - Angular + Electron - frontend app, also very basic and left for future development.
4. `tests/` - We follow TDD, we have 500+ parametrized test cases overall. We use extensive various custom test automation tools. Our tests are deterministic. We put pressure on testing the `core` module's features, especially Substructure Matching, that has nearly 400 tests itself.
5. `data/` - contains SDF files - Text format storing multiple chemical structures and their associated data.
6. `notebooks/` - contains Jupyter Notebooks: (1) `notebooks/pubchem-tool.ipynb` used for generating new test cases. Custom API that outputs matching SMILES molecules given input SMARTS. Used manually by Magbridge Developers. (2) `notebooks/substruct-matching.ipynb` - Given `SubstructMatchTest` ID, allows to visualize given test case to highlight matched `BondType`s. Core Tool used by MagBridge Developers.

## Global Rules
- Never commit automatically. All commits are made manually by the developer.
- When working with `*.py` files, always use already installed **pyright-lsp@claude-plugins-official** plugin

## Architecture & Key Concepts
- Application's architecture was designed so it is a **localhost** application. There are no external resources required to run. The mindset behind this concept was to allow the users the peace of mind while working with their confidential experiments.
- Rdkit as base foundation for any `core` module's logic
- Configuration as Python - we don't use any additional databases / data processing systems in the production environment
