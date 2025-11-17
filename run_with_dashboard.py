#!/usr/bin/env python3
"""
Enhanced Obsidian Auto-Linker Runner with Live Dashboard
Optimized for MacBook Air M4 2025
"""

import os
import sys
import signal
import time
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional

# Import dashboard and logger
from live_dashboard import LiveDashboard, get_dashboard
from logger_config import setup_logging, get_logger, DashboardLogHandler
from rich.live import Live
from rich.console import Console

console = Console()
logger = None
dashboard = None


class EnhancedRunner:
    """Enhanced runner with live dashboard integration"""

    def __init__(self, update_interval: int = 15):
        global logger, dashboard

        self.update_interval = update_interval
        self.running = False
        self.config = {}

        # Initialize dashboard
        dashboard = get_dashboard(update_interval=update_interval)

        # Initialize logging
        logger = setup_logging(log_level="INFO", enable_file_logging=True)

        # Add dashboard handler to logger
        dashboard_handler = DashboardLogHandler(dashboard)
        logger.addHandler(dashboard_handler)

        # Signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        logger.info("Stopping process...")
        self.running = False
        dashboard.stop()

        # Show final stats
        console.print("\n[bold green]✓ Process stopped safely[/bold green]")
        console.print(f"\n[bold]Final Statistics:[/bold]")
        console.print(f"  Processed: {dashboard.stats['processed_files']}/{dashboard.stats['total_files']}")
        console.print(f"  Failed: {dashboard.stats['failed_files']}")
        console.print(f"  Duration: {datetime.now() - dashboard.stats['start_time']}")

        sys.exit(0)

    def load_config(self) -> bool:
        """Load configuration from config.yaml"""
        config_file = Path('config.yaml')

        if not config_file.exists():
            logger.error("config.yaml not found. Please run setup first.")
            return False

        try:
            with open(config_file, 'r') as f:
                self.config = yaml.safe_load(f) or {}

            # Validate required fields
            required_fields = ['vault_path', 'ollama_model']
            missing = [field for field in required_fields if field not in self.config]

            if missing:
                logger.error(f"Missing required config fields: {', '.join(missing)}")
                return False

            # Validate vault path
            vault_path = Path(self.config['vault_path'])
            if not vault_path.exists():
                logger.error(f"Vault path does not exist: {vault_path}")
                return False

            logger.info(f"Configuration loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return False

    def check_ollama(self) -> bool:
        """Check if Ollama is running"""
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=5)

            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    logger.info(f"Ollama is running with {len(models)} models")
                    return True
                else:
                    logger.error("Ollama is running but no models are loaded")
                    return False
            else:
                logger.error("Ollama is not responding properly")
                return False
        except Exception as e:
            logger.error(f"Ollama connection failed: {e}")
            logger.info("Please start Ollama: ollama serve")
            return False

    def interactive_setup(self) -> bool:
        """Interactive configuration setup"""
        console.print("[bold cyan]=" * 40 + "[/bold cyan]")
        console.print("[bold white]OBSIDIAN AUTO-LINKER - ENHANCED SETUP[/bold white]")
        console.print("[bold cyan]=" * 40 + "[/bold cyan]\n")

        # Load existing config if available
        try:
            with open('config.yaml', 'r') as f:
                existing_config = yaml.safe_load(f) or {}
        except FileNotFoundError:
            existing_config = {}
        except (yaml.YAMLError, IOError) as e:
            logger.warning(f"Error loading config: {e}")
            existing_config = {}

        # Vault path
        default_vault = existing_config.get('vault_path', '/Users/medici/Documents/MediciVault')
        console.print(f"[bold]📁 Vault Path[/bold] (default: {default_vault})")

        try:
            vault_path = input("   Enter path or press Enter for default: ").strip()
        except EOFError:
            vault_path = default_vault
            console.print(f"   Using default: {vault_path}")

        if not vault_path:
            vault_path = default_vault

        if not Path(vault_path).exists():
            console.print(f"[bold red]❌ Path does not exist: {vault_path}[/bold red]")
            return False

        # File ordering
        console.print("\n[bold]📋 File Processing Order:[/bold]")
        console.print("   1. Recent (newest first)")
        console.print("   2. Size (largest first)")
        console.print("   3. Random")
        console.print("   4. Alphabetical")

        try:
            order_choice = input("   Choose (1-4, default=1): ").strip()
        except EOFError:
            order_choice = "1"

        order_map = {'1': 'recent', '2': 'size', '3': 'random', '4': 'alphabetical'}
        file_ordering = order_map.get(order_choice, 'recent')

        # Processing mode
        console.print("\n[bold]🔧 Processing Mode:[/bold]")
        console.print("   1. Fast Dry Run (no AI, quick test)")
        console.print("   2. Full Dry Run (with AI, no file changes)")
        console.print("   3. Live Run (creates _linked.md files)")

        try:
            mode_choice = input("   Choose (1-3, default=1): ").strip()
        except EOFError:
            mode_choice = "1"

        if mode_choice == "1":
            dry_run, fast_dry_run = True, True
        elif mode_choice == "2":
            dry_run, fast_dry_run = True, False
        else:
            dry_run, fast_dry_run = False, False

        # Batch size
        console.print("\n[bold]📦 Batch Size:[/bold]")
        console.print("   1. Single file (recommended)")
        console.print("   2. Small batch (5 files)")
        console.print("   3. Medium batch (10 files)")

        try:
            batch_choice = input("   Choose (1-3, default=1): ").strip()
        except EOFError:
            batch_choice = "1"

        batch_map = {'1': 1, '2': 5, '3': 10}
        batch_size = batch_map.get(batch_choice, 1)

        # Parallel processing
        console.print("\n[bold]⚡ Parallel Processing:[/bold]")
        default_parallel_enabled = existing_config.get('parallel_processing_enabled', False)
        parallel_prompt = "Y/n" if default_parallel_enabled else "y/N"
        try:
            parallel_choice = input(
                f"   Enable parallel processing? ({parallel_prompt}, default={'on' if default_parallel_enabled else 'off'}): "
            ).strip().lower()
        except EOFError:
            parallel_choice = 'y' if default_parallel_enabled else 'n'

        parallel_processing_enabled = (
            parallel_choice in ['y', 'yes']
            if parallel_choice
            else default_parallel_enabled
        )

        default_workers = existing_config.get('parallel_workers', 1)
        parallel_workers = default_workers

        if parallel_processing_enabled:
            try:
                workers_input = input(
                    f"   Parallel workers (1-16, default={default_workers}): "
                ).strip()
            except EOFError:
                workers_input = ""

            if workers_input:
                try:
                    parsed_workers = int(workers_input)
                    if 1 <= parsed_workers <= 16:
                        parallel_workers = parsed_workers
                    else:
                        console.print("[yellow]Using default worker count (must be 1-16).[/yellow]")
                except ValueError:
                    console.print("[yellow]Invalid number, using default worker count.[/yellow]")

        # Save configuration
        self.config = {
            'vault_path': vault_path,
            'file_ordering': file_ordering,
            'dry_run': dry_run,
            'fast_dry_run': fast_dry_run,
            'batch_size': batch_size,
            'parallel_processing_enabled': parallel_processing_enabled,
            'parallel_workers': parallel_workers,
            'ollama_base_url': existing_config.get('ollama_base_url', 'http://localhost:11434'),
            'ollama_model': existing_config.get('ollama_model', 'qwen2.5:3b'),
        }

        try:
            with open('config.yaml', 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            logger.info("Configuration saved to config.yaml")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

        # Show summary
        console.print("\n[bold green]✓ Configuration Complete[/bold green]")
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  Vault: {vault_path}")
        console.print(f"  Ordering: {file_ordering}")
        console.print(f"  Mode: {'Fast Dry Run' if fast_dry_run else 'Full Dry Run' if dry_run else 'Live Run'}")
        console.print(f"  Batch: {batch_size} file(s)")
        console.print(
            f"  Parallel: {'On' if parallel_processing_enabled else 'Off'}"
            + (f" ({parallel_workers} worker(s))" if parallel_processing_enabled else "")
        )

        return True

    def _process_files_with_dashboard(self, processor, vault_path: Path, live):
        """Process files with live dashboard updates"""
        import time

        # Wrap call_ollama to track AI requests
        original_call_ollama = processor.call_ollama

        def wrapped_call_ollama(prompt, system_prompt="", max_retries=None):
            """Wrapped version that tracks AI requests"""
            start_time = time.time()
            try:
                result = original_call_ollama(prompt, system_prompt, max_retries)
                elapsed = time.time() - start_time

                # Track successful request
                success = result != ""
                dashboard.add_ai_request(elapsed, success, tokens=len(result.split()) if result else 0)

                return result
            except Exception as e:
                elapsed = time.time() - start_time
                dashboard.add_ai_request(elapsed, False, timeout=True)
                raise

        # Replace with wrapped version
        processor.call_ollama = wrapped_call_ollama

        # Wrap cache operations
        original_analyze = processor.analyze_with_balanced_ai

        def wrapped_analyze(content, existing_notes):
            """Wrapped version that tracks cache hits/misses"""
            content_hash = processor.get_content_hash(content)

            # Check if cached
            if content_hash in processor.ai_cache:
                dashboard.add_cache_hit()
            else:
                dashboard.add_cache_miss()

            return original_analyze(content, existing_notes)

        # Replace with wrapped version
        processor.analyze_with_balanced_ai = wrapped_analyze

        # Apply configuration to processor module
        processor.VAULT_PATH = str(vault_path)
        processor.DRY_RUN = self.config.get('dry_run', True)
        processor.FAST_DRY_RUN = self.config.get('fast_dry_run', False)
        processor.BATCH_SIZE = self.config.get('batch_size', 1)
        processor.FILE_ORDERING = self.config.get('file_ordering', 'recent')

        # Load progress and cache
        processor.load_progress()
        processor.load_cache()

        # Update cache stats in dashboard
        cache_size_mb = 0
        if hasattr(processor, 'ai_cache') and processor.ai_cache:
            import sys
            cache_size_mb = sys.getsizeof(str(processor.ai_cache)) / (1024 * 1024)
        dashboard.update_cache_stats(cache_size_mb, len(processor.ai_cache) if hasattr(processor, 'ai_cache') else 0)

        # Get all notes
        console.print("[cyan]Loading existing notes...[/cyan]")
        existing_notes = processor.get_all_notes(str(vault_path))
        console.print(f"[green]Found {len(existing_notes)} existing notes[/green]\n")

        # Find files to process
        all_files = []
        for root, dirs, files in os.walk(str(vault_path)):
            if processor.config.get('backup_folder', '_backups') in root:
                continue
            for file in files:
                if file.endswith('.md') and not file.startswith(('📍', 'MOC')):
                    file_path = os.path.join(root, file)
                    if processor.should_process_file(file_path):
                        all_files.append(file_path)

        # Filter out already processed files if resume is enabled
        if processor.RESUME_ENABLED:
            all_files = [f for f in all_files if f not in processor.progress_data['processed_files']]

        # Order files
        all_files = processor.order_files(all_files, processor.FILE_ORDERING)

        # Update dashboard with total
        dashboard.update_processing(
            total_files=len(all_files),
            processed_files=0,
            failed_files=0,
            current_file='Ready to start',
            current_stage='Initialized'
        )
        live.update(dashboard.render())

        console.print(f"[cyan]Processing {len(all_files)} files...[/cyan]\n")

        # Statistics
        stats = {
            'processed': 0,
            'already_processed': 0,
            'failed': 0,
            'would_process': 0,
            'links_added': 0,
            'tags_added': 0
        }

        # Process files one by one
        start_time = time.time()
        for i, file_path in enumerate(all_files, 1):
            if not self.running:
                break

            filename = os.path.basename(file_path)
            file_size_kb = os.path.getsize(file_path) / 1024

            # Update dashboard
            dashboard.update_processing(
                current_file=filename,
                current_stage='Analyzing',
                processed_files=stats['processed']
            )
            dashboard.add_activity(f"Processing {filename}", success=True)
            live.update(dashboard.render())

            # Process the file
            file_start = time.time()
            try:
                result = processor.process_conversation(file_path, existing_notes, stats)
                file_time = time.time() - file_start

                # Update dashboard with timing
                dashboard.add_file_processing_time(int(file_size_kb), file_time)

                # Try to extract MOC category from analytics if available
                if hasattr(processor, 'analytics') and processor.analytics.get('moc_distribution'):
                    # Get the most recent MOC (last one added)
                    moc_dist = processor.analytics['moc_distribution']
                    if moc_dist:
                        # Find which MOC this file likely belongs to
                        # This is a simple heuristic - in reality the file determines its own MOC
                        for moc in moc_dist.keys():
                            dashboard.add_moc_category(moc)
                            break

                if result:
                    dashboard.add_activity(f"✓ Processed {filename} ({file_time:.1f}s)", success=True)
                else:
                    dashboard.add_activity(f"⏭ Skipped {filename}", success=True)

            except Exception as e:
                file_time = time.time() - file_start
                stats['failed'] += 1
                dashboard.add_error("processing_error", str(e))
                dashboard.add_activity(f"✗ Failed {filename}: {str(e)[:50]}", success=False)
                logger.error(f"Error processing {filename}: {e}")

            # Update final stats
            dashboard.update_processing(
                processed_files=stats['processed'],
                failed_files=stats['failed']
            )
            live.update(dashboard.render())

            # Save progress periodically
            if i % 5 == 0:
                processor.save_progress()
                processor.save_cache()

        # Final update
        elapsed = time.time() - start_time
        dashboard.update_processing(
            current_file='Complete',
            current_stage='Finished'
        )
        live.update(dashboard.render())

        console.print(f"\n[bold green]✓ Processing Complete[/bold green]")
        console.print(f"[green]Processed: {stats['processed']} | Failed: {stats['failed']} | Time: {elapsed:.1f}s[/green]\n")

        # Save final progress
        processor.save_progress()
        processor.save_cache()

    def run_with_dashboard(self):
        """Run processing with live dashboard"""
        logger.info("Starting Obsidian Auto-Linker with Live Dashboard")

        # Import the enhanced processor
        try:
            import obsidian_auto_linker_enhanced as processor
        except ImportError as e:
            logger.error(f"Failed to import processor: {e}")
            return

        # Run processor with dashboard enabled
        try:
            console.print("\n[bold green]✅ Starting processing with live dashboard...[/bold green]\n")
            processor.main(enable_dashboard=True, dashboard_update_interval=self.update_interval)
            with Live(dashboard.render(), refresh_per_second=1.0/self.update_interval, screen=True) as live:
                logger.info(f"Processing {total_files} files from {vault_path}")

                # Integrate with actual processing engine
                self._process_files_with_dashboard(processor, vault_path, live)

        except KeyboardInterrupt:
            self.signal_handler(None, None)
        except Exception as e:
            logger.error(f"Error during processing: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.running = False

    def main(self):
        """Main entry point"""
        console.print("\n[bold cyan]" + "=" * 70)
        console.print("[bold white]OBSIDIAN AUTO-LINKER - ENHANCED WITH LIVE DASHBOARD")
        console.print("[bold cyan]" + "=" * 70 + "\n")

        # Check Ollama
        if not self.check_ollama():
            console.print("[bold red]❌ Cannot proceed without Ollama[/bold red]")
            return

        # Check if config exists
        if not Path('config.yaml').exists():
            console.print("[yellow]No configuration found. Starting setup...[/yellow]\n")
            if not self.interactive_setup():
                return
        else:
            if not self.load_config():
                console.print("[yellow]Configuration invalid. Starting setup...[/yellow]\n")
                if not self.interactive_setup():
                    return

        # Confirm before starting
        console.print("\n[bold]Ready to start processing[/bold]")

        if self.config.get('dry_run'):
            if self.config.get('fast_dry_run'):
                console.print("[green]Mode: Fast Dry Run (no AI, no file changes)[/green]")
            else:
                console.print("[green]Mode: Full Dry Run (with AI, no file changes)[/green]")
        else:
            console.print("[yellow]⚠️  Mode: Live Run (will create _linked.md files)[/yellow]")

        parallel_status = self.config.get('parallel_processing_enabled', False)
        workers = self.config.get('parallel_workers', 1)
        console.print(
            f"Parallel processing: {'On' if parallel_status else 'Off'}"
            + (f" ({workers} worker(s) requested)" if parallel_status else "")
        )
        console.print(
            f"Enhanced dashboard: On (updates every {self.update_interval} seconds)"
        )

        try:
            confirm = input("\nContinue? (y/N): ").strip().lower()
        except EOFError:
            confirm = "y"

        if confirm not in ['y', 'yes']:
            console.print("[yellow]Cancelled by user[/yellow]")
            return

        # Run with dashboard
        console.print("\n[bold green]Starting live dashboard...[/bold green]")
        console.print(f"[dim]Dashboard updates every {self.update_interval} seconds[/dim]")
        console.print("[dim]Press Ctrl+C to stop at any time[/dim]\n")

        time.sleep(2)  # Give user time to read

        self.run_with_dashboard()


if __name__ == "__main__":
    try:
        runner = EnhancedRunner(update_interval=15)
        runner.main()
    except Exception as e:
        console.print(f"\n[bold red]Fatal error: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
