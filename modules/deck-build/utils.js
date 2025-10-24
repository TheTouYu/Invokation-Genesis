// Deck data structure
let deck = {
    characters: [],
    cards: []
};

// Available cards
let allCards = [];
let allCharacterCards = [];

// Page state
let currentTab = 'character';

// 分页相关状态
let currentCharPage = 1;
let totalCharPages = 1;
let currentCardPage = 1;
let totalCardPages = 1;

// 分页相关的过滤参数
let currentCharFilters = { country: '', element: '', weaponType: '', search: '' };
let currentCardFilters = { cost: '', search: '', tags: [] };

// 获取JWT token的函数
function getJWTToken() {
    // 尝试从localStorage获取token
    let token = localStorage.getItem('jwt_token');
    if (!token) {
        // 如果localStorage中没有，尝试从cookie获取
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith('access_token_cookie=')) {
                token = cookie.substring('access_token_cookie='.length, cookie.length);
                break;
            }
        }
    }
    return token;
}

// 检查是否需要认证的API端点
function needsAuth(url) {
    // Authentication endpoints that don't require a token:
    // - /api/auth/login for login
    // - /api/auth/register for registration
    if (url.includes('/api/auth/login') || 
        url.includes('/api/auth/register')) {
        return false;
    }
    
    // All other endpoints require authentication
    return true;
}

// Format cost for display
function formatCostDisplay(cost) {
    if (!cost || !Array.isArray(cost) || cost.length === 0) {
        return 'N/A';
    }
    
    // Handle the case where cost is an array of objects like [{"type": "火", "value": 1}]
    return cost.map(c => {
        if (typeof c === 'object' && c !== null) {
            if (c.type && c.value !== undefined) {
                return `${c.type}:${c.value}`;
            } else if (c.type) {
                return c.type;
            } else if (c.value !== undefined) {
                return c.value;
            }
        }
        return c;
    }).join(', ');
}

// 获取所有选中的标签
function getSelectedTags() {
    const selectedTags = [];
    const tagButtons = document.querySelectorAll('#tagButtonsContainer .tag-btn-selected');
    tagButtons.forEach(button => {
        // Extract tag from button id: tagbtn_标签名 -> 标签名
        const tag = button.id.replace('tagbtn_', '');
        selectedTags.push(tag);
    });
    return selectedTags;
}