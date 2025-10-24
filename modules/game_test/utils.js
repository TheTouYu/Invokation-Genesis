// 存储从API获取的数据
let users = [];
let decks = [];
let gameSessions = [];
let replays = [];
let jwtToken = '';

// 登录函数
async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const loginStatus = document.getElementById('loginStatus');
    
    if (!username || !password) {
        loginStatus.innerHTML = '<div class="error">请输入用户名和密码</div>';
        return;
    }
    
    try {
        const response = await fetch(`${window.location.origin}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            jwtToken = data.access_token;
            document.getElementById('jwtToken').value = jwtToken; // 更新令牌输入框
            localStorage.setItem('jwtToken', jwtToken); // 存储到本地存储
            loginStatus.innerHTML = '<div class="success">登录成功！令牌已获取并保存</div>';
            
            // 加载初始数据
            loadInitialData();
        } else {
            loginStatus.innerHTML = `<div class="error">登录失败: ${data.message || data.error}</div>`;
        }
    } catch (error) {
        loginStatus.innerHTML = `<div class="error">请求失败: ${error.message}</div>`;
    }
}

// 加载初始数据（用户、卡组等）
async function loadInitialData() {
    // 从本地存储加载令牌
    const storedToken = localStorage.getItem('jwtToken');
    if (storedToken) {
        jwtToken = storedToken;
        document.getElementById('jwtToken').value = jwtToken;
        document.getElementById('authStatus').innerText = '已加载保存的Token';
    }
    
    // 如果有令牌，加载用户信息、卡组等数据
    if (jwtToken) {
        await loadUsers();
        await loadUserDecks();
    }
}

// 通用API请求函数
async function apiRequest(url, method = 'GET', data = null) {
    // 如果jwtToken变量有值，优先使用它；否则从输入框获取
    const token = jwtToken || document.getElementById('jwtToken').value;
    
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(url, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || `HTTP error! status: ${response.status}`);
        }
        
        return result;
    } catch (error) {
        console.error('API请求错误:', error);
        throw error;
    }
}

// 更新选择框选项的通用函数
function updateSelectOptions(selectId, items, valueField, textField) {
    const select = document.getElementById(selectId);
    if (!select) return;
    
    // 保存当前选择（如果有的话）
    const currentSelection = select.value;
    
    // 清空现有选项（保留刷新选项）
    Array.from(select.options).forEach(option => {
        if (option.value !== 'refresh') {
            select.removeChild(option);
        }
    });
    
    // 添加新选项
    items.forEach(item => {
        const option = document.createElement('option');
        option.value = item[valueField];
        option.textContent = item[textField];
        select.appendChild(option);
    });
    
    // 恢复之前的选项（如果仍然存在）
    if (items.some(item => item[valueField] === currentSelection)) {
        select.value = currentSelection;
    }
}

// 填充操作载荷示例
function fillPayloadExample(example) {
    document.getElementById('actionPayload').value = example;
}

// 从localStorage加载保存的token
document.addEventListener('DOMContentLoaded', function() {
    // 尝试加载初始数据（包括令牌和用户/卡组信息）
    loadInitialData();
});

// 保存Token到localStorage
function saveToken() {
    const token = document.getElementById('jwtToken').value;
    jwtToken = token; // 更新全局变量
    localStorage.setItem('jwtToken', token);
    document.getElementById('authStatus').innerText = 'Token已保存';
}