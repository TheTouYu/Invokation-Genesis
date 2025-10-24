// UI交互逻辑的模块
// Switch between tabs
function switchTab(tabName) {
    // Update tab UI
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    document.querySelector(`.tab[onclick*="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}Tab`).classList.add('active');
    
    currentTab = tabName;
    
    // Load cards based on selected tab
    if (tabName === 'character') {
        displayCharacterCards(allCharacterCards);
    } else if (tabName === 'other') {
        displayCards(allCards);
    }
}

// Filter cards using backend API
function filterCards() {
    // 保存当前过滤条件
    currentCardFilters = {
        cost: document.getElementById('costFilter').value,
        search: document.getElementById('searchInput').value,
        tags: getSelectedTags()
    };
    
    // 重置到第一页
    currentCardPage = 1;
    loadCardPage();
}

// Filter character cards using backend API
function filterCharacterCards() {
    // 保存当前过滤条件
    currentCharFilters = {
        country: document.getElementById('countryFilter').value,
        element: document.getElementById('elementFilter').value,
        weaponType: document.getElementById('weaponTypeFilter').value,
        search: document.getElementById('characterSearchInput').value
    };
    
    // 重置到第一页
    currentCharPage = 1;
    loadCharacterCardsPage();
}

// Search cards by name (just calls filterCards)
function searchCards() {
    // 更新搜索条件
    currentCardFilters.search = document.getElementById('searchInput').value;
    
    // 重置到第一页
    currentCardPage = 1;
    loadCardPage();
}

// Search character cards by name (just calls filterCharacterCards)
function searchCharacterCards() {
    // 更新搜索条件
    currentCharFilters.search = document.getElementById('characterSearchInput').value;
    
    // 重置到第一页
    currentCharPage = 1;
    loadCharacterCardsPage();
}

// Function to populate tag buttons
function populateTagCheckboxes() {
    const url = '/api/cards/tags';
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
            const container = document.getElementById('tagButtonsContainer');
            container.innerHTML = '';  // Clear existing buttons
            
            // Add individual tag buttons
            data.tags.forEach(tag => {
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'tag-btn';
                button.textContent = tag;
                button.onclick = function() {
                    toggleTagButton(this, tag);
                    filterCards(); // Auto-apply filter when tag button is clicked
                };
                button.id = `tagbtn_${tag}`;
                container.appendChild(button);
            });
        })
        .catch(error => {
            console.error('Error loading tags for buttons:', error);
            // Fallback to some common tags
            const container = document.getElementById('tagButtonsContainer');
            container.innerHTML = '';
            
            const commonTags = ['事件牌', '装备牌', '支援牌', '元素共鸣', '武器', '圣遗物', '天赋', '特技', '秘传', '伙伴', '料理', '道具', '场地'];
            commonTags.forEach(tag => {
                const button = document.createElement('button');
                button.type = 'button';
                button.className = 'tag-btn';
                button.textContent = tag;
                button.onclick = function() {
                    toggleTagButton(this, tag);
                    filterCards(); // Auto-apply filter when tag button is clicked
                };
                button.id = `tagbtn_${tag}`;
                container.appendChild(button);
            });
        });
}

// Toggle tag button selection
function toggleTagButton(button, tag) {
    button.classList.toggle('tag-btn-selected');
}

// Quick search functions
function quickSearch(keyword) {
    // Clear all selected tag buttons
    const tagButtons = document.querySelectorAll('#tagButtonsContainer .tag-btn-selected');
    tagButtons.forEach(button => {
        button.classList.remove('tag-btn-selected');
    });
    
    // Update the search input and trigger search
    const searchInput = document.getElementById('searchInput');
    searchInput.value = keyword;
    searchCards();
}

// Scroll to bottom function
function scrollToBottom() {
    const validationSection = document.querySelector('.section:last-child');
    if (validationSection) {
        validationSection.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// 随机选择角色功能
function selectRandomCharacter(count = 1) {
    const countryFilter = document.getElementById('countryFilter').value;
    const elementFilter = document.getElementById('elementFilter').value;
    const weaponTypeFilter = document.getElementById('weaponTypeFilter').value;
    
    // 构建查询参数（始终使用当前过滤条件）
    const params = new URLSearchParams();
    params.append('type', '角色牌');
    params.append('count', count.toString());
    
    if (countryFilter) params.append('country', countryFilter);
    if (elementFilter) params.append('element', elementFilter);
    if (weaponTypeFilter) params.append('weapon_type', weaponTypeFilter);
    
    const url = `/api/cards/random?${params.toString()}`;
    const token = getJWTToken();
    const headers = token ? { 
        'Authorization': 'Bearer ' + token 
    } : {};
    
    // 调用后端API获取随机角色
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
            if (data.cards && data.cards.length > 0) {
                // 对每个随机角色进行处理
                data.cards.forEach(randomCard => {
                    // 检查角色是否已选
                    if (!deck.characters.some(c => c.id === randomCard.id)) {
                        // 如果还有空位，添加角色；否则替换一个已选角色
                        if (deck.characters.length < 3) {
                            // 查找对应的DOM元素并触发选择
                            const cardElements = document.querySelectorAll('#characterCardSelection .card-item');
                            for (const element of cardElements) {
                                if (element.getAttribute('data-card-id') === randomCard.id) {
                                    toggleCharacterSelection(randomCard, element);
                                    break;
                                }
                            }
                        } else {
                            // 如果满了，先移除一个角色再添加新的
                            if (deck.characters.length > 0) {
                                const randomIndex = Math.floor(Math.random() * deck.characters.length);
                                const characterToRemove = deck.characters[randomIndex];
                                
                                // 从DOM中查找对应元素并移除
                                const cardElements = document.querySelectorAll('#characterCardSelection .card-item');
                                for (const element of cardElements) {
                                    if (element.getAttribute('data-card-id') === characterToRemove.id) {
                                        toggleCharacterSelection(characterToRemove, element);
                                        break;
                                    }
                                }
                                
                                // 添加新的随机角色
                                for (const element of cardElements) {
                                    if (element.getAttribute('data-card-id') === randomCard.id) {
                                        toggleCharacterSelection(randomCard, element);
                                        break;
                                    }
                                }
                            }
                        }
                    }
                });
            } else {
                alert('没有符合条件的随机角色可选择');
            }
        })
        .catch(error => {
            console.error('Error selecting random character:', error);
            alert('随机选择角色失败，请重试');
        });
}

// 随机选择行动牌功能
function selectRandomCard(count = 1) {
    const searchTerm = document.getElementById('searchInput').value;
    const costFilter = document.getElementById('costFilter').value;
    
    // Get selected tags from buttons
    const selectedTags = getSelectedTags();
    
    // 构建查询参数（始终使用当前过滤条件）
    const params = new URLSearchParams();
    params.append('type', '非角色牌');
    params.append('count', count.toString());
    
    if (costFilter) params.append('cost', costFilter);
    if (searchTerm) params.append('search', searchTerm);
    
    // Add tags as separate parameters
    selectedTags.forEach(tag => {
        params.append('tag', tag);
    });
    
    const url = `/api/cards/random?${params.toString()}`;
    const token = getJWTToken();
    const headers = token ? { 
        'Authorization': 'Bearer ' + token 
    } : {};
    
    // 调用后端API获取随机卡牌
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
            if (data.cards && data.cards.length > 0) {
                // 对每个随机卡牌进行处理
                data.cards.forEach(randomCard => {
                    // 计算该卡牌当前已选择的数量
                    const currentCount = deck.cards.filter(c => c.id === randomCard.id).length;
                    
                    // 如果还有空间，添加卡牌；否则替换一个已选卡牌
                    if (deck.cards.length < 30 && currentCount < 2) {
                        // 查找对应的DOM元素并触发选择
                        const cardElements = document.querySelectorAll('#cardSelection .card-item');
                        for (const element of cardElements) {
                            if (element.getAttribute('data-card-id') === randomCard.id) {
                                toggleCardSelection(randomCard, element);
                                break;
                            }
                        }
                    } else if (deck.cards.length >= 30) {
                        // 如果满了，先移除一个卡牌再添加新的
                        if (deck.cards.length > 0) {
                            // 随机选择一个卡牌ID来移除
                            const uniqueCardIds = [...new Set(deck.cards.map(card => card.id))];
                            const randomIndex = Math.floor(Math.random() * uniqueCardIds.length);
                            const cardIdToRemove = uniqueCardIds[randomIndex];
                            
                            // 从DOM中找到对应元素并移除（移除最多2张）
                            const cardElements = document.querySelectorAll('#cardSelection .card-item');
                            for (const element of cardElements) {
                                if (element.getAttribute('data-card-id') === cardIdToRemove) {
                                    // 先尝试移除2张，如果只选择了1张就移除1张
                                    const currentCount = deck.cards.filter(c => c.id === cardIdToRemove).length;
                                    if (currentCount > 0) {
                                        toggleCardSelection(deck.cards.find(c => c.id === cardIdToRemove), element);
                                    }
                                    if (currentCount > 1) {
                                        toggleCardSelection(deck.cards.find(c => c.id === cardIdToRemove), element);
                                    }
                                    break;
                                }
                            }
                            
                            // 添加新的随机卡牌
                            for (const element of cardElements) {
                                if (element.getAttribute('data-card-id') === randomCard.id) {
                                    const newCurrentCount = deck.cards.filter(c => c.id === randomCard.id).length;
                                    if (newCurrentCount < 2) {
                                        toggleCardSelection(randomCard, element);
                                    }
                                    break;
                                }
                            }
                        }
                    }
                });
            } else {
                alert('没有符合条件的随机卡牌可选择');
            }
        })
        .catch(error => {
            console.error('Error selecting random card:', error);
            alert('随机选择行动牌失败，请重试');
        });
}