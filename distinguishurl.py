from github import Github
import openai
import re
import os

# Initialize Github instance with your personal access token
g = Github("your_github_token")

# Function to get content from a single file
def get_file_content(repo, path):
    file_content = repo.get_contents(path)
    return file_content.decoded_content.decode("utf-8")

# Function to recursively get all files in the repository
def get_all_files_in_repo(repo, path=""):
    contents = repo.get_contents(path)
    files = []
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:
            files.append(file_content)
    return files

# Function to handle URL and process content
def process_github_url(url):
    # Parse the URL
    match = re.match(r'https://github.com/([^/]+)/([^/]+)(/blob/(.+))?', url)
    if not match:
        print("Invalid GitHub URL")
        return
    
    owner, repo_name, _, file_path = match.groups()
    repo = g.get_repo(f"{owner}/{repo_name}")
    
    if file_path:
        # Single file
        print(f"Processing single file: {file_path}")
        file_content = get_file_content(repo, file_path)
        
        # Process with Azure OpenAI API
        response = openai.Completion.create(
            engine="davinci-codex",  # or any other model you are using
            prompt=file_content,
            max_tokens=100
        )
        print(f"Response for file {file_path}:")
        print(response.choices[0].text.strip())
    else:
        # Repository
        print(f"Processing repository: {owner}/{repo_name}")
        all_files = get_all_files_in_repo(repo)
        
        for file in all_files:
            file_content = file.decoded_content.decode("utf-8")
            file_name = os.path.basename(file.path)
            
            # Process with Azure OpenAI API
            response = openai.Completion.create(
                engine="davinci-codex",  # or any other model you are using
                prompt=file_content,
                max_tokens=100
            )
            
            print(f"Response for file {file.path}:")
            print(response.choices[0].text.strip())
            print("\n" + "-"*60 + "\n")

# Example URLs
url1 = "https://github.com/starinfinity/share"
url2 = "https://github.com/starinfinity/share/blob/main/holiday_check.py"

# Set up your Azure OpenAI API key
openai.api_key = "your_azure_openai_api_key"

# Process the URLs
process_github_url(url1)
process_github_url(url2)
