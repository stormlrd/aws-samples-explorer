import requests
import time
import os

def fetch_aws_samples_repos():
    """
    Fetch and write repositories from aws-samples GitHub organization incrementally.
    Memory-efficient: writes to files as data is fetched instead of storing everything in memory.
    """
    page = 1
    per_page = 100
    total_count = 0
    
    # Get GitHub token from environment variable (optional but recommended)
    github_token = os.environ.get('GITHUB_TOKEN')
    
    headers = {
        'Accept': 'application/vnd.github+json',
        'User-Agent': 'aws-samples-repo-lister'
    }
    
    if github_token:
        headers['Authorization'] = f'token {github_token}'
        print("Using authenticated GitHub API (5000 requests/hour)")
    else:
        print("Using unauthenticated GitHub API (60 requests/hour)")
        print("Tip: Set GITHUB_TOKEN environment variable for higher rate limits")
    
    print("Fetching aws-samples repositories using GitHub API...")
    
    # Open files for writing (will overwrite existing files)
    with open('aws_samples_repos.txt', 'w', encoding='utf-8') as txt_file, \
         open('aws_samples_repos.csv', 'w', encoding='utf-8') as csv_file:
        
        # Write CSV header
        csv_file.write("Name,URL,Stars,Description\n")
        
        while True:
            url = f"https://api.github.com/orgs/aws-samples/repos?page={page}&per_page={per_page}"
            
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                
                if not data:
                    break
                
                # Write repos immediately as we fetch them
                for repo in data:
                    repo_name = repo['name']
                    repo_url = repo['html_url']
                    repo_stars = repo['stargazers_count']
                    repo_desc = repo['description'] or ''
                    
                    # Write to text file
                    txt_file.write(f"{repo_name}\n")
                    
                    # Write to CSV file (escape quotes in description)
                    desc_escaped = repo_desc.replace('"', '""')
                    csv_file.write(f'"{repo_name}","{repo_url}",{repo_stars},"{desc_escaped}"\n')
                    
                    total_count += 1
                    print(f"Found: {repo_name} ({repo_stars} stars)")
                
                print(f"Page {page} complete - {len(data)} repos found (Total: {total_count})")
                
                if len(data) < per_page:
                    break
                
                page += 1
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error on page {page}: {e}")
                break
    
    return total_count

if __name__ == "__main__":
    total = fetch_aws_samples_repos()
    
    print(f"\n{'='*50}")
    print(f"Total repositories found: {total}")
    print(f"{'='*50}\n")
    print("Repository list saved to 'aws_samples_repos.txt'")
    print("Detailed info saved to 'aws_samples_repos.csv'")
