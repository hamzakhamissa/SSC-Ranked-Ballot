# Ranked Ballot Calculator

A modern React + TypeScript application for calculating Borda count scores from ranked choice ballots.

## Features

- **Client-side processing**: No server required - runs entirely in the browser
- **Automatic rank detection**: Finds `Rank 1`, `Rank 2`, etc. columns automatically
- **Borda scoring**: Rank 1 gets k points, Rank k gets 1 point
- **Modern UI**: Clean, responsive interface built with React + TypeScript
- **GitHub Pages ready**: Deploys as a static site

## Usage

1. Upload a CSV file with ranked ballots
2. Set how many top candidates to display
3. Click "Calculate" to see results

### CSV Format

Your CSV should have columns like:
- `Rank 1`, `Rank 2`, `Rank 3`, etc.
- Other columns are ignored
- Candidate names in the rank columns

## Development

### Local Development
```bash
npm install
npm run dev
```

### Build for Production
```bash
npm run build
```

### Backend (Optional)
For local development with Flask backend:
```bash
cd backend
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python main.py your-file.csv --top 5
```

## GitHub Pages

This project is configured for GitHub Pages deployment:
- Builds to `dist/` folder
- Base path set to `/SSC-Ranked-Ballot/`
- No server required - pure client-side app

## Notes
- Works with any number of rank columns (not limited to 10)
- Handles CSV parsing with proper quote handling
- Ties are broken alphabetically