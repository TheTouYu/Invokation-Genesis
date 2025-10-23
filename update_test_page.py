#!/usr/bin/env python3
"""
Script to update the api_test_page function in app.py to read HTML from file
"""
import re

# Read the app.py file
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the new function
new_function = '''        @app.route('/api/test', methods=['GET'])
        def api_test_page():
            """提供API测试页面"""
            with open('api_test_page.html', 'r', encoding='utf-8') as f:
                test_page_html = f.read()
            return test_page_html, 200, {'Content-Type': 'text/html'}'''

# Replace the function using regex
# This pattern looks for the function definition and replaces it with the new one
pattern = r'@\w+\[.*?def api_test_page\(\):\n\s*"""提供API测试页面"""\n.*?return.*?text/html\'\}'
replacement = new_function

# Use re.DOTALL to match across multiple lines
updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write the updated content back to the file
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(updated_content)

print("Successfully updated the api_test_page function to read HTML from file")