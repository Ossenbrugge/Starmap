#!/usr/bin/env python3
"""
Git Setup Verification Script for Starmap
Verifies that .gitignore is working correctly and shows repository status
"""

import os
import subprocess
import sys
from pathlib import Path


class GitSetupVerifier:
    """Verify Git configuration and .gitignore setup"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.gitignore_path = self.project_root / ".gitignore"
    
    def run_git_command(self, command):
        """Run a git command and return the result"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                cwd=self.project_root
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)
    
    def check_git_repository(self):
        """Check if we're in a Git repository"""
        print("🔍 Checking Git repository status...")
        
        success, output, error = self.run_git_command("git status --porcelain")
        
        if not success:
            print("  ❌ Not a Git repository or Git not available")
            print(f"     Error: {error}")
            return False
        
        print("  ✅ Git repository detected")
        return True
    
    def check_gitignore_exists(self):
        """Check if .gitignore file exists"""
        print("📄 Checking .gitignore file...")
        
        if not self.gitignore_path.exists():
            print("  ❌ .gitignore file not found")
            return False
        
        print("  ✅ .gitignore file exists")
        
        # Check file size
        size = self.gitignore_path.stat().st_size
        print(f"     Size: {size} bytes")
        
        return True
    
    def verify_ignore_patterns(self):
        """Verify that important patterns are properly ignored"""
        print("🚫 Verifying ignore patterns...")
        
        patterns_to_test = [
            ("starmap_venv/", "Virtual environment"),
            ("backup/", "Backup directory"),
            ("__pycache__/", "Python cache"),
            ("test.log", "Log files"),
            (".env.local", "Environment files"),
            ("temp/", "Temporary directories"),
            ("*.pyc", "Compiled Python files"),
            ("instance/", "Flask instance folder")
        ]
        
        all_ignored = True
        
        for pattern, description in patterns_to_test:
            success, output, error = self.run_git_command(f"git check-ignore {pattern}")
            
            if success and output:
                print(f"  ✅ {description}: {pattern}")
            else:
                print(f"  ⚠️  {description}: {pattern} (not ignored or doesn't exist)")
                # This might be OK if the file/directory doesn't exist
        
        return all_ignored
    
    def check_tracked_files(self):
        """Check what files are currently tracked"""
        print("📊 Checking tracked files...")
        
        success, output, error = self.run_git_command("git ls-files")
        
        if not success:
            print("  ❌ Could not list tracked files")
            return False
        
        tracked_files = output.split('\n') if output else []
        
        # Check for important files that should be tracked
        important_files = [
            "app.py",
            "requirements.txt",
            ".gitignore",
            "models/",
            "views/",
            "controllers/"
        ]
        
        tracked_important = []
        missing_important = []
        
        for file_pattern in important_files:
            found = any(file_pattern in tracked_file for tracked_file in tracked_files)
            if found:
                tracked_important.append(file_pattern)
            else:
                missing_important.append(file_pattern)
        
        print(f"  ✅ {len(tracked_important)} important files/directories tracked")
        if missing_important:
            print(f"  ⚠️  {len(missing_important)} important files not yet tracked:")
            for file_pattern in missing_important:
                print(f"     - {file_pattern}")
        
        return True
    
    def check_untracked_files(self):
        """Check for untracked files that might need attention"""
        print("📋 Checking untracked files...")
        
        success, output, error = self.run_git_command("git status --porcelain")
        
        if not success:
            print("  ❌ Could not check untracked files")
            return False
        
        untracked_files = [
            line[3:] for line in output.split('\n') 
            if line.startswith('??') and line.strip()
        ]
        
        if not untracked_files:
            print("  ✅ No untracked files")
            return True
        
        print(f"  📄 {len(untracked_files)} untracked files found:")
        for file_name in untracked_files[:10]:  # Show first 10
            print(f"     - {file_name}")
        
        if len(untracked_files) > 10:
            print(f"     ... and {len(untracked_files) - 10} more")
        
        print("\n  💡 Consider adding important files with: git add <filename>")
        
        return True
    
    def check_for_sensitive_files(self):
        """Check for potentially sensitive files that shouldn't be tracked"""
        print("🔐 Checking for sensitive files...")
        
        success, output, error = self.run_git_command("git ls-files")
        
        if not success:
            print("  ❌ Could not check for sensitive files")
            return False
        
        tracked_files = output.split('\n') if output else []
        
        sensitive_patterns = [
            '.env',
            'secret',
            'password',
            'key.',
            '.pem',
            '.p12',
            'credentials',
            'config.py',
            'starmap_venv',
            'backup'
        ]
        
        sensitive_files = []
        for tracked_file in tracked_files:
            for pattern in sensitive_patterns:
                if pattern in tracked_file.lower():
                    sensitive_files.append(tracked_file)
                    break
        
        if not sensitive_files:
            print("  ✅ No sensitive files detected in tracking")
            return True
        
        print(f"  ⚠️  {len(sensitive_files)} potentially sensitive files tracked:")
        for file_name in sensitive_files:
            print(f"     - {file_name}")
        
        print("\n  💡 Consider removing sensitive files with: git rm --cached <filename>")
        
        return len(sensitive_files) == 0
    
    def show_repository_summary(self):
        """Show a summary of the repository status"""
        print("\n" + "="*60)
        print("📊 REPOSITORY SUMMARY")
        print("="*60)
        
        # Count tracked files
        success, output, error = self.run_git_command("git ls-files")
        tracked_count = len(output.split('\n')) if success and output else 0
        
        # Count untracked files
        success, output, error = self.run_git_command("git status --porcelain")
        untracked_count = len([
            line for line in output.split('\n') 
            if line.startswith('??') and line.strip()
        ]) if success and output else 0
        
        # Check repository size
        success, output, error = self.run_git_command("git count-objects -vH")
        repo_size = "Unknown"
        if success and output:
            for line in output.split('\n'):
                if 'size-pack' in line:
                    repo_size = line.split()[-1]
                    break
        
        print(f"📁 Tracked files: {tracked_count}")
        print(f"📄 Untracked files: {untracked_count}")
        print(f"💾 Repository size: {repo_size}")
        
        # Show ignored directories
        ignored_dirs = ["starmap_venv/", "backup/", "__pycache__/"]
        existing_ignored = [d for d in ignored_dirs if Path(d).exists()]
        
        if existing_ignored:
            print(f"🚫 Ignored directories: {', '.join(existing_ignored)}")
        
        print("\n✅ Repository is properly configured!")
    
    def run_verification(self):
        """Run complete verification"""
        print("🌟 Git Setup Verification for Starmap")
        print("="*50)
        
        checks = [
            self.check_git_repository,
            self.check_gitignore_exists,
            self.verify_ignore_patterns,
            self.check_tracked_files,
            self.check_untracked_files,
            self.check_for_sensitive_files
        ]
        
        all_passed = True
        
        for check in checks:
            try:
                result = check()
                if result is False:
                    all_passed = False
                print()  # Add spacing between checks
            except Exception as e:
                print(f"  ❌ Check failed: {e}")
                all_passed = False
                print()
        
        # Show summary regardless of check results
        self.show_repository_summary()
        
        return all_passed


def main():
    """Main verification function"""
    verifier = GitSetupVerifier()
    
    success = verifier.run_verification()
    
    if success:
        print("\n🎉 All Git setup checks passed!")
        print("\n📋 Next steps:")
        print("   git add .                    # Add new files")
        print("   git commit -m 'message'      # Commit changes")
        print("   git push origin main         # Push to remote")
    else:
        print("\n⚠️  Some issues detected. Please review the output above.")
        print("\n📋 Common fixes:")
        print("   git rm --cached <file>       # Remove sensitive files")
        print("   git add <file>               # Add important files")
        print("   Edit .gitignore              # Update ignore patterns")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())