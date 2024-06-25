#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, render_template_string, request
import threading
import webbrowser
from IPython.display import IFrame, display
import requests

# Enhanced HTML template with CSS animations and improved styling
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Repository Content</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bulma/0.9.3/css/bulma.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css"/>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f0f0f0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: auto;
        }
        .content-container {
            background: #ffffff;
            border-radius: 12px;
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
            padding: 30px;
            margin-top: 20px;
            animation: fadeIn 1s;
        }
        .content-title {
            font-size: 28px;
            font-weight: bold;
            color: #333;
            margin-bottom: 15px;
            text-align: center;
        }
        .content-section {
            margin-bottom: 25px;
        }
        .content-section h2 {
            font-size: 22px;
            font-weight: bold;
            color: #4A90E2;
            margin-bottom: 10px;
        }
        .content-item {
            margin-bottom: 15px;
            padding-left: 15px;
            position: relative;
        }
        .content-item p {
            margin: 0;
            font-size: 18px;
            color: #555;
        }
        .content-item p strong {
            font-weight: bold;
            color: #333;
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="content-container animate__animated animate__fadeInUp">
            <div class="content-title">GitHub Repository Content</div>
            <div class="content-section">
                <h2>Repository Details</h2>
                <div class="content-item">
                    <p><strong>Name: </strong>{{ repo_name }}</p>
                </div>
                <div class="content-item">
                    <p><strong>Description: </strong>{{ repo_description }}</p>
                </div>
                <div class="content-item">
                    <p><strong>Language: </strong>{{ repo_language }}</p>
                </div>
                <div class="content-item">
                    <p><strong>Clone URL: </strong><a href="{{ repo_clone_url }}">{{ repo_clone_url }}</a></p>
                </div>
            </div>
            <div class="content-section">
                <h2>Files</h2>
                {% for file in repo_files %}
                <div class="content-item">
                    <p><strong>{{ file['name'] }}</strong></p>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</body>
</html>
"""

app = Flask(__name__)

def fetch_github_repo_info(repo_url):
    api_url = repo_url.replace("github.com", "api.github.com/repos")
    response = requests.get(api_url)
    if response.status_code == 200:
        repo_info = response.json()
        contents_url = repo_info["contents_url"].replace("{+path}", "")
        files_response = requests.get(contents_url)
        if files_response.status_code == 200:
            repo_files = files_response.json()
            return {
                "name": repo_info["name"],
                "description": repo_info["description"],
                "language": repo_info["language"],
                "clone_url": repo_info["clone_url"],
                "files": repo_files
            }
    return None

@app.route('/')
def feedback():
    repo_url = request.args.get("repo_url", "")
    if repo_url:
        repo_info = fetch_github_repo_info(repo_url)
        if repo_info:
            return render_template_string(html_template,
                                          repo_name=repo_info["name"],
                                          repo_description=repo_info["description"],
                                          repo_language=repo_info["language"],
                                          repo_clone_url=repo_info["clone_url"],
                                          repo_files=repo_info["files"])
        else:
            return "Invalid repository URL or the repository could not be fetched.", 400
    else:
        return "No repository URL provided.", 400

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Run Flask app in a separate thread
threading.Thread(target=run_flask).start()

# Example GitHub repository URL
repo_url = "https://github.com/Username/repository"
#paste a valid repo url 

# Open the app in the default web browser with the repository URL as a parameter
webbrowser.open(f"http://127.0.0.1:5000?repo_url={repo_url}")

# Display the web app in an iframe within the Jupyter notebook
display(IFrame(src=f"http://127.0.0.1:5000?repo_url={repo_url}", width='100%', height='600px'))


# In[ ]:


import os
import requests
import openai
from flask import Flask, request, render_template_string

# Setting up OpenAI API key
openai.api_key = 'Use_api_key_here'
#openai api key can be accessed from openai platform or generating it

app = Flask(__name__)

# Function to get all Python files from GitHub repository
def get_python_files_from_github(repo_url):
    if repo_url.endswith('/'):
        repo_url = repo_url[:-1]
    api_url = f"https://api.github.com/repos/{'/'.join(repo_url.split('/')[-2:])}/contents/"

    def fetch_files(url, files):
        response = requests.get(url)
        if response.status_code == 200:
            items = response.json()
            for item in items:
                if item['type'] == 'file' and item['name'].endswith('.py'):
                    files.append(item['download_url'])
                elif item['type'] == 'dir':
                    fetch_files(item['url'], files)
        return files

    return fetch_files(api_url, [])

# Function to read the content of a file from a URL
def read_file_from_url(file_url):
    response = requests.get(file_url)
    if response.status_code == 200:
        return response.text
    return ""

# Function to get a code review from OpenAI GPT-3.5-turbo model
def get_code_review(code):
    messages = [
        {"role": "system", "content": "You are a code reviewer. Review the following Python code for any issues, bugs, improvements, or best practices. Provide detailed feedback."},
        {"role": "user", "content": code}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=500,
        temperature=0.5,
    )

    return response.choices[0].message['content'].strip()

# Function to generate chat completion for any user question
def generate_chat_completion(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=[{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}],
        max_tokens=250,
        temperature=0.7,
    )
    return response.choices[0].message['content'].strip()

# HTML template with enhanced visuals and background video
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Intelligent Code Review System</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bulma/0.9.3/css/bulma.min.css">
    <style>
        body {
            font-family: 'Poppins', sans-serif;
            margin: 0;
            padding: 0;
            overflow: hidden;
            color: #fff;
        }
        #background-video {
            position: fixed;
            right: 0;
            bottom: 0;
            min-width: 100%;
            min-height: 100%;
            z-index: -1;
        }
        .container {
            margin-top: 50px;
            z-index: 1;
            position: relative;
        }
        .title {
            font-weight: 600;
            text-align: center;
            text-shadow: 2px 2px 5px rgba(255, 255, 255, 0.8), 3px 3px 10px rgba(0, 0, 0, 0.3);
            color: #ffeb3b;
        }
        .button.is-link {
            background: #ff416c;
            background: linear-gradient(to right, #ff4b2b, #ff416c);
            border: none;
            box-shadow: 0 4px 15px 0 rgba(255, 65, 108, 0.75);
        }
        .scrollable-content {
            max-height: 300px;
            overflow-y: auto;
            background: rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 10px;
        }
        .gpt-box {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 300px;
            background: rgba(0, 0, 0, 0.8);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            padding: 15px;
            z-index: 2;
            color: #fff;
        }
        .gpt-box .title {
            font-weight: 400;
            font-size: 18px;
            text-shadow: 1px 1px 3px rgba(255, 255, 255, 0.7), 2px 2px 5px rgba(0, 0, 0, 0.3);
        }
        .gpt-box .input, .gpt-box .button {
            margin-bottom: 10px;
        }
        .message.is-info {
            background: rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            border-radius: 10px;
        }
        .message-body pre {
            white-space: pre-wrap;
        }
    </style>
</head>
<body>
    <video autoplay muted loop id="background-video">
        <source src="https://cdn.pixabay.com/video/2019/07/20/25380-350507864_large.mp4" type="video/mp4">
        Your browser does not support HTML5 video.
    </video>

    <section class="section">
        <div class="container">
            <h1 class="title">Intelligent Code Review System</h1>
            <form method="POST" action="/">
                <div class="field">
                    <label class="label" style="text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5); color: #ffeb3b;">Enter a GitHub Repository Link</label>
                    <div class="control">
                        <input class="input" type="text" name="repo_url" placeholder="https://github.com/username/repository" required>
                    </div>
                </div>
                <div class="control">
                    <button class="button is-link" type="submit">Get Code Review</button>
                </div>
            </form>
            <hr>
            {% if reviews %}
                <h2 class="title" style="text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.5); color: #ffeb3b;">Code Reviews</h2>
                <div class="content scrollable-content">
                    {% for review in reviews %}
                        <article class="message is-info">
                            <div class="message-header">
                                <p>{{ review.file_url }}</p>
                            </div>
                            <div class="message-body">
                                <pre>{{ review.review }}</pre>
                            </div>
                        </article>
                    {% endfor %}
                </div>
            {% else %}
                <p>No reviews available. Enter a GitHub repository link above to get started.</p>
            {% endif %}
        </div>
    </section>

    <div class="gpt-box">
        <h2 class="title">Ask Me Anything</h2>
        <form method="POST" action="/ask-gpt">
            <div class="field">
                <div class="control">
                    <input class="input" type="text" name="gpt_question" placeholder="Ask a question..." required>
                </div>
            </div>
            <div class="control">
                <button class="button is-link" type="submit">Ask GPT</button>
            </div>
        </form>
        {% if gpt_response %}
            <hr>
            <div class="content scrollable-content">
                <p><strong>Response:</strong></p>
                <p>{{ gpt_response }}</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        repo_url = request.form['repo_url']
        python_files = get_python_files_from_github(repo_url)
        reviews = []

        for file_url in python_files:
            code = read_file_from_url(file_url)
            if code:
                review = get_code_review(code)
                reviews.append({'file_url': file_url, 'review': review})

        return render_template_string(html_template, reviews=reviews, gpt_response=None)

    return render_template_string(html_template, reviews=None, gpt_response=None)

@app.route('/ask-gpt', methods=['POST'])
def ask_gpt():
    question = request.form['gpt_question']
    response = generate_chat_completion(question)
    return render_template_string(html_template, reviews=None, gpt_response=response)

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

