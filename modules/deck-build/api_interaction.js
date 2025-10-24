// API交互逻辑的模块
// 更改角色页码
function changeCharacterPage(direction) {
    const newPage = currentCharPage + direction;
    if (newPage >= 1 && newPage <= totalCharPages) {
        currentCharPage = newPage;
        loadCharacterCardsPage();
    }
}

// 更改行动牌页码
function changeCardPage(direction) {
    const newPage = currentCardPage + direction;
    if (newPage >= 1 && newPage <= totalCardPages) {
        currentCardPage = newPage;
        loadCardPage();
    }
}

// 加载指定页码的角色卡
function loadCharacterCardsPage() {
    const params = new URLSearchParams();
    params.append('type', '角色牌');
    params.append('page', currentCharPage.toString());
    params.append('per_page', '12');
    
    if (currentCharFilters.country) params.append('country', currentCharFilters.country);
    if (currentCharFilters.element) params.append('element', currentCharFilters.element);
    if (currentCharFilters.weaponType) params.append('weapon_type', currentCharFilters.weaponType);
    if (currentCharFilters.search) params.append('search', currentCharFilters.search);
    
    const url = `/api/cards/filter?${params.toString()}`;
    const token = getJWTToken();
    const headers = token ? { 
        'Authorization': 'Bearer ' + token 
    } : {};
    
    fetch(url, {
        headers: headers
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('HTTP error ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            allCharacterCards = data.cards || [];
            if (currentTab === 'character') {
                displayCharacterCards(allCharacterCards);
            }
            // 确保传递的参数有效，默认值防止出错
            const total = data.total || 0;
            const pages = data.pages || 1;
            const currentPage = data.current_page || 1;
            updateCharacterPagination(total, pages, currentPage);
        })
        .catch(error => {
            console.error('Error loading character cards page:', error);
            // 错误处理：恢复到第一页
            currentCharPage = 1;
            updateCharacterPagination(0, 1, 1);
        });
}

// 加载指定页码的行动牌
function loadCardPage() {
    const params = new URLSearchParams();
    params.append('type', '非角色牌');
    params.append('page', currentCardPage.toString());
    params.append('per_page', '30');
    
    if (currentCardFilters.cost) params.append('cost', currentCardFilters.cost);
    if (currentCardFilters.search) params.append('search', currentCardFilters.search);
    
    // 添加标签参数
    currentCardFilters.tags.forEach(tag => {
        params.append('tag', tag);
    });
    
    const url = `/api/cards/filter?${params.toString()}`;
    const token = getJWTToken();
    const headers = token ? { 
        'Authorization': 'Bearer ' + token 
    } : {};
    
    fetch(url, {
        headers: headers
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('HTTP error ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            allCards = data.cards || [];
            if (currentTab === 'other') {
                displayCards(allCards);
            }
            // 确保传递的参数有效，默认值防止出错
            const total = data.total || 0;
            const pages = data.pages || 1;
            const currentPage = data.current_page || 1;
            updateCardPagination(total, pages, currentPage);
        })
        .catch(error => {
            console.error('Error loading card page:', error);
            // 错误处理：恢复到第一页
            currentCardPage = 1;
            updateCardPagination(0, 1, 1);
        });
}

// 更新角色卡分页信息
function updateCharacterPagination(total, totalPages, currentPage) {
    // 验证参数并设置默认值
    totalCharPages = totalPages && totalPages > 0 ? totalPages : 1;
    currentCharPage = currentPage && currentPage > 0 ? currentPage : 1;
    
    // 确保当前页不超过总页数
    if (currentCharPage > totalCharPages) {
        currentCharPage = totalCharPages;
    }
    
    const pageInfo = document.getElementById('characterPageInfo');
    if (pageInfo) {
        pageInfo.textContent = `第 ${currentCharPage} 页，共 ${totalCharPages} 页 (共 ${total || 0} 张)`;
    }
    
    const prevButton = document.querySelector('#characterPagination button:first-child');
    const nextButton = document.querySelector('#characterPagination button:last-child');
    
    if (prevButton) {
        prevButton.disabled = currentCharPage <= 1;
    }
    if (nextButton) {
        nextButton.disabled = currentCharPage >= totalCharPages;
    }
    
    const paginationContainer = document.getElementById('characterPagination');
    if (paginationContainer) {
        paginationContainer.style.display = totalCharPages > 1 ? 'block' : 'none';
    }
}

// 更新行动牌分页信息
function updateCardPagination(total, totalPages, currentPage) {
    // 验证参数并设置默认值
    totalCardPages = totalPages && totalPages > 0 ? totalPages : 1;
    currentCardPage = currentPage && currentPage > 0 ? currentPage : 1;
    
    // 确保当前页不超过总页数
    if (currentCardPage > totalCardPages) {
        currentCardPage = totalCardPages;
    }
    
    const pageInfo = document.getElementById('cardPageInfo');
    if (pageInfo) {
        pageInfo.textContent = `第 ${currentCardPage} 页，共 ${totalCardPages} 页 (共 ${total || 0} 张)`;
    }
    
    const prevButton = document.querySelector('#cardPagination button:first-child');
    const nextButton = document.querySelector('#cardPagination button:last-child');
    
    if (prevButton) {
        prevButton.disabled = currentCardPage <= 1;
    }
    if (nextButton) {
        nextButton.disabled = currentCardPage >= totalCardPages;
    }
    
    const paginationContainer = document.getElementById('cardPagination');
    if (paginationContainer) {
        paginationContainer.style.display = totalCardPages > 1 ? 'block' : 'none';
    }
}

// Login and authentication functions
async function loginUser() {
    const username = document.getElementById('usernameInput').value;
    const password = document.getElementById('passwordInput').value;
    const statusDiv = document.getElementById('loginStatus');
    
    if (!username || !password) {
        statusDiv.innerHTML = '<div class="error-message">请输入用户名和密码</div>';
        return;
    }
    
    try {
        const response = await fetch('/api/auth/login', {
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
            // Store the token
            localStorage.setItem('jwt_token', data.access_token);
            
            // Update UI to show logged in state
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('userInfo').style.display = 'flex';
            document.getElementById('currentUsername').textContent = username;
            statusDiv.innerHTML = '<div class="success-message">登录成功！</div>';
            
            // Reload cards after successful login
            loadCards();
        } else {
            statusDiv.innerHTML = '<div class="error-message">登录失败: ' + (data.message || '用户名或密码错误') + '</div>';
        }
    } catch (error) {
        statusDiv.innerHTML = '<div class="error-message">登录请求失败: ' + error.message + '</div>';
    }
}

function logoutUser() {
    // Remove the token
    localStorage.removeItem('jwt_token');
    
    // Update UI to show logged out state
    document.getElementById('loginForm').style.display = 'flex';
    document.getElementById('userInfo').style.display = 'none';
    document.getElementById('usernameInput').value = 'test';
    document.getElementById('passwordInput').value = 'test';
    document.getElementById('loginStatus').innerHTML = '<div class="success-message">已登出</div>';
}

// 保存卡组功能
async function saveDeck() {
    const deckName = document.getElementById('deckName').value;
    const deckDescription = document.getElementById('deckDescription').value;
    const statusDiv = document.getElementById('saveDeckStatus');
    
    if (!deckName) {
        statusDiv.innerHTML = '<div class="error-message">请输入卡组名称</div>';
        return;
    }
    
    // 检查卡组是否有效
    if (deck.characters.length !== 3 || deck.cards.length === 0) {
        statusDiv.innerHTML = '<div class="error-message">请构建一个有效的卡组（3个角色和至少1张行动牌）</div>';
        return;
    }
    
    // 验证卡组
    const deckData = {
        name: deckName,
        character_ids: deck.characters.map(c => c.id),
        card_ids: deck.cards.map(c => c.id),
        description: deckDescription
    };
    
    try {
        const token = getJWTToken();
        if (!token) {
            statusDiv.innerHTML = '<div class="error-message">请先登录</div>';
            return;
        }
        
        const response = await fetch('/api/deck', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            },
            body: JSON.stringify({
                name: deckName,
                card_ids: deck.cards.map(c => c.id),
                character_card_ids: deck.characters.map(c => c.id),
                description: deckDescription
            })
        });
        
        const result = await response.json();
        
        if (response.ok) {
            statusDiv.innerHTML = `<div class="success-message">卡组 "${result.deck_name}" 创建成功！ID: ${result.deck_id}</div>`;
            // 清空输入框
            document.getElementById('deckName').value = '';
            document.getElementById('deckDescription').value = '';
        } else {
            statusDiv.innerHTML = `<div class="error-message">创建卡组失败: ${result.message}</div>`;
        }
    } catch (error) {
        statusDiv.innerHTML = `<div class="error-message">保存卡组时发生错误: ${error.message}</div>`;
    }
}