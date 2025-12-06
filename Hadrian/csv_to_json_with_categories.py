import csv
import json
import re

# AWS Console categories
AWS_CATEGORIES = {
    'Compute': ['ec2', 'lambda', 'batch', 'fargate', 'eks', 'ecs', 'lightsail', 'serverless'],
    'Storage': ['s3', 'ebs', 'efs', 'fsx', 'glacier', 'storage', 'backup'],
    'Database': ['rds', 'dynamodb', 'aurora', 'redshift', 'neptune', 'documentdb', 'elasticache', 'timestream', 'keyspaces', 'qldb'],
    'Networking & Content Delivery': ['vpc', 'cloudfront', 'route53', 'api-gateway', 'apigw', 'direct-connect', 'app-mesh', 'cloud-map', 'global-accelerator', 'elb', 'load-balancer'],
    'Security, Identity, & Compliance': ['iam', 'cognito', 'secrets-manager', 'guardduty', 'inspector', 'macie', 'security', 'kms', 'acm', 'certificate', 'waf', 'shield', 'firewall'],
    'Machine Learning': ['sagemaker', 'rekognition', 'comprehend', 'lex', 'polly', 'transcribe', 'translate', 'forecast', 'personalize', 'textract', 'kendra', 'ml', 'ai', 'bedrock'],
    'Analytics': ['athena', 'emr', 'cloudwatch', 'elasticsearch', 'opensearch', 'kinesis', 'quicksight', 'data-pipeline', 'glue', 'lake-formation', 'msk', 'kafka'],
    'Developer Tools': ['codecommit', 'codebuild', 'codedeploy', 'codepipeline', 'cloud9', 'x-ray', 'cli', 'sdk', 'cdk', 'sam', 'amplify', 'devops'],
    'Management & Governance': ['cloudformation', 'cloudtrail', 'config', 'opsworks', 'service-catalog', 'systems-manager', 'trusted-advisor', 'control-tower', 'organizations', 'resource-groups'],
    'Containers': ['ecr', 'ecs', 'eks', 'fargate', 'docker', 'kubernetes', 'k8s', 'container'],
    'Application Integration': ['sns', 'sqs', 'eventbridge', 'step-functions', 'swf', 'mq', 'appsync', 'event'],
    'IoT': ['iot', 'greengrass', 'freertos', 'sitewise', 'things'],
    'Media Services': ['elemental', 'media', 'ivs', 'kinesis-video'],
    'Migration & Transfer': ['migration', 'dms', 'datasync', 'transfer', 'snowball'],
    'Mobile': ['mobile', 'amplify', 'appsync', 'device-farm', 'pinpoint'],
    'Frontend & Web': ['amplify', 'appsync', 'web', 'frontend', 'react', 'vue', 'angular'],
    'Blockchain': ['blockchain', 'managed-blockchain', 'qldb'],
    'Quantum': ['braket', 'quantum'],
    'Robotics': ['robomaker', 'robot'],
    'Satellite': ['ground-station', 'satellite'],
}

def categorize_repo(name, description):
    """
    Categorize a repository based on its name and description.
    """
    text = f"{name} {description or ''}".lower()
    
    matched_categories = []
    
    for category, keywords in AWS_CATEGORIES.items():
        for keyword in keywords:
            if keyword in text:
                matched_categories.append(category)
                break
    
    # Return the first match, or 'Other' if no match
    return matched_categories[0] if matched_categories else 'Other'

def csv_to_json():
    """
    Convert CSV file to JSON with categories.
    """
    repos = []
    uncategorized = []
    
    with open('aws_samples_repos.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            category = categorize_repo(row['Name'], row['Description'])
            
            repo_data = {
                'name': row['Name'],
                'url': row['URL'],
                'stars': int(row['Stars']) if row['Stars'].isdigit() else 0,
                'description': row['Description'],
                'category': category,
                'uncategorized': category == 'Other'
            }
            
            repos.append(repo_data)
            
            if category == 'Other':
                uncategorized.append(repo_data)
    
    # Sort by category, then by stars
    repos.sort(key=lambda x: (x['category'], -x['stars']))
    
    # Create output structure
    output = {
        'organization': 'aws-samples',
        'total_repositories': len(repos),
        'uncategorized_count': len(uncategorized),
        'repositories': repos
    }
    
    # Save to JSON
    with open('aws_samples_repos.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Save uncategorized to separate file
    if uncategorized:
        with open('aws_samples_repos_uncategorized.json', 'w', encoding='utf-8') as f:
            json.dump({
                'uncategorized_repositories': uncategorized,
                'count': len(uncategorized)
            }, f, indent=2, ensure_ascii=False)
    
    # Print category summary
    category_counts = {}
    for repo in repos:
        cat = repo['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print(f"Total repositories: {len(repos)}")
    print(f"\nRepositories by category:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        marker = " ⚠️ UNCATEGORIZED" if cat == 'Other' else ""
        print(f"  {cat}: {count}{marker}")
    
    print(f"\nJSON file saved to 'aws_samples_repos.json'")
    
    if uncategorized:
        print(f"Uncategorized repos saved to 'aws_samples_repos_uncategorized.json'")
        print(f"\nUncategorized repositories ({len(uncategorized)}):")
        for repo in uncategorized[:10]:
            print(f"  - {repo['name']}")
        if len(uncategorized) > 10:
            print(f"  ... and {len(uncategorized) - 10} more")

if __name__ == "__main__":
    csv_to_json()
