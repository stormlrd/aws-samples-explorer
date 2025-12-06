import requests
import time

def get_aws_samples_repos():
    """
    Fetch all repositories from the aws-samples GitHub organization using the GitHub API.
    """
    repos = []
    page = 1
    per_page = 100  # Max allowed by GitHub API
    
    print("Fetching aws-samples repositories using GitHub API...")
    
    while True:
        url = f"https://api.github.com/orgs/aws-samples/repos?page={page}&per_page={per_page}"
        
        try:
            response = requests.get(url, headers={
                'Accept': 'application/vnd.github+json',
                'User-Agent': 'aws-samples-repo-lister'
            })
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                break
            
            for repo in data:
                repo_name = repo['name']
                repos.append({
                    'name': repo_name,
                    'url': repo['html_url'],
                    'description': repo['description'],
                    'stars': repo['stargazers_count']
                })
                print(f"Found: {repo_name} ({repo['stargazers_count']} stars)")
            
            print(f"Page {page} complete - {len(data)} repos found")
            
            if len(data) < per_page:
                break
            
            page += 1
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            break
    
    return repos

if __name__ == "__main__":
    repositories = get_aws_samples_repos()
    
    print(f"\n{'='*50}")
    print(f"Total repositories found: {len(repositories)}")
    print(f"{'='*50}\n")
    
    # Save to text file
    with open('aws_samples_repos.txt', 'w', encoding='utf-8') as f:
        for repo in repositories:
            f.write(f"{repo['name']}\n")
    
    # Save detailed info to CSV
    with open('aws_samples_repos.csv', 'w', encoding='utf-8') as f:
        f.write("Name,URL,Stars,Description\n")
        for repo in repositories:
            desc = (repo['description'] or '').replace('"', '""')
            f.write(f'"{repo["name"]}","{repo["url"]}",{repo["stars"]},"{desc}"\n')
    
    print("Repository list saved to 'aws_samples_repos.txt'")
    print("Detailed info saved to 'aws_samples_repos.csv'")
