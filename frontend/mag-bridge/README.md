# Running Frontend

## Prerequisites
1. Install [node.js](https://nodejs.org/en). LTS versions are recommended.
2. Open terminal in FE root folder (`dc-magnetic-data-calculator/frontend/mag-bridge`).
3. Run `npm i` to install frontend with all it's dependencies.

## Useful commands

### Running Frontend app
- (recommended) Running frontend via electron in development mode: `npm run dev`.

### Running installer build commands
In case of build issues, the `dist/electron` directory needs to be purged of any data. 
- MacOS: `npm run build:mac`.
- Windows:  `npm run build:win`.
- Linux:  `npm run build:linux`.
