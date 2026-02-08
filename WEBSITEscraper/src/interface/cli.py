import asyncio
import argparse
import json
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

from ..core.config import settings
from ..core.browser import browser_manager
from ..engine.crawler import Crawler
from ..pipeline.extractor import extractor

console = Console()

async def run_scraper(url: str, depth: int, output_file: str = None, gdocs: bool = False):
    """
    Orchestrates the scraping process.
    """
    # Override settings if needed
    settings.MAX_DEPTH = depth
    
    console.print(Panel(f"[bold green]Starting Industrial Scraper[/bold green]\nURL: {url}\nDepth: {depth}", title="Configuration"))

    crawler = Crawler(browser_manager)
    
    results = []
    
    try:
        await browser_manager.start()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task_id = progress.add_task(f"Crawling {url}...", total=None)
            
            # 1. Crawl
            raw_data = await crawler.crawl(url)
            console.print(f"[green]✓[/green] Crawled {len(raw_data)} pages.")
            
            # 2. Extract
            progress.update(task_id, description="Extracting ESG data...")
            
            table = Table(title="Scraping Results")
            table.add_column("URL", style="cyan")
            table.add_column("Company", style="magenta")
            table.add_column("ESG Score (Avg)", justify="right")
            
            for page in raw_data:
                # Basic filter: only process if content length is substantial
                if len(page['content']) < 1000:
                    continue
                    
                report = extractor.extract(page['content'], page['url'])
                
                if report:
                    results.append(report.dict())
                    
                    # Calculate average score for display
                    avg_score = (report.environmental.score + report.social.score + report.governance.score) / 3
                    table.add_row(report.url[:50] + "...", report.company_name, f"{avg_score:.1f}")
                    
                    # 3. GDocs Export (Immediate per item)
                    if gdocs:
                        from ..pipeline.export_gdocs import find_or_create_esg_doc, append_esg_analysis
                        try:
                            doc_id = find_or_create_esg_doc("ESG Master Report")
                            if doc_id:
                                link = append_esg_analysis(doc_id, report)
                                console.print(f"[blue]Exported to GDoc: {link}[/blue]")
                        except Exception as e:
                            console.print(f"[red]GDocs Export Failed: {e}[/red]")
                else:
                    console.print(f"[red]Extraction failed for {page['url']}[/red]")
            
            console.print(table)
            
            # 4. JSON Export
            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2)
                console.print(f"[bold blue]Exported results to {output_file}[/bold blue]")
                
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
    finally:
        await browser_manager.stop()

def main():
    parser = argparse.ArgumentParser(description="Industrial Grade ESG Scraper")
    parser.add_argument("url", help="Target URL to scrape")
    parser.add_argument("--depth", type=int, default=1, help="Crawl depth (default: 1)")
    parser.add_argument("--output", "-o", help="Output JSON file path", default="results.json")
    parser.add_argument("--gdocs", "-g", action="store_true", help="Export to Google Docs")
    
    args = parser.parse_args()
    
    asyncio.run(run_scraper(args.url, args.depth, args.output, args.gdocs))

if __name__ == "__main__":
    main()
