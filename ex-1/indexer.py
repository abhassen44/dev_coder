import os
import sys
import json
import base64
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load .env file
load_dotenv()


# --- ⚙️ CONFIGURATION ---
CONFIG = {
    'OWNER': 'abhassen44',                     # The owner of the repository
    'REPO': 'gen-qi',                     # The name of the repository
    # Add the file extensions you want to index. (e.g., '.js', '.py', '.go')
    'FILE_EXTENSIONS_TO_INDEX': ['.py', '.md', '.txt'],
    # For the prototype, we'll limit the number of files to avoid long runs
    'MAX_FILES_TO_INDEX': 20,
    'OUTPUT_FILE': 'indexed_repo.json'
}
# --- END CONFIGURATION ---

# Retrieve the token from environment variables
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
API_URL = 'https://api.github.com'

# Set up headers for all API requests
HEADERS = {
    'Authorization': f'Bearer {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
    'X-GitHub-Api-Version': '2022-11-28'
}

def main():
    """Main function to orchestrate the indexing."""
    print("Starting GitHub repository indexing...")

    if not GITHUB_TOKEN:
        print("❌ ERROR: GITHUB_TOKEN is not set. Please set it as an environment variable.")
        sys.exit(1)

    try:
        # 1. Get the SHA of the latest commit on the default branch
        print(f"[1/5] Fetching default branch info for {CONFIG['OWNER']}/{CONFIG['REPO']}...")
        repo_info_res = requests.get(f"{API_URL}/repos/{CONFIG['OWNER']}/{CONFIG['REPO']}", headers=HEADERS)
        repo_info_res.raise_for_status()
        repo_info = repo_info_res.json()
        default_branch = repo_info['default_branch']

        branch_info_res = requests.get(f"{API_URL}/repos/{CONFIG['OWNER']}/{CONFIG['REPO']}/branches/{default_branch}", headers=HEADERS)
        branch_info_res.raise_for_status()
        latest_commit_sha = branch_info_res.json()['commit']['sha']
        print(f"✅ Default branch is '{default_branch}' at commit SHA: {latest_commit_sha}")

        # 2. Get the entire repository file tree
        print("[2/5] Fetching repository file tree...")
        tree_res = requests.get(f"{API_URL}/repos/{CONFIG['OWNER']}/{CONFIG['REPO']}/git/trees/{latest_commit_sha}?recursive=1", headers=HEADERS)
        tree_res.raise_for_status()
        all_files = tree_res.json()['tree']

        # 3. Filter for relevant files based on extension
        # Note: file['path'].endswith() takes a tuple of extensions
        extensions_tuple = tuple(CONFIG['FILE_EXTENSIONS_TO_INDEX'])
        files_to_index = []
        for file in all_files:
            if file['type'] == 'blob' and file['path'].endswith(extensions_tuple):
                files_to_index.append(file)
        files_to_index = files_to_index[:CONFIG['MAX_FILES_TO_INDEX']]

        print(f"✅ Found {len(files_to_index)} files to index.")
        # 4. Fetch the content for each file
        print("[3/5] Fetching content for each file...")
        indexed_files = []
        for file in files_to_index:
            blob_res = requests.get(file['url'], headers=HEADERS)
            blob_res.raise_for_status()
            blob_content_base64 = blob_res.json()['content']
            
            # Decode the base64 content
            try:
                decoded_content = base64.b64decode(blob_content_base64).decode('utf-8')
                indexed_files.append({'path': file['path'], 'content': decoded_content})
            except UnicodeDecodeError:
                print(f"  ⚠️  Could not decode file: {file['path']} (skipping)")

        print("✅ All file contents fetched.")

        # 5. Fetch recent commit history for context
        print("[4/5] Fetching commit history...")
        commits_res = requests.get(f"{API_URL}/repos/{CONFIG['OWNER']}/{CONFIG['REPO']}/commits?per_page=10", headers=HEADERS)
        commits_res.raise_for_status()
        # commit_history = [
        #     {
        #         'sha': commit['sha'],
        #         'author': commit['commit']['author']['name'],
        #         'date': commit['commit']['author']['date'],
        #         'message': commit['commit']['message']
        #     } for commit in commits_res.json()
        # ]

        commit_history = []
        for commit in commits_res.json():
            commit_info = {
                'sha': commit['sha'],
                'author': commit['commit']['author']['name'], 
                'date': commit['commit']['author']['date'],
                'message': commit['commit']['message']
            }
            commit_history.append(commit_info)
            
        commit_history = []
        print("✅ Commit history fetched.")

        # Assemble the final JSON object
        final_output = {
            'repository': f"{CONFIG['OWNER']}/{CONFIG['REPO']}",
            'indexedAt': datetime.utcnow().isoformat() + "Z",
            'files': indexed_files,
            'commitHistory': commit_history
        }

        # Write to output file
        print(f"[5/5] Writing all data to {CONFIG['OUTPUT_FILE']}...")
        with open(CONFIG['OUTPUT_FILE'], 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2)

        print(f"\n🎉 Indexing complete! Check the '{CONFIG['OUTPUT_FILE']}' file.")

    except requests.exceptions.HTTPError as e:
        print(f"❌ API Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()