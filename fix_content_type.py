#!/usr/bin/env python3
"""
Script to fix the Content-Type in api_test_page function
"""
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the Content-Type line
content = content.replace(
    "return test_page_html, 200, {\"'Content-Type'\": 'text/html'}",
    "return test_page_html, 200, {'Content-Type': 'text/html'}"
)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed the Content-Type in api_test_page function")