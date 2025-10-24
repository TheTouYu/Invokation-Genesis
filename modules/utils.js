// 存储从API获取的数据
let users = [];
let decks = [];
let gameSessions = [];
let replays = [];

// 通用API请求函数
async function apiRequest(url, method = 'GET', data = null) {
    const token = document.getElementById('jwtToken').value;
    
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
    const savedToken = localStorage.getItem('jwtToken');
    if (savedToken) {
        document.getElementById('jwtToken').value = savedToken;
        document.getElementById('authStatus').innerText = '已加载保存的Token';
    }
    
    // 初始加载用户和卡组数据
    loadUsers();
    loadUserDecks();
});

// 保存Token到localStorage
function saveToken() {
    const token = document.getElementById('jwtToken').value;
    localStorage.setItem('jwtToken', token);
    document.getElementById('authStatus').innerText = 'Token已保存';
}