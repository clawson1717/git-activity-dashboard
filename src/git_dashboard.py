#!/usr/bin/env python3
"""
Git Activity Dashboard - A CLI tool for visualizing git activity across repos.
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Tuple

try:
    from git import Repo
    from git.exc import InvalidGitRepositoryError
except ImportError:
    print("Error: GitPython not installed. Run: pip install GitPython")
    sys.exit(1)

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    # Fallback if colorama not installed
    class Fore:
        CYAN = BLUE = GREEN = YELLOW = RED = MAGENTA = WHITE = ''
    class Style:
        BRIGHT = DIM = RESET_ALL = ''


def load_config(config_path: str = None) -> Dict:
    """Load configuration from YAML file."""
    import yaml
    
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    # Default config locations
    default_paths = [
        'config/settings.yaml',
        os.path.expanduser('~/.git-dashboard.yaml'),
        os.path.expanduser('~/.config/git-dashboard/settings.yaml'),
    ]
    
    for path in default_paths:
        if os.path.exists(path):
            with open(path, 'r') as f:
                return yaml.safe_load(f)
    
    # Return default config
    return {
        'scan_directories': [os.getcwd()],
        'default_days': 30,
        'max_repos': 50,
        'exclude_patterns': ['.git', 'node_modules', 'venv', '__pycache__'],
    }


def find_git_repos(base_path: str, exclude_patterns: List[str], max_repos: int = 50) -> List[Path]:
    """Recursively find git repositories."""
    repos = []
    base = Path(base_path).resolve()
    
    if not base.exists():
        return repos
    
    for path in base.rglob('.git'):
        repo_path = path.parent
        
        # Check if excluded
        if any(pattern in str(repo_path) for pattern in exclude_patterns):
            continue
        
        try:
            Repo(repo_path)
            repos.append(repo_path)
            if len(repos) >= max_repos:
                break
        except InvalidGitRepositoryError:
            continue
    
    return repos


def get_commit_stats(repo_path: Path, days: int) -> Dict:
    """Get commit statistics for a repository."""
    try:
        repo = Repo(repo_path)
    except InvalidGitRepositoryError:
        return None
    
    since_date = datetime.now() - timedelta(days=days)
    since_str = since_date.strftime('%Y-%m-%d')
    
    commits = []
    files_changed = 0
    insertions = 0
    deletions = 0
    daily_commits = defaultdict(int)
    
    try:
        for commit in repo.iter_commits('HEAD', since=since_str):
            commit_date = datetime.fromtimestamp(commit.committed_date)
            commits.append({
                'hash': commit.hexsha[:8],
                'message': commit.message.strip(),
                'author': str(commit.author),
                'date': commit_date,
            })
            daily_commits[commit_date.strftime('%Y-%m-%d')] += 1
        
        # Get diff stats if we have commits
        if commits:
            try:
                # Get stats from the last commit
                latest_commit = repo.head.commit
                if latest_commit.parents:
                    diff = latest_commit.parents[0].diff(latest_commit, create_patch=False)
                    files_changed = sum(1 for _ in diff)
                    
                    # Get line stats using git show --stat
                    result = subprocess.run(
                        ['git', '-C', str(repo_path), 'show', '--stat', '--oneline', 'HEAD'],
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        # Parse the stat output
                        lines = result.stdout.strip().split('\n')
                        if lines:
                            last_line = lines[-1]
                            if 'insertion' in last_line or 'deletion' in last_line:
                                parts = last_line.split(',')
                                for part in parts:
                                    if 'insertion' in part:
                                        insertions = int(part.strip().split()[0])
                                    elif 'deletion' in part:
                                        deletions = int(part.strip().split()[0])
            except Exception:
                pass
    
    except Exception as e:
        pass
    
    return {
        'name': repo_path.name,
        'path': str(repo_path),
        'total_commits': len(commits),
        'files_changed': files_changed,
        'insertions': insertions,
        'deletions': deletions,
        'commits': commits[:10],  # Last 10 commits
        'daily_commits': dict(daily_commits),
    }


def draw_bar_chart(daily_data: Dict[str, int], days: int) -> str:
    """Draw an ASCII bar chart of daily activity."""
    if not daily_data:
        return "  No activity data available."
    
    # Generate date range
    dates = []
    for i in range(days - 1, -1, -1):
        date_str = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        dates.append(date_str)
    
    # Get values for the range
    values = [daily_data.get(d, 0) for d in dates]
    
    if not values or max(values) == 0:
        return "  No commits in this period."
    
    # Draw chart
    max_val = max(values)
    chart_height = 10
    lines = []
    
    # Header
    lines.append(f"\n{Fore.CYAN}{Style.BRIGHT}  Daily Activity (Last {days} Days){Style.RESET_ALL}")
    lines.append(f"  {Fore.DIM}{'─' * 60}{Style.RESET_ALL}")
    
    # Chart area
    for i in range(chart_height, 0, -1):
        threshold = (i / chart_height) * max_val
        line = f"  {Fore.DIM}{i * max_val // chart_height:3d} │{Style.RESET_ALL}"
        for val in values[-14:]:  # Show last 14 days for width
            if val >= threshold:
                line += f"{Fore.GREEN}█{Style.RESET_ALL}"
            else:
                line += " "
        lines.append(line)
    
    # X-axis
    lines.append(f"  {Fore.DIM}    └{'─' * min(len(values), 14)}{Style.RESET_ALL}")
    
    # Date labels (show first and last)
    if len(dates) >= 14:
        first_date = dates[-14]
        last_date = dates[-1]
        lines.append(f"  {Fore.DIM}     {first_date}  →  {last_date}{Style.RESET_ALL}")
    
    return '\n'.join(lines)


def format_stat(label: str, value: int, color: str = Fore.WHITE) -> str:
    """Format a statistic line."""
    return f"  {Fore.DIM}{label:20s}{Style.RESET_ALL} {color}{Style.BRIGHT}{value:>8d}{Style.RESET_ALL}"


def display_dashboard(stats_list: List[Dict], days: int):
    """Display the activity dashboard."""
    # Header
    print(f"\n{Fore.CYAN}{'═' * 70}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'🔥 GIT ACTIVITY DASHBOARD':^70s}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'═' * 70}{Style.RESET_ALL}\n")
    
    # Summary stats
    total_commits = sum(s['total_commits'] for s in stats_list)
    total_repos = len(stats_list)
    active_repos = sum(1 for s in stats_list if s['total_commits'] > 0)
    
    print(f"{Fore.YELLOW}{Style.BRIGHT}📊 SUMMARY{Style.RESET_ALL}")
    print(f"  {Fore.DIM}{'─' * 40}{Style.RESET_ALL}")
    print(format_stat("Repositories scanned:", total_repos, Fore.CYAN))
    print(format_stat("Active repositories:", active_repos, Fore.GREEN))
    print(format_stat(f"Total commits ({days} days):", total_commits, Fore.YELLOW))
    print()
    
    # Per-repo stats
    print(f"{Fore.YELLOW}{Style.BRIGHT}📁 REPOSITORY BREAKDOWN{Style.RESET_ALL}")
    print(f"  {Fore.DIM}{'─' * 60}{Style.RESET_ALL}")
    print(f"  {'Repository':<25} {'Commits':>8} {'Files':>8} {'+/-':>12}")
    print(f"  {Fore.DIM}{'─' * 60}{Style.RESET_ALL}")
    
    # Sort by commit count
    sorted_stats = sorted(stats_list, key=lambda x: x['total_commits'], reverse=True)
    
    for stat in sorted_stats:
        if stat['total_commits'] > 0:
            color = Fore.GREEN if stat['total_commits'] > 5 else Fore.YELLOW if stat['total_commits'] > 0 else Fore.DIM
            changes = f"+{stat['insertions']}/-{stat['deletions']}"
            print(f"  {color}{stat['name']:<25}{Style.RESET_ALL} {stat['total_commits']:>8} {stat['files_changed']:>8} {Fore.CYAN}{changes:>12}{Style.RESET_ALL}")
    
    # Aggregate daily activity chart
    all_daily = defaultdict(int)
    for stat in stats_list:
        for date, count in stat['daily_commits'].items():
            all_daily[date] += count
    
    print(draw_bar_chart(all_daily, days))
    
    # Recent commits
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}📝 RECENT COMMITS{Style.RESET_ALL}")
    print(f"  {Fore.DIM}{'─' * 60}{Style.RESET_ALL}")
    
    all_commits = []
    for stat in stats_list:
        for commit in stat['commits']:
            commit['repo'] = stat['name']
            all_commits.append(commit)
    
    # Sort by date
    all_commits.sort(key=lambda x: x['date'], reverse=True)
    
    for commit in all_commits[:15]:  # Show last 15 commits
        date_str = commit['date'].strftime('%m/%d %H:%M')
        message = commit['message'].split('\n')[0][:40]  # First line, truncated
        print(f"  {Fore.DIM}{date_str}{Style.RESET_ALL} {Fore.CYAN}{commit['repo']:<15}{Style.RESET_ALL} {Fore.WHITE}{message}{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}{'═' * 70}{Style.RESET_ALL}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Git Activity Dashboard - Visualize git activity across repositories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python src/git_dashboard.py                    # Use default config
  python src/git_dashboard.py -p ~/projects      # Scan specific directory
  python src/git_dashboard.py -d 7               # Show last 7 days
        '''
    )
    parser.add_argument('-p', '--path', help='Directory to scan for git repositories')
    parser.add_argument('-d', '--days', type=int, default=30, help='Number of days to analyze (default: 30)')
    parser.add_argument('-c', '--config', help='Path to config file')
    parser.add_argument('--max-repos', type=int, default=50, help='Maximum repositories to scan')
    
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    
    # Determine scan paths
    if args.path:
        scan_paths = [args.path]
    else:
        scan_paths = config.get('scan_directories', [os.getcwd()])
    
    days = args.days or config.get('default_days', 30)
    max_repos = args.max_repos or config.get('max_repos', 50)
    exclude_patterns = config.get('exclude_patterns', ['.git', 'node_modules'])
    
    print(f"{Fore.CYAN}🔍 Scanning for git repositories...{Style.RESET_ALL}")
    
    # Find all repos
    all_repos = []
    for scan_path in scan_paths:
        repos = find_git_repos(scan_path, exclude_patterns, max_repos)
        all_repos.extend(repos)
        if len(all_repos) >= max_repos:
            all_repos = all_repos[:max_repos]
            break
    
    if not all_repos:
        print(f"{Fore.RED}No git repositories found!{Style.RESET_ALL}")
        sys.exit(1)
    
    print(f"{Fore.GREEN}Found {len(all_repos)} repositories{Style.RESET_ALL}")
    
    # Analyze each repo
    stats_list = []
    for repo_path in all_repos:
        stats = get_commit_stats(repo_path, days)
        if stats:
            stats_list.append(stats)
    
    # Display dashboard
    display_dashboard(stats_list, days)


if __name__ == '__main__':
    main()
