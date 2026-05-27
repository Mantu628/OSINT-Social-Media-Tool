#!/usr/bin/env python3
"""
OSINT Social Media Tool - Command Line Interface
Professional OSINT tool for social media information gathering
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List

import click
import yaml
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.panel import Panel

# Setup
console = Console()
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load configuration
def load_config():
    """Load configuration from config.yaml"""
    config_path = PROJECT_ROOT / 'config.yaml'
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

CONFIG = load_config()

# ============================================================================
# CLI Group
# ============================================================================

@click.group()
@click.version_option(version='1.0.0', prog_name='OSINT Tool')
def cli():
    """
    OSINT Social Media Tool
    Professional intelligence gathering for cybersecurity professionals
    """
    pass

# ============================================================================
# Search Commands
# ============================================================================

@cli.command()
@click.option(
    '--username',
    required=False,
    help='Target username to search for'
)
@click.option(
    '--email',
    required=False,
    help='Email address to search for'
)
@click.option(
    '--phone',
    required=False,
    help='Phone number to search for'
)
@click.option(
    '--hashtag',
    required=False,
    help='Hashtag to search for'
)
@click.option(
    '--location',
    required=False,
    help='Location to search for'
)
@click.option(
    '--platforms',
    default='all',
    help='Comma-separated list of platforms (twitter,instagram,facebook,linkedin,reddit,tiktok,youtube)'
)
@click.option(
    '--limit',
    type=int,
    default=100,
    help='Maximum number of results'
)
@click.option(
    '--output',
    type=click.Path(),
    help='Output file path (csv, json, xlsx)'
)
@click.option(
    '--proxy',
    help='Proxy URL (http://proxy:port)'
)
@click.option(
    '--delay',
    type=int,
    default=1,
    help='Delay between requests in seconds'
)
def search(username, email, phone, hashtag, location, platforms, limit, output, proxy, delay):
    """Search for information across social media platforms"""
    
    try:
        # Validate input
        if not any([username, email, phone, hashtag, location]):
            console.print("[red]Error: Please provide at least one search parameter[/red]")
            sys.exit(1)
        
        # Determine search type
        search_type = 'username' if username else \
                     'email' if email else \
                     'phone' if phone else \
                     'hashtag' if hashtag else \
                     'location'
        
        query = username or email or phone or hashtag or location
        
        console.print(f"\n[bold cyan]OSINT Search[/bold cyan]")
        console.print(f"Query: {query}")
        console.print(f"Type: {search_type}")
        console.print(f"Platforms: {platforms}\n")
        
        # Import search engine
        from core.search_engine import SearchEngine
        
        # Initialize search engine
        search_engine = SearchEngine(CONFIG)
        
        # Parse platforms
        platform_list = ['all'] if platforms.lower() == 'all' else [p.strip() for p in platforms.split(',')]
        
        # Perform search
        console.print("[yellow]Searching... Please wait[/yellow]")
        
        results = search_engine.search(
            query=query,
            search_type=search_type,
            platforms=platform_list,
            limit=limit,
            proxy=proxy,
            delay=delay
        )
        
        # Display results
        if results:
            console.print(f"\n[green]Found {len(results)} result(s)[/green]\n")
            
            # Create table
            table = Table(title="Search Results")
            table.add_column("Platform", style="cyan")
            table.add_column("Username", style="magenta")
            table.add_column("Name", style="green")
            table.add_column("Followers", style="yellow")
            table.add_column("Verified", style="blue")
            
            for result in results[:20]:  # Show first 20
                table.add_row(
                    result.get('platform', 'N/A'),
                    result.get('username', 'N/A'),
                    result.get('full_name', 'N/A'),
                    str(result.get('followers', 'N/A')),
                    '✓' if result.get('verified') else '✗'
                )
            
            console.print(table)
            
            # Export if requested
            if output:
                export_results(results, output)
                console.print(f"\n[green]Results exported to: {output}[/green]")
        else:
            console.print("[yellow]No results found[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.option('--tag', required=True, help='Hashtag to analyze')
@click.option('--platforms', default='all', help='Comma-separated list of platforms')
@click.option('--limit', type=int, default=100, help='Maximum number of posts')
@click.option('--output', type=click.Path(), help='Output file path')
def hashtag(tag, platforms, limit, output):
    """Analyze hashtag usage and trends"""
    
    try:
        console.print(f"\n[bold cyan]Hashtag Analysis[/bold cyan]")
        console.print(f"Tag: #{tag}")
        console.print(f"Limit: {limit}\n")
        
        from core.hashtag_analyzer import HashtagAnalyzer
        
        analyzer = HashtagAnalyzer(CONFIG)
        
        platform_list = ['all'] if platforms.lower() == 'all' else [p.strip() for p in platforms.split(',')]
        
        console.print("[yellow]Analyzing hashtag... Please wait[/yellow]")
        
        results = analyzer.analyze(tag, platform_list, limit)
        
        if results:
            console.print(f"\n[green]Found {len(results)} post(s)[/green]\n")
            
            # Create table
            table = Table(title=f"Hashtag: #{tag}")
            table.add_column("Platform", style="cyan")
            table.add_column("Author", style="magenta")
            table.add_column("Content", style="green", width=40)
            table.add_column("Engagement", style="yellow")
            
            for post in results[:10]:  # Show first 10
                content = post.get('content', '')[:40] + '...' if len(post.get('content', '')) > 40 else post.get('content', '')
                engagement = post.get('likes', 0) + post.get('shares', 0) + post.get('comments', 0)
                
                table.add_row(
                    post.get('platform', 'N/A'),
                    post.get('author', 'N/A'),
                    content,
                    str(engagement)
                )
            
            console.print(table)
            
            if output:
                export_results(results, output)
                console.print(f"\n[green]Results exported to: {output}[/green]")
        else:
            console.print("[yellow]No posts found[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.option('--email', required=True, help='Email address to lookup')
@click.option('--output', type=click.Path(), help='Output file path')
def email_lookup(email, output):
    """Lookup social media accounts by email"""
    
    try:
        console.print(f"\n[bold cyan]Email Lookup[/bold cyan]")
        console.print(f"Email: {email}\n")
        
        from core.lookup import EmailLookup
        
        lookup = EmailLookup(CONFIG)
        
        console.print("[yellow]Searching... Please wait[/yellow]")
        
        results = lookup.search(email)
        
        if results:
            console.print(f"\n[green]Found {len(results)} account(s)[/green]\n")
            
            table = Table(title="Email Lookup Results")
            table.add_column("Platform", style="cyan")
            table.add_column("Username", style="magenta")
            table.add_column("URL", style="green")
            
            for result in results:
                table.add_row(
                    result.get('platform', 'N/A'),
                    result.get('username', 'N/A'),
                    result.get('url', 'N/A')
                )
            
            console.print(table)
            
            if output:
                export_results(results, output)
                console.print(f"\n[green]Results exported to: {output}[/green]")
        else:
            console.print("[yellow]No accounts found[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.option('--phone', required=True, help='Phone number to lookup')
@click.option('--output', type=click.Path(), help='Output file path')
def phone_lookup(phone, output):
    """Lookup social media accounts by phone number"""
    
    try:
        console.print(f"\n[bold cyan]Phone Lookup[/bold cyan]")
        console.print(f"Phone: {phone}\n")
        
        from core.lookup import PhoneLookup
        
        lookup = PhoneLookup(CONFIG)
        
        console.print("[yellow]Searching... Please wait[/yellow]")
        
        results = lookup.search(phone)
        
        if results:
            console.print(f"\n[green]Found {len(results)} account(s)[/green]\n")
            
            table = Table(title="Phone Lookup Results")
            table.add_column("Platform", style="cyan")
            table.add_column("Username", style="magenta")
            table.add_column("URL", style="green")
            
            for result in results:
                table.add_row(
                    result.get('platform', 'N/A'),
                    result.get('username', 'N/A'),
                    result.get('url', 'N/A')
                )
            
            console.print(table)
            
            if output:
                export_results(results, output)
                console.print(f"\n[green]Results exported to: {output}[/green]")
        else:
            console.print("[yellow]No accounts found[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

# ============================================================================
# Analysis Commands
# ============================================================================

@cli.command()
@click.option('--username', required=True, help='Username to analyze')
@click.option('--platform', default='twitter', help='Platform name')
@click.option('--limit', type=int, default=100, help='Number of posts to analyze')
@click.option('--output', type=click.Path(), help='Output file path')
def sentiment(username, platform, limit, output):
    """Analyze sentiment of user posts"""
    
    try:
        console.print(f"\n[bold cyan]Sentiment Analysis[/bold cyan]")
        console.print(f"User: @{username}")
        console.print(f"Platform: {platform}\n")
        
        from core.sentiment_analyzer import SentimentAnalyzer
        
        analyzer = SentimentAnalyzer(CONFIG)
        
        console.print("[yellow]Analyzing sentiment... Please wait[/yellow]")
        
        results = analyzer.analyze(username, platform, limit)
        
        if results:
            console.print(f"\n[green]Analysis complete[/green]\n")
            
            # Display statistics
            table = Table(title="Sentiment Statistics")
            table.add_column("Sentiment", style="cyan")
            table.add_column("Count", style="magenta")
            table.add_column("Percentage", style="green")
            
            total = results.get('total', 0)
            for sentiment, count in results.get('distribution', {}).items():
                percentage = (count / total * 100) if total > 0 else 0
                table.add_row(sentiment.capitalize(), str(count), f"{percentage:.1f}%")
            
            console.print(table)
            
            if output:
                export_results(results, output)
                console.print(f"\n[green]Results exported to: {output}[/green]")
        else:
            console.print("[yellow]No data to analyze[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.option('--username', required=True, help='Username to analyze')
@click.option('--platform', default='twitter', help='Platform name')
@click.option('--depth', type=int, default=2, help='Network depth')
@click.option('--output', type=click.Path(), help='Output file path')
def network(username, platform, depth, output):
    """Analyze user network and connections"""
    
    try:
        console.print(f"\n[bold cyan]Network Analysis[/bold cyan]")
        console.print(f"User: @{username}")
        console.print(f"Platform: {platform}")
        console.print(f"Depth: {depth}\n")
        
        from core.network_analyzer import NetworkAnalyzer
        
        analyzer = NetworkAnalyzer(CONFIG)
        
        console.print("[yellow]Building network graph... Please wait[/yellow]")
        
        graph_data = analyzer.analyze(username, platform, depth)
        
        if graph_data:
            console.print(f"\n[green]Network analysis complete[/green]\n")
            
            # Display network statistics
            table = Table(title="Network Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            table.add_row("Total Nodes", str(len(graph_data.get('nodes', []))))
            table.add_row("Total Connections", str(len(graph_data.get('edges', []))))
            table.add_row("Density", f"{graph_data.get('metrics', {}).get('density', 0):.2f}")
            
            console.print(table)
            
            if output:
                export_results(graph_data, output)
                console.print(f"\n[green]Graph exported to: {output}[/green]")
        else:
            console.print("[yellow]Could not build network graph[/yellow]")
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

# ============================================================================
# Report Commands
# ============================================================================

@cli.command()
@click.option('--username', required=True, help='Username to generate report for')
@click.option('--platform', required=True, help='Platform name')
@click.option('--format', type=click.Choice(['pdf', 'html', 'docx']), default='pdf', help='Report format')
@click.option('--include-timeline', is_flag=True, help='Include timeline analysis')
@click.option('--include-network', is_flag=True, help='Include network graph')
@click.option('--output', type=click.Path(), help='Output file path')
def report(username, platform, format, include_timeline, include_network, output):
    """Generate comprehensive investigation report"""
    
    try:
        console.print(f"\n[bold cyan]Report Generation[/bold cyan]")
        console.print(f"User: @{username}")
        console.print(f"Platform: {platform}")
        console.print(f"Format: {format}\n")
        
        from core.report_generator import ReportGenerator
        
        generator = ReportGenerator(CONFIG)
        
        console.print("[yellow]Generating report... Please wait[/yellow]")
        
        report_path = generator.generate(
            username=username,
            platform=platform,
            format_type=format,
            include_timeline=include_timeline,
            include_network=include_network,
            output_path=output
        )
        
        console.print(f"\n[green]Report generated successfully[/green]")
        console.print(f"Location: {report_path}")
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

# ============================================================================
# Configuration Commands
# ============================================================================

@cli.command()
def config():
    """Show current configuration"""
    
    try:
        console.print("\n[bold cyan]Configuration[/bold cyan]\n")
        
        # Display server config
        server_config = CONFIG.get('server', {})
        console.print("[bold]Server Configuration:[/bold]")
        for key, value in server_config.items():
            console.print(f"  {key}: {value}")
        
        # Display platform config
        platforms_config = CONFIG.get('platforms', {})
        console.print("\n[bold]Enabled Platforms:[/bold]")
        for platform, settings in platforms_config.items():
            if settings.get('enabled'):
                console.print(f"  ✓ {platform.capitalize()}")
        
        # Display features
        features = CONFIG.get('features', {})
        console.print("\n[bold]Enabled Features:[/bold]")
        for feature, enabled in features.items():
            if isinstance(enabled, bool) and enabled:
                console.print(f"  ✓ {feature}")
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.option('--name', required=True, help='Configuration name')
@click.option('--platforms', default='all', help='Comma-separated platforms')
@click.option('--limit', type=int, default=100, help='Default result limit')
def save_config(name, platforms, limit):
    """Save search configuration"""
    
    try:
        config_data = {
            'name': name,
            'platforms': platforms.split(','),
            'limit': limit,
            'created_at': datetime.now().isoformat()
        }
        
        config_dir = PROJECT_ROOT / 'saved_configs'
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / f'{name}.json'
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        console.print(f"[green]Configuration saved: {config_file}[/green]")
    
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

# ============================================================================
# Utility Functions
# ============================================================================

def export_results(results, output_path):
    """Export results to file"""
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.suffix.lower() == '.json':
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
    
    elif output_path.suffix.lower() == '.csv':
        try:
            import pandas as pd
            df = pd.DataFrame(results)
            df.to_csv(output_path, index=False)
        except ImportError:
            console.print("[red]pandas required for CSV export[/red]")
    
    elif output_path.suffix.lower() == '.xlsx':
        try:
            import pandas as pd
            df = pd.DataFrame(results)
            df.to_excel(output_path, index=False)
        except ImportError:
            console.print("[red]openpyxl required for XLSX export[/red]")

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Fatal error: {str(e)}[/red]")
        sys.exit(1)
