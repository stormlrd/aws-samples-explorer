# AWS Samples Repository Explorer

A Streamlit app to explore and discover repositories from the AWS Samples GitHub organization.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Scrape AWS Samples Repositories

Run the scraper to fetch all repositories from the aws-samples GitHub organization:

```bash
python list_aws_samples_repos.py
```

This will create:
- `aws_samples_repos.txt` - Simple list of repository names
- `aws_samples_repos.csv` - Detailed CSV with name, URL, stars, and description

### Step 2: Convert to JSON with Categories

Process the CSV and categorize repositories:

```bash
python csv_to_json_with_categories.py
```

This will create:
- `aws_samples_repos.json` - Main JSON file with categorized repositories
- `aws_samples_repos_uncategorized.json` - Repositories that couldn't be categorized

### Step 3: Run the Streamlit App

Launch the interactive explorer:

```bash
streamlit run app.py
```

The app will open in your browser with features including:
- Overview dashboard with metrics and visualizations
- Search and filter capabilities
- Analytics and statistics
- Browse by category
- Top repositories ranking
- Quick links for common use cases

## Features

- 📊 Interactive visualizations using Plotly
- 🔍 Search and filter repositories
- 📂 Browse by AWS service categories
- ⭐ Sort by popularity (stars)
- 📈 Analytics and statistics
- 🎯 Quick links for common use cases
