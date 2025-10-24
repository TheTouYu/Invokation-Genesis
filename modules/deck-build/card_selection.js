// 卡片选择逻辑的模块
// Toggle character selection in the deck
function toggleCharacterSelection(card, element) {
    const cardId = card.id;

    // 角色牌：点击选择，再次点击取消（每种角色只能选1张）
    const existingIndex = deck.characters.findIndex(c => c.id === cardId);

    if (existingIndex === -1) {
        // 角色不在卡组中，尝试添加
        if (deck.characters.length >= 3) {
            alert('角色牌最多只能选择3张不同角色！');
            return;
        }
        
        deck.characters.push({...card});
        element.classList.add('selected');
        
        const countSpan = element.querySelector('.card-count span');
        if (countSpan) {
            countSpan.textContent = 1;
        }
    } else {
        // 角色已在卡组中，移除它
        deck.characters.splice(existingIndex, 1);
        element.classList.remove('selected');
        
        const countSpan = element.querySelector('.card-count span');
        if (countSpan) {
            countSpan.textContent = 0;
        }
    }
    
    // 实时更新UI
    updateDeckDisplay();
    updateCharacterCardCounts();
    
    // 仅重新渲染当前标签页的卡片，保持当前的过滤条件
    if (currentTab === 'character') {
        // 保留当前的过滤条件
        const countryFilter = document.getElementById('countryFilter').value;
        const elementFilter = document.getElementById('elementFilter').value;
        const weaponTypeFilter = document.getElementById('weaponTypeFilter').value;
        const searchTerm = document.getElementById('characterSearchInput').value;
        
        // 重新应用过滤条件来保持显示的一致性
        const params = new URLSearchParams();
        params.append('type', '角色牌');
        params.append('page', '1');
        params.append('per_page', '12');
        if (countryFilter) params.append('country', countryFilter);
        if (elementFilter) params.append('element', elementFilter);
        if (weaponTypeFilter) params.append('weapon_type', weaponTypeFilter);
        if (searchTerm) params.append('search', searchTerm);
        
        const url = `/api/cards/filter?${params.toString()}`;
        const headers = needsAuth(url) ? { 
            'Authorization': 'Bearer ' + (getJWTToken() || '') 
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
                displayCharacterCards(data.cards);
            })
            .catch(() => {
                // 备用方法：重新显示所有角色卡，但保持已选择的卡牌高亮
                displayCharacterCards(allCharacterCards);
            });
    }
}

// Toggle card selection in the deck (for non-character cards)
function toggleCardSelection(card, element) {
    const cardId = card.id;
    const cardType = card.type;

    // 行动牌：第1次点击选1张，第2次点击选2张，第3次点击取消选择（回到0张）
    const currentCount = deck.cards.filter(c => c.id === cardId).length;

    if (currentCount === 0) {
        // 添加第1张
        if (deck.cards.length >= 30) {
            alert('行动牌已达到30张的上限！');
            return;
        }
        deck.cards.push({...card});
        
        element.classList.add('selected');
        const countSpan = element.querySelector('.card-count span');
        if (countSpan) {
            countSpan.textContent = 1;
        }
    } else if (currentCount === 1) {
        // 添加第2张
        if (deck.cards.length >= 30) {
            alert('行动牌已达到30张的上限！');
            return;
        }
        deck.cards.push({...card});
        
        const countSpan = element.querySelector('.card-count span');
        if (countSpan) {
            countSpan.textContent = 2;
        }
    } else {
        // 移除所有该卡牌（第3次点击，取消选择）
        deck.cards = deck.cards.filter(c => c.id !== cardId);
        
        element.classList.remove('selected');
        const countSpan = element.querySelector('.card-count span');
        if (countSpan) {
            countSpan.textContent = 0;
        }
    }
    
    // 实时更新UI
    updateDeckDisplay();
    updateCardCounts();
    
    // 仅重新渲染当前标签页的卡片，保持当前的过滤条件
    if (currentTab === 'other') {
        // 保留当前的过滤条件
        const searchTerm = document.getElementById('searchInput').value;
        const costFilter = document.getElementById('costFilter').value;
        
        // 获取选中的标签
        const selectedTags = getSelectedTags();
        
        // 重新应用过滤条件以保持显示的一致性
        const params = new URLSearchParams();
        params.append('type', '非角色牌');
        params.append('page', '1');
        params.append('per_page', '30');
        if (costFilter) params.append('cost', costFilter);
        if (searchTerm) params.append('search', searchTerm);
        
        // 添加标签参数
        selectedTags.forEach(tag => {
            params.append('tag', tag);
        });
        
        const url = `/api/cards/filter?${params.toString()}`;
        const headers = needsAuth(url) ? { 
            'Authorization': 'Bearer ' + (getJWTToken() || '') 
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
                displayCards(data.cards);
            })
            .catch(() => {
                // 备用方法：重新显示所有行动卡，但保持已选择的卡牌高亮
                displayCards(allCards);
            });
    }
}

// Update count displays for all cards
function updateCardCounts() {
    const allCards = document.querySelectorAll('#cardSelection .card-item');
    allCards.forEach(item => {
        const cardId = item.getAttribute('data-card-id');
        
        // For non-character cards, check how many are selected
        const count = deck.cards.filter(c => c.id === cardId).length;
        
        const countSpan = item.querySelector('.card-count span');
        if (countSpan) {
            countSpan.textContent = count;
        }
    });
}

// Update count displays for character cards
function updateCharacterCardCounts() {
    const allCharacterCards = document.querySelectorAll('#characterCardSelection .card-item');
    allCharacterCards.forEach(item => {
        const cardId = item.getAttribute('data-card-id');
        
        // For character cards, check if selected
        const count = deck.characters.filter(c => c.id === cardId).length;
        
        const countSpan = item.querySelector('.card-count span');
        if (countSpan) {
            countSpan.textContent = count;
        }
    });
}