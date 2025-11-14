#!/usr/bin/env python3
"""
Interactive Obsidian Auto-Linker Runner
Provides easy configuration and process control
"""

import os
import sys
import signal
import subprocess
import time
import json
import psutil
import threading
from pathlib import Path
from datetime import datetime

class ObsidianAutoLinker:
    def __init__(self):
        self.process = None
        self.running = False
        self.monitoring = False
        self.enable_dashboard = False
        self.resource_stats = {
            'start_time': None,
            'peak_cpu': 0,
            'peak_memory': 0,
            'avg_cpu': 0,
            'avg_memory': 0,
            'cpu_samples': [],
            'memory_samples': [],
            'last_activity': None,
            'current_stage': 'Initializing',
            'files_processed': 0,
            'files_scanned': 0
        }
        self.monitor_thread = None
        
    def signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n🛑 Stopping process...")
        
        # Stop monitoring
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        
        # Show resource usage summary
        self.show_resource_summary()
        
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.running = False
        print("✅ Process stopped safely")
        sys.exit(0)
    
    def get_vault_path(self):
        """Get vault path from user"""
        default_path = "/Users/medici/Documents/MediciVault"
        
        print("📁 Obsidian Vault Path:")
        print(f"   Default: {default_path}")
        
        try:
            vault_path = input("   Enter path (or press Enter for default): ").strip()
        except EOFError:
            # Non-interactive mode, use default
            vault_path = default_path
            print(f"   Using default: {vault_path}")
        
        if not vault_path:
            vault_path = default_path
            
        if not os.path.exists(vault_path):
            print(f"❌ Path does not exist: {vault_path}")
            return None
            
        return vault_path
    
    def start_resource_monitoring(self):
        """Start monitoring system resources"""
        self.monitoring = True
        self.resource_stats['start_time'] = datetime.now()
        self.monitor_thread = threading.Thread(target=self.monitor_resources, daemon=True)
        self.monitor_thread.start()
        print("📊 Resource monitoring started")
    
    def monitor_resources(self):
        """Monitor CPU and memory usage"""
        while self.monitoring:
            try:
                # Get system-wide CPU and memory usage
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                
                # Update stats
                self.resource_stats['cpu_samples'].append(cpu_percent)
                self.resource_stats['memory_samples'].append(memory_percent)
                
                # Keep only last 60 samples (1 minute of data)
                if len(self.resource_stats['cpu_samples']) > 60:
                    self.resource_stats['cpu_samples'] = self.resource_stats['cpu_samples'][-60:]
                    self.resource_stats['memory_samples'] = self.resource_stats['memory_samples'][-60:]
                
                # Update peaks
                if cpu_percent > self.resource_stats['peak_cpu']:
                    self.resource_stats['peak_cpu'] = cpu_percent
                if memory_percent > self.resource_stats['peak_memory']:
                    self.resource_stats['peak_memory'] = memory_percent
                
                # Update averages
                if self.resource_stats['cpu_samples']:
                    self.resource_stats['avg_cpu'] = sum(self.resource_stats['cpu_samples']) / len(self.resource_stats['cpu_samples'])
                    self.resource_stats['avg_memory'] = sum(self.resource_stats['memory_samples']) / len(self.resource_stats['memory_samples'])
                
                time.sleep(1)
            except Exception as e:
                print(f"⚠️  Resource monitoring error: {e}")
                break
    
    def update_activity(self, stage, activity=""):
        """Update what the process is currently doing"""
        self.resource_stats['current_stage'] = stage
        self.resource_stats['last_activity'] = f"{stage}: {activity}" if activity else stage
        self.resource_stats['last_activity_time'] = datetime.now().strftime("%H:%M:%S")
    
    def show_resource_summary(self):
        """Show resource usage summary when stopping"""
        if not self.resource_stats['start_time']:
            return
            
        duration = datetime.now() - self.resource_stats['start_time']
        
        print("\n" + "="*60)
        print("📊 RESOURCE USAGE SUMMARY")
        print("="*60)
        print(f"⏱️  Total Runtime: {duration}")
        print(f"📁 Files Scanned: {self.resource_stats['files_scanned']}")
        print(f"✅ Files Processed: {self.resource_stats['files_processed']}")
        print(f"🖥️  Peak CPU Usage: {self.resource_stats['peak_cpu']:.1f}%")
        print(f"🧠 Peak Memory Usage: {self.resource_stats['peak_memory']:.1f}%")
        print(f"📈 Average CPU Usage: {self.resource_stats['avg_cpu']:.1f}%")
        print(f"📈 Average Memory Usage: {self.resource_stats['avg_memory']:.1f}%")
        print(f"🔄 Last Activity: {self.resource_stats['last_activity']}")
        print(f"⏰ Last Activity Time: {self.resource_stats.get('last_activity_time', 'Unknown')}")

        # Show recent CPU/Memory trend
        if len(self.resource_stats['cpu_samples']) >= 10:
            recent_cpu = self.resource_stats['cpu_samples'][-10:]
            recent_memory = self.resource_stats['memory_samples'][-10:]
            print(f"📊 Recent CPU Trend: {recent_cpu[-1]:.1f}% (last 10s avg: {sum(recent_cpu)/len(recent_cpu):.1f}%)")
            print(f"📊 Recent Memory Trend: {recent_memory[-1]:.1f}% (last 10s avg: {sum(recent_memory)/len(recent_memory):.1f}%)")

        print("="*60)
    
    def get_file_ordering(self):
        """Get file ordering preference"""
        print("\n📋 File Processing Order:")
        print("   1. Recent (newest first) - Recommended")
        print("   2. Size (largest first)")
        print("   3. Random")
        print("   4. Alphabetical")
        
        while True:
            try:
                choice = input("   Choose (1-4, default=1): ").strip()
            except EOFError:
                # Non-interactive mode, use default
                choice = "1"
                print("   Using default: 1")
            
            if not choice:
                return "recent"
            elif choice == "1":
                return "recent"
            elif choice == "2":
                return "size"
            elif choice == "3":
                return "random"
            elif choice == "4":
                return "alphabetical"
            else:
                print("   ❌ Invalid choice. Please enter 1-4")
    
    def get_processing_mode(self):
        """Get processing mode"""
        print("\n🔧 Processing Mode:")
        print("   1. Fast Dry Run (quick test - no AI analysis)")
        print("   2. Full Dry Run (complete test with AI analysis)")
        print("   3. Live Run (process files for real)")
        
        while True:
            try:
                choice = input("   Choose (1-3, default=1): ").strip()
            except EOFError:
                # Non-interactive mode, use default
                choice = "1"
                print("   Using default: 1")
            
            if not choice:
                return "fast_dry"
            elif choice == "1":
                return "fast_dry"
            elif choice == "2":
                return "dry"
            elif choice == "3":
                return "live"
            else:
                print("   ❌ Invalid choice. Please enter 1-3")
    
    def get_batch_size(self):
        """Get batch size"""
        print("\n📦 Processing Batch Size:")
        print("   1. One file at a time (recommended)")
        print("   2. Small batch (5 files)")
        print("   3. Medium batch (10 files)")
        
        while True:
            try:
                choice = input("   Choose (1-3, default=1): ").strip()
            except EOFError:
                # Non-interactive mode, use default
                choice = "1"
                print("   Using default: 1")
            
            if not choice:
                return 1
            elif choice == "1":
                return 1
            elif choice == "2":
                return 5
            elif choice == "3":
                return 10
            else:
                print("   ❌ Invalid choice. Please enter 1-3")

    def get_dashboard_preference(self):
        """Ask if user wants to enable the live dashboard"""
        print("\n📊 Live Dashboard:")
        print("   1. Enable dashboard (real-time metrics and monitoring)")
        print("   2. Disable dashboard (simple text output)")

        while True:
            try:
                choice = input("   Choose (1-2, default=1): ").strip()
            except EOFError:
                # Non-interactive mode, use default
                choice = "1"
                print("   Using default: 1")

            if not choice:
                return True
            elif choice == "1":
                return True
            elif choice == "2":
                return False
            else:
                print("   ❌ Invalid choice. Please enter 1-2")

    def update_config(self, vault_path, file_ordering, processing_mode, batch_size):
        """Update config.yaml with user choices"""
        # Convert processing mode to config values
        if processing_mode == "fast_dry":
            dry_run = True
            fast_dry_run = True
        elif processing_mode == "dry":
            dry_run = True
            fast_dry_run = False
        else:  # live
            dry_run = False
            fast_dry_run = False
            
        config_content = f"""batch_size: {batch_size}
custom_model_name: ''
dry_run: {dry_run}
fast_dry_run: {fast_dry_run}
file_ordering: '{file_ordering}'
ollama_base_url: http://localhost:11434
ollama_model: goekdenizguelmez/JOSIEFIED-Qwen3:latest
vault_path: {vault_path}
"""
        
        with open('config.yaml', 'w') as f:
            f.write(config_content)
        
        print(f"✅ Configuration updated")
    
    def check_ollama(self):
        """Check if Ollama is running"""
        try:
            import requests
            response = requests.get('http://localhost:11434/api/tags', timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    print(f"✅ Ollama running with {len(models)} models")
                    return True
                else:
                    print("❌ Ollama running but no models loaded")
                    return False
            else:
                print("❌ Ollama not responding")
                return False
        except (requests.exceptions.RequestException, ConnectionError) as e:
            print(f"❌ Ollama not running: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error checking Ollama: {e}")
            return False
    
    def run_processing(self):
        """Run the processing script"""
        print("\n🚀 Starting Obsidian Auto-Linker...")
        print("   Press Ctrl+C to stop at any time")
        print("   " + "="*50)

        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)

        # If dashboard is enabled, run in-process
        if self.enable_dashboard:
            try:
                import obsidian_auto_linker_enhanced as processor
                self.running = True
                self.update_activity("Starting", "Launching with dashboard")

                print("\n✅ Starting processing with live dashboard...\n")
                processor.main(enable_dashboard=True, dashboard_update_interval=15)

                self.update_activity("Completed", "Processing finished")

            except KeyboardInterrupt:
                print("\n🛑 Interrupted by user")
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
                self.update_activity("Error", f"Exception: {str(e)}")
            finally:
                self.running = False
                self.monitoring = False
            return

        # Otherwise, use subprocess mode (no dashboard)
        self.start_resource_monitoring()

        try:
            self.running = True
            self.update_activity("Starting", "Launching processing script")

            self.process = subprocess.Popen([
                sys.executable, 'obsidian_auto_linker_enhanced.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            universal_newlines=True, bufsize=1)

            # Stream output in real-time and track activity
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    line_clean = line.rstrip()
                    print(line_clean)

                    # Update activity based on output patterns
                    if "Processing file" in line_clean:
                        self.update_activity("Processing", "Analyzing file content")
                        self.resource_stats['files_processed'] += 1
                    elif "AI Analysis" in line_clean:
                        self.update_activity("AI Analysis", "Local LLM processing")
                    elif "Creating links" in line_clean:
                        self.update_activity("Linking", "Creating wiki links")
                    elif "Saving file" in line_clean:
                        self.update_activity("Saving", "Writing processed file")
                    elif "Progress:" in line_clean:
                        self.update_activity("Progress", "Updating progress")
                    elif "Testing Ollama" in line_clean:
                        self.update_activity("Testing", "Connecting to Ollama")
                    elif "Found" in line_clean and "markdown files to process" in line_clean:
                        self.update_activity("Scanning", "Discovering files")
                        # Extract file count from line like "Found 25 markdown files to process"
                        import re
                        match = re.search(r'Found (\d+) markdown files', line_clean)
                        if match:
                            self.resource_stats['files_scanned'] = int(match.group(1))

            self.process.wait()
            self.update_activity("Completed", "Processing finished")

        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
            if self.process:
                self.process.terminate()
        except Exception as e:
            print(f"❌ Error: {e}")
            self.update_activity("Error", f"Exception: {str(e)}")
        finally:
            self.running = False
            self.monitoring = False
    
    def show_previous_results(self):
        """Show results from the previous run"""
        try:
            # Check for progress file
            progress_file = '.processing_progress.json'
            if os.path.exists(progress_file):
                with open(progress_file, 'r') as f:
                    data = json.load(f)
                    if data and isinstance(data, dict):
                        processed = len(data.get('processed_files', []))
                        failed = len(data.get('failed_files', []))
                        last_update = data.get('last_update', 'Unknown')
                        
                        print("\n📊 PREVIOUS RUN RESULTS")
                        print("="*40)
                        print(f"✅ Files Processed: {processed}")
                        print(f"❌ Files Failed: {failed}")
                        print(f"📅 Last Update: {last_update}")
                        if processed > 0:
                            print(f"📈 Success Rate: {(processed/(processed+failed)*100):.1f}%")
                        print("="*40)
                        return True
        except Exception as e:
            print(f"⚠️  Could not load previous results: {e}")
        return False
    
    def main(self):
        """Main interactive interface"""
        print("="*60)
        print("🚀 OBSIDIAN AUTO-LINKER")
        print("   Interactive Configuration & Control")
        print("="*60)
        
        # Show previous results if available
        self.show_previous_results()
        
        # Check Ollama first
        if not self.check_ollama():
            print("\n❌ Ollama is not running or not accessible")
            print("   Please start Ollama first:")
            print("   ollama serve")
            return
        
        # Get user preferences
        vault_path = self.get_vault_path()
        if not vault_path:
            return

        file_ordering = self.get_file_ordering()
        processing_mode = self.get_processing_mode()
        batch_size = self.get_batch_size()
        enable_dashboard = self.get_dashboard_preference()

        # Store dashboard preference
        self.enable_dashboard = enable_dashboard

        # Show summary
        mode_descriptions = {
            "fast_dry": "Fast Dry Run (quick test - no AI analysis)",
            "dry": "Full Dry Run (complete test with AI analysis)",
            "live": "Live Run (will create new files)"
        }

        print("\n📋 Configuration Summary:")
        print(f"   📁 Vault: {vault_path}")
        print(f"   📋 Order: {file_ordering}")
        print(f"   🔧 Mode: {mode_descriptions[processing_mode]}")
        print(f"   📦 Batch: {batch_size} file(s) at a time")
        print(f"   📊 Dashboard: {'Enabled' if enable_dashboard else 'Disabled'}")
        
        # Confirm before running
        print("\n⚠️  Ready to start processing")
        if processing_mode == "live":
            print("   ⚠️  LIVE MODE: This will create new files with '_linked' suffix")
        elif processing_mode == "fast_dry":
            print("   ⚡ FAST DRY RUN: Quick test - no AI analysis, very fast")
        else:
            print("   ✅ FULL DRY RUN: Complete test with AI analysis")
            
        try:
            confirm = input("\n   Continue? (y/N): ").strip().lower()
        except EOFError:
            # Non-interactive mode, auto-confirm
            confirm = "y"
            print("   Auto-confirming (non-interactive mode)")
        
        if confirm not in ['y', 'yes']:
            print("❌ Cancelled by user")
            return
        
        # Update config and run
        self.update_config(vault_path, file_ordering, processing_mode, batch_size)
        self.run_processing()

if __name__ == "__main__":
    app = ObsidianAutoLinker()
    app.main()