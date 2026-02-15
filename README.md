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
```

## Configuration

Edit `config/settings.yaml` to customize:
- Directories to scan
- Default time range
- Output preferences

## Example Output

See `examples/sample_output.txt` for a sample of the dashboard output.

## Requirements

- Python 3.7+
- GitPython
- colorama

## License

MIT License - Feel free to use and modify!
