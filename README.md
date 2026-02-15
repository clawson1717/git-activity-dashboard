# 🔥 Git Activity Dashboard

A CLI tool that visualizes git activity across multiple repositories. Get insights into your coding activity with colorful terminal charts and statistics.

## Features

- 📊 **Multi-repo scanning** - Scan directories for git repositories
- 📈 **Activity visualization** - ASCII bar charts of daily commit activity
- 📋 **Detailed statistics** - Commits per repo, files changed, lines added/removed
- 🎨 **Colorful terminal UI** - Beautiful colored output with colorama
- ⚙️ **Configurable** - YAML-based configuration for directories to scan

## Installation

```bash
# Clone the repository
git clone https://github.com/clawson1717/git-activity-dashboard.git
cd git-activity-dashboard

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run with default config
python src/git_dashboard.py

# Run with custom directory
python src/git_dashboard.py --path /path/to/projects

# Show last N days (default: 30)
python src/git_dashboard.py --days 7

# Export activity data to JSON
python src/git_dashboard.py --export-json

# Exclude specific directories (can be used multiple times)
python src/git_dashboard.py --exclude node_modules --exclude vendor

# Use only CLI exclusions (ignore config file exclusions)
python src/git_dashboard.py --exclude .git --no-exclude-from-config
```

### JSON Export

The `--export-json` option exports all collected git activity data to a timestamped JSON file in `~/.git-dashboard/output/`. This enables integration with other tools and custom dashboard building.

**JSON Structure:**
- `metadata`: Export timestamp, analysis period, and version
- `summary`: Aggregated statistics (repositories scanned, total commits, files changed, lines added/removed)
- `daily_activity`: Daily commit counts across all repositories
- `repositories`: Detailed per-repository data including:
  - Repository name and path
  - Commit counts
  - Files changed and line statistics
  - Daily activity breakdown
  - Recent commits with hash, message, author, and date

## Configuration

Edit `config/settings.yaml` to customize:
- Directories to scan
- Default time range
- Output preferences
- Exclude patterns for directories to skip

### Exclude Patterns

By default, the scanner excludes common dependency and cache directories:
- `node_modules` - Node.js dependencies
- `.git` - Git internals
- `__pycache__` - Python cache
- `.venv`, `venv` - Python virtual environments
- `vendor` - Vendor directories (Go, PHP, etc.)

You can customize exclusions in `config/settings.yaml`:

```yaml
exclude_patterns:
  - .git
  - node_modules
  - venv
  - __pycache__
  - vendor
  - target  # Rust build directory
  - dist    # Build output
```

Or use the `--exclude` CLI option to add exclusions on-the-fly.

## Example Output

See `examples/sample_output.txt` for a sample of the dashboard output.

## Requirements

- Python 3.7+
- GitPython
- colorama

## License

MIT License - Feel free to use and modify!
