# Running the Frontend

## Prerequisites

1. Install Node.js (https://nodejs.org/en) — the latest LTS version is recommended.  
2. Open a terminal in the frontend root folder:
   `cd dc-magnetic-data-calculator/frontend/mag-bridge`
3. Install dependencies:
   `npm install`

   💡 Note:
   npm install uses both package.json and package-lock.json to ensure consistent dependency versions.
   Avoid deleting package-lock.json, as it helps keep environments identical across machines.

## Useful Commands

### Running the Frontend App

Recommended (development mode):
   `npm run dev`

This command runs the Angular development server with Hot Module Replacement (HMR)
and launches the Electron app for live-reload development.

### Building Installer Packages

If you encounter build issues, delete the dist/electron directory before rebuilding.

macOS:
   `npm run build:mac`

Windows:
   `npm run build:win`

Linux:
   `npm run build:linux`

## Common Issues

- Build errors after switching branches:
   Remove the dist/electron directory and rebuild using the appropriate build command.
