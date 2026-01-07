# Daily Mail Comment Headlines (dmch)

A Python script that fetches the Daily Mail homepage and replaces article headlines with their top-rated comments, creating a humorous alternative view of the news.

## What it does

1. Fetches the Daily Mail homepage
2. Extracts all article headlines
3. For each article, fetches the top-rated comment
4. Replaces the headline text with the top comment
5. Outputs the modified page as `index.html`

## Usage

### Local Usage

```bash
pip install -r requirements.txt
python dmch.py
```

This will generate an `index.html` file in the current directory.

### Automated Updates with GitHub Actions

The repository includes a GitHub Actions workflow that:
- Runs every hour automatically
- Executes `dmch.py` to generate a fresh `index.html`
- Commits and pushes the changes
- Can be triggered manually from the Actions tab

### GitHub Pages

To serve the generated `index.html` with GitHub Pages:

1. Go to your repository Settings
2. Navigate to Pages
3. Under "Source", select "Deploy from a branch"
4. Select the branch containing `index.html` (e.g., `main` or `master`)
5. Click Save

Your page will be available at `https://[username].github.io/dmch/`

## Requirements

- Python 3.11+
- beautifulsoup4

## Credits

Inspired by the original Django/Google App Engine implementation at [jasoncartwright/dmcommentheadlines](https://github.com/jasoncartwright/dmcommentheadlines)