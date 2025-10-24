// 初始化模块
// Check if user is already logged in when page loads
document.addEventListener('DOMContentLoaded', function() {
    const token = localStorage.getItem('jwt_token');
    if (token) {
        // Check if token is valid by making a simple request
        fetch('/api/auth/profile', {
            headers: {
                'Authorization': 'Bearer ' + token
            }
        })
        .then(response => {
            if (response.ok) {
                // Token is valid, update UI
                document.getElementById('loginForm').style.display = 'none';
                document.getElementById('userInfo').style.display = 'flex';
                // We can't get username from token directly, so we'll just show generic text
                document.getElementById('currentUsername').textContent = '已登录用户';
            } else {
                // Token is invalid, remove it
                localStorage.removeItem('jwt_token');
            }
        })
        .catch(() => {
            // Error occurred, remove token
            localStorage.removeItem('jwt_token');
        });
    }
    
    loadCards(); // Load cards from API
    loadCharacterFilters(); // Load character filter options
    populateTagCheckboxes(); // Initialize tag buttons for other cards
});