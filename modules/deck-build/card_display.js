// 显示卡牌的模块
// Display character cards in the selection area with expanded details
function displayCharacterCards(cards) {
    const container = document.getElementById('characterCardSelection');
    container.innerHTML = '';
    
    // Sort cards to show selected ones first
    const sortedCards = [...cards].sort((a, b) => {
        const aSelected = deck.characters.some(c => c.id === a.id) ? 1 : 0;
        const bSelected = deck.characters.some(c => c.id === b.id) ? 1 : 0;
        return bSelected - aSelected; // Selected cards first
    });
    
    sortedCards.forEach(card => {
        const cardItem = document.createElement('div');
        cardItem.className = 'card-item expanded-character';
        cardItem.setAttribute('data-card-id', card.id);
        cardItem.setAttribute('data-card-type', card.type);
        
        // Determine display name based on card type
        let displayName = card.name;
        if (card.title && card.title !== card.name) {
            displayName += ' (' + card.title + ')';
        }
        
        // Format additional info for character cards
        const countryInfo = card.country ? `国家: ${card.country}` : '国家: 未知';
        const elementInfo = card.element ? `元素: ${card.element}` : '元素: 未知';
        const weaponInfo = card.weapon_type ? `武器: ${card.weapon_type}` : '武器: 未知';
        
        // Format skill info
        let skillsInfo = '';
        if (card.skills && Array.isArray(card.skills) && card.skills.length > 0) {
            skillsInfo += '<div class="skills-section"><strong>技能:</strong><ul>';
            card.skills.forEach(skill => {
                const skillType = skill.type || '未知';
                const skillName = skill.name || '未知技能';
                const skillDesc = skill.description || '无描述';
                const skillCost = formatCostDisplay(skill.cost || []);
                skillsInfo += `<li><strong>${skillName}</strong> (${skillType}) | 费用: ${skillCost}<br>${skillDesc}</li>`;
            });
            skillsInfo += '</ul></div>';
        } else {
            skillsInfo = '<div class="skills-section"><strong>技能:</strong> 无技能信息</div>';
        }
        
        // 获取当前选择计数
        const currentCount = deck.characters.some(c => c.id === card.id) ? 1 : 0;
        
        cardItem.innerHTML = `
            <div class="character-header">
                <div><strong class="character-name">${displayName}</strong></div>
                <div class="character-info">${countryInfo} | ${elementInfo} | ${weaponInfo}</div>
            </div>
            <div class="character-details">
                <div>类型: ${card.type || '未知'}</div>
                ${skillsInfo}
            </div>
            <div class="card-count">已选: <span>${currentCount}</span></div>
        `;
        
        cardItem.addEventListener('click', function() {
            toggleCharacterSelection(card, this);
        });
        container.appendChild(cardItem);
    });
}

// Display other cards in the selection area
function displayCards(cards) {
    const container = document.getElementById('cardSelection');
    container.innerHTML = '';
    
    // Sort cards to show selected ones first
    const sortedCards = [...cards].sort((a, b) => {
        const aCount = deck.cards.filter(c => c.id === a.id).length;
        const bCount = deck.cards.filter(c => c.id === b.id).length;
        return bCount - aCount; // Selected cards first
    });
    
    sortedCards.forEach(card => {
        const cardItem = document.createElement('div');
        cardItem.className = 'card-item';
        cardItem.setAttribute('data-card-id', card.id);
        cardItem.setAttribute('data-card-type', card.type);
        
        // Determine display name based on card type
        let displayName = card.name;
        if (card.title && card.title !== card.name) {
            displayName += ' (' + card.title + ')';
        }
        
        // Format additional info for other cards
        // Use the data structure from loadCards function
        const typeInfo = card.type ? `类型: ${card.type}` : '类型: 未知';
        const costInfo = card.cost && card.cost.length > 0 ? `费用: ${formatCostDisplay(card.cost)}` : '费用: N/A';
        const descriptionInfo = card.description ? card.description : '无描述';
        
        // 获取当前选择计数
        const currentCount = deck.cards.filter(c => c.id === card.id).length;
        
        cardItem.innerHTML = `
            <div><strong>${displayName}</strong></div>
            <div class="card-type-info">${typeInfo} | ${costInfo}</div>
            <div class="card-description">${descriptionInfo}</div>
            <div class="card-count">已选: <span>${currentCount}</span></div>
        `;
        
        cardItem.addEventListener('click', function() {
            toggleCardSelection(card, this);
        });
        container.appendChild(cardItem);
    });
}