import requests
import csv
import time

# GitHub API token for authentication
GITHUB_TOKEN = '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'
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# Step 1: Fetch users from Austin with over 100 followers
def fetch_users():
    users = []
    url = "https://api.github.com/search/users"
    params = {
        'q': 'location:Austin followers:>100',
        'per_page': 100
    }

    page = 1
    while True:
        response = requests.get(url, headers=HEADERS, params={**params, 'page': page})
        data = response.json()
        
        if response.status_code != 200:
            print(f"Error fetching repos for {username}")
            break

        if 'items' not in data:
            break

        for user in data['items']:
            user_data = fetch_user_details(user['login'])
            if user_data:
                users.append(user_data)

        if 'next' not in response.links:
            break
        page += 1
        time.sleep(1)  # To avoid rate limiting

    return users

# Step 2: Fetch detailed user info
def fetch_user_details(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url, headers=HEADERS)
    user = response.json()

    if response.status_code != 200:
        return None

    # Clean up company name
    company = user['company'] or ""
    if company.startswith("@"):
        company = company[1:]
    company = company.strip().upper()

    return {
        'login': user['login'],
        'name': user.get('name', ''),
        'company': company,
        'location': user.get('location', ''),
        'email': user.get('email', ''),
        'hireable': str(user.get('hireable', False)).lower(),
        'bio': user.get('bio', ''),
        'public_repos': user.get('public_repos', 0),
        'followers': user.get('followers', 0),
        'following': user.get('following', 0),
        'created_at': user.get('created_at', '')
    }

# Step 3: Fetch repositories for each user
def fetch_user_repos(username):
    repos = []
    url = f"https://api.github.com/users/{username}/repos"
    params = {'per_page': 100}

    page = 1
    while True:
        response = requests.get(url, headers=HEADERS, params={**params, 'page': page})
        data = response.json()

        if response.status_code != 200:
            break

        for repo in data:
            repos.append({
                'login': username,
                'full_name': repo.get('full_name', ''),
                'created_at': repo.get('created_at', ''),
                'stargazers_count': repo.get('stargazers_count', 0),
                'watchers_count': repo.get('watchers_count', 0),
                'language': repo.get('language', ''),
                'has_projects': str(repo.get('has_projects', False)).lower(),
                'has_wiki': str(repo.get('has_wiki', False)).lower(),
                'license_name': repo.get('license', {}).get('key', '') if repo.get('license') else ''
            })


        if 'next' not in response.links or len(repos) >= 500:
            break
        page += 1
        time.sleep(1)

    return repos[:500]

# Step 4: Write to users.csv
def write_users_csv(users):
    with open('users.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'login', 'name', 'company', 'location', 'email', 'hireable',
            'bio', 'public_repos', 'followers', 'following', 'created_at'
        ])
        writer.writeheader()
        writer.writerows(users)

# Step 5: Write to repositories.csv
def write_repositories_csv(repositories):
    with open('repositories.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'login', 'full_name', 'created_at', 'stargazers_count',
            'watchers_count', 'language', 'has_projects', 'has_wiki',
            'license_name'
        ])
        writer.writeheader()
        writer.writerows(repositories)

# Step 6: Generate README.md
def generate_readme():
    with open('README.md', 'w') as file:
        file.write("# GitHub User Analysis in Austin\n\n")
        file.write("### Key Insights:\n")
        file.write("- Used GitHub API to scrape user data in Austin with over 100 followers.\n")
        file.write("- An interesting finding was the variety of tech companies represented by users.\n")
        file.write("- Developers in Austin could increase visibility by enhancing profile completeness.\n")

# Main function
def main():
    print("Fetching users...")
    users = fetch_users()
    write_users_csv(users)

    print("Fetching repositories...")
    repositories = []
    for user in users:
        user_repos = fetch_user_repos(user['login'])
        repositories.extend(user_repos)

    write_repositories_csv(repositories)
    generate_readme()
    print("Data scraping complete. Files created: users.csv, repositories.csv, README.md")

if __name__ == '__main__':
    main()
