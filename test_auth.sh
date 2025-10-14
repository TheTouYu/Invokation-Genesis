#!/bin/bash

echo "Testing User Registration..."
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpassword"}'

echo -e "\n\nTesting User Login..."
LOGIN_RESPONSE=$(curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpassword"}' \
  -s)

echo $LOGIN_RESPONSE

# 提取访问令牌
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo -e "\n\nTesting Profile Access with JWT..."
curl -X GET http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer $ACCESS_TOKEN"

echo -e "\n\nTesting with Invalid Token..."
curl -X GET http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer invalidtoken"