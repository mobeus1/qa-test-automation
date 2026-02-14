#!/usr/bin/env python3
"""
Migrate monorepo QA configs to multi-repo architecture.

This script:
1. Reads all apps from configs/apps/
2. Creates a separate qa-config-{app-name} repo for each
3. Migrates configs and test suites to the new repos
4. Sets up proper CODEOWNERS and permissions
"""

import os
import json
import subprocess
import sys
import argparse
from pathlib import Path

class RepoMigrator:
    def __init__(self, org_name, template_repo, dry_run=False):
        self.org_name = org_name
        self.template_repo = template_repo
        self.dry_run = dry_run
        self.base_dir = Path(__file__).parent.parent
        self.apps_dir = self.base_dir / "configs" / "apps"
        self.test_suites_dir = self.base_dir / "test-suites"
        
    def log(self, message, level="INFO"):
        """Print colored log messages"""
        colors = {
            "INFO": "\033[94m",    # Blue
            "SUCCESS": "\033[92m", # Green
            "WARNING": "\033[93m", # Yellow
            "ERROR": "\033[91m",   # Red
            "RESET": "\033[0m"
        }
        print(f"{colors.get(level, '')}{level}: {message}{colors['RESET']}")
    
    def run_command(self, cmd, cwd=None, check=True):
        """Run shell command with error handling"""
        if self.dry_run:
            self.log(f"DRY RUN: {' '.join(cmd)}", "WARNING")
            return None
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {' '.join(cmd)}", "ERROR")
            self.log(f"Error: {e.stderr}", "ERROR")
            raise
    
    def get_app_list(self):
        """Get list of all applications in configs/apps/"""
        if not self.apps_dir.exists():
            self.log(f"Apps directory not found: {self.apps_dir}", "ERROR")
            return []
        
        apps = [d.name for d in self.apps_dir.iterdir() if d.is_dir()]
        self.log(f"Found {len(apps)} applications to migrate", "INFO")
        return apps
    
    def create_config_repo(self, app_name):
        """Create a new config repo from template"""
        repo_name = f"qa-config-{app_name}"
        
        self.log(f"Creating repository: {repo_name}", "INFO")
        
        # Check if repo already exists
        check_result = self.run_command(
            ["gh", "repo", "view", f"{self.org_name}/{repo_name}"],
            check=False
        )
        
        if check_result and check_result.returncode == 0:
            self.log(f"Repository {repo_name} already exists, skipping creation", "WARNING")
            return repo_name
        
        # Create from template
        cmd = [
            "gh", "repo", "create",
            f"{self.org_name}/{repo_name}",
            "--private",
            "--description", f"QA test configuration for {app_name}"
        ]
        
        if self.template_repo:
            cmd.extend(["--template", self.template_repo])
        
        self.run_command(cmd)
        self.log(f"Created repository: {repo_name}", "SUCCESS")
        
        return repo_name
    
    def merge_configs(self, app_name):
        """Merge testcomplete.json and jmeter.json into single config.json"""
        app_config_dir = self.apps_dir / app_name
        
        config = {
            "app_name": app_name,
            "version": "1.0",
            "testcomplete": {},
            "jmeter": {}
        }
        
        # Load TestComplete config
        tc_config_file = app_config_dir / "testcomplete.json"
        if tc_config_file.exists():
            with open(tc_config_file) as f:
                config["testcomplete"] = json.load(f)
        
        # Load JMeter config
        jm_config_file = app_config_dir / "jmeter.json"
        if jm_config_file.exists():
            with open(jm_config_file) as f:
                config["jmeter"] = json.load(f)
        
        return config
    
    def populate_repo(self, app_name, repo_name, temp_dir):
        """Clone repo, populate with configs and test suites, commit and push"""
        repo_path = temp_dir / repo_name
        app_config_dir = self.apps_dir / app_name
        app_test_suite_dir = self.test_suites_dir / app_name
        
        # Clone the repo
        self.log(f"Cloning {repo_name}...", "INFO")
        self.run_command(
            ["gh", "repo", "clone", f"{self.org_name}/{repo_name}", str(repo_path)]
        )
        
        # Create merged config.json
        config = self.merge_configs(app_name)
        config_file = repo_path / "config.json"
        
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        # Copy CODEOWNERS if exists
        codeowners_src = app_config_dir / "CODEOWNERS"
        if codeowners_src.exists():
            codeowners_dst = repo_path / "CODEOWNERS"
            self.run_command(["cp", str(codeowners_src), str(codeowners_dst)])
        
        # Copy test suites if they exist
        if app_test_suite_dir.exists():
            # TestComplete
            tc_src = app_test_suite_dir / "testcomplete"
            if tc_src.exists():
                tc_dst = repo_path / "testcomplete"
                self.run_command(["cp", "-r", str(tc_src), str(tc_dst)])
            
            # JMeter
            jm_src = app_test_suite_dir / "jmeter"
            if jm_src.exists():
                jm_dst = repo_path / "jmeter"
                self.run_command(["cp", "-r", str(jm_src), str(jm_dst)])
        
        # Create README
        readme_content = f"""# QA Test Configuration - {app_name}

This repository contains test configuration and test suites for **{app_name}**.

## Structure

- `config.json` - Combined TestComplete and JMeter configuration
- `testcomplete/` - TestComplete test project
- `jmeter/` - JMeter test plans
- `CODEOWNERS` - Team ownership

## Usage

This configuration is automatically loaded by the central QA orchestration system when tests are triggered for {app_name}.

## Updating Configuration

1. Edit `config.json`
2. Commit and push changes
3. Tests will use the new configuration on next run

## Related Repositories

- [qa-test-automation](https://github.com/{self.org_name}/qa-test-automation) - Central orchestrator
- [Application Repository] - Your application source code
"""
        
        with open(repo_path / "README.md", "w") as f:
            f.write(readme_content)
        
        # Git add, commit, push
        self.log(f"Committing changes to {repo_name}...", "INFO")
        self.run_command(["git", "add", "."], cwd=repo_path)
        self.run_command(
            ["git", "commit", "-m", f"Initial migration of {app_name} configuration"],
            cwd=repo_path
        )
        self.run_command(["git", "push"], cwd=repo_path)
        
        self.log(f"Successfully populated {repo_name}", "SUCCESS")
    
    def add_repo_topics(self, repo_name):
        """Add GitHub topics for organization"""
        topics = ["qa-automation", "qa-config", "test-configuration"]
        
        self.log(f"Adding topics to {repo_name}...", "INFO")
        self.run_command([
            "gh", "repo", "edit",
            f"{self.org_name}/{repo_name}",
            "--add-topic", ",".join(topics)
        ])
    
    def migrate_app(self, app_name, temp_dir):
        """Migrate a single application to its own repo"""
        self.log(f"\n{'='*60}", "INFO")
        self.log(f"Migrating application: {app_name}", "INFO")
        self.log(f"{'='*60}", "INFO")
        
        try:
            # Create repo
            repo_name = self.create_config_repo(app_name)
            
            # Populate with content
            self.populate_repo(app_name, repo_name, temp_dir)
            
            # Add topics
            self.add_repo_topics(repo_name)
            
            self.log(f"✓ Migration completed for {app_name}", "SUCCESS")
            return True
            
        except Exception as e:
            self.log(f"✗ Migration failed for {app_name}: {str(e)}", "ERROR")
            return False
    
    def migrate_all(self, apps=None, temp_dir=None):
        """Migrate all or selected applications"""
        if temp_dir is None:
            temp_dir = Path("/tmp/qa-migration")
        
        temp_dir.mkdir(exist_ok=True)
        
        if apps is None:
            apps = self.get_app_list()
        
        if not apps:
            self.log("No applications found to migrate", "WARNING")
            return
        
        self.log(f"Starting migration of {len(apps)} applications", "INFO")
        
        success_count = 0
        failed_apps = []
        
        for app_name in apps:
            if self.migrate_app(app_name, temp_dir):
                success_count += 1
            else:
                failed_apps.append(app_name)
        
        # Summary
        self.log(f"\n{'='*60}", "INFO")
        self.log(f"Migration Summary", "INFO")
        self.log(f"{'='*60}", "INFO")
        self.log(f"Total apps: {len(apps)}", "INFO")
        self.log(f"Successful: {success_count}", "SUCCESS")
        self.log(f"Failed: {len(failed_apps)}", "ERROR" if failed_apps else "INFO")
        
        if failed_apps:
            self.log(f"Failed apps: {', '.join(failed_apps)}", "ERROR")
        
        # Cleanup
        if not self.dry_run:
            self.log(f"\nCleaning up temporary directory: {temp_dir}", "INFO")
            self.run_command(["rm", "-rf", str(temp_dir)])

def main():
    parser = argparse.ArgumentParser(description="Migrate QA configs to multi-repo architecture")
    parser.add_argument(
        "--org",
        required=True,
        help="GitHub organization name (e.g., your-org)"
    )
    parser.add_argument(
        "--template",
        help="Template repository for new repos (e.g., your-org/qa-config-template)"
    )
    parser.add_argument(
        "--apps",
        nargs="+",
        help="Specific apps to migrate (default: all)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    parser.add_argument(
        "--temp-dir",
        type=Path,
        default=Path("/tmp/qa-migration"),
        help="Temporary directory for cloning repos"
    )
    
    args = parser.parse_args()
    
    # Verify gh CLI is installed
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: GitHub CLI (gh) is not installed or not in PATH")
        print("Install from: https://cli.github.com/")
        sys.exit(1)
    
    # Run migration
    migrator = RepoMigrator(
        org_name=args.org,
        template_repo=args.template,
        dry_run=args.dry_run
    )
    
    migrator.migrate_all(apps=args.apps, temp_dir=args.temp_dir)

if __name__ == "__main__":
    main()
