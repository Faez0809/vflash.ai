import os

with open('templates/base.html', 'r', encoding='utf-8') as f:
    base_html = f.read()

# Replace condition to include words
base_html = base_html.replace(
    "{% elif request.endpoint == 'dashboard' %}", 
    "{% elif request.endpoint in ['dashboard', 'words'] %}"
)

base_html = base_html.replace(
    "{% if request.endpoint not in ['login', 'signup', 'dashboard'] %}", 
    "{% if request.endpoint not in ['login', 'signup', 'dashboard', 'words'] %}"
)

with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(base_html)

print("Updated base.html")
