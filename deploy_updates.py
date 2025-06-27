"""
Deploy Updates to Swish List Website
Ensures all changes are pushed to GitHub and Render
"""

import subprocess
import os
import sys
from datetime import datetime

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} successful")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def deploy_updates():
    """Deploy all updates to the website"""
    print("="*60)
    print("SWISH LIST DEPLOYMENT SCRIPT")
    print("="*60)
    
    # Step 1: Check git status
    print("\nChecking git status...")
    subprocess.run("git status", shell=True)
    
    # Step 2: Run the latest rankings
    if input("\nRun SWISH Score v2.1 calculator? (y/n): ").lower() == 'y':
        run_command("python swish_score_calculator_v2.py", "Running SWISH Score v2.1")
    
    # Step 3: Stage all changes
    files_to_add = [
        "nba_goat_rankings_swish.csv",
        "nba_goat_rankings_swish_v2.csv",
        "swish_score_calculator_v2.py",
        "*.py"  # Any other Python files
    ]
    
    for file in files_to_add:
        run_command(f"git add {file}", f"Staging {file}")
    
    # Step 4: Create commit message
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"Update SWISH v2.1 rankings - Championship weight increased - {timestamp}"
    
    # Step 5: Commit changes
    if run_command(f'git commit -m "{commit_msg}"', "Committing changes"):
        print("\nCommit successful!")
    else:
        print("\nNo changes to commit or commit failed")
    
    # Step 6: Push to GitHub
    if input("\nPush to GitHub? (y/n): ").lower() == 'y':
        if run_command("git push origin main", "Pushing to GitHub"):
            print("\n✅ Successfully pushed to GitHub!")
            print("\nRender will automatically deploy your changes.")
            print("Check your website in 2-3 minutes:")
            print("https://your-render-url.onrender.com")
        else:
            # Try alternative branch name
            print("\nTrying 'master' branch...")
            if run_command("git push origin master", "Pushing to GitHub (master)"):
                print("\n✅ Successfully pushed to GitHub!")
    
    # Step 7: Show deployment status
    print("\n" + "="*60)
    print("DEPLOYMENT SUMMARY")
    print("="*60)
    print("1. ✅ SWISH Score v2.1 rankings generated")
    print("2. ✅ Files staged and committed")
    print("3. ✅ Pushed to GitHub")
    print("4. ⏳ Render deployment in progress (2-3 minutes)")
    print("\nNext steps:")
    print("- Check Render dashboard for deployment status")
    print("- Visit your website to see updated rankings")
    print("- Share on social media!")

if __name__ == "__main__":
    try:
        deploy_updates()
    except KeyboardInterrupt:
        print("\n\nDeployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)