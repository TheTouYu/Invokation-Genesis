// 卡组管理的模块
// Update deck display
function updateDeckDisplay() {
    const currentDeckEl = document.getElementById('currentDeck');
    const charCountEl = document.getElementById('charCount');
    const actionCountEl = document.getElementById('actionCount');
    const totalCountEl = document.getElementById('totalCount');
    
    // Clear current display
    currentDeckEl.innerHTML = '';
    
    // Group character cards by ID to show counts (should always be 1 per character)
    const characterCounts = {};
    deck.characters.forEach(char => {
        // In Genshin Impact Card Game, each character can only appear once
        // So we just track unique characters
        if (!characterCounts[char.id]) {
            characterCounts[char.id] = {
                card: char,
                count: 1  // Each character appears only once
            };
        }
    });
    
    // Display character cards first
    if (Object.keys(characterCounts).length > 0) {
        const charSection = document.createElement('div');
        charSection.innerHTML = '<h4>角色牌:</h4>';
        currentDeckEl.appendChild(charSection);
        
        const charList = document.createElement('ul');
        for (const [id, data] of Object.entries(characterCounts)) {
            const li = document.createElement('li');
            li.textContent = `${data.card.name} (${data.card.title || '无称号'}) x${data.count}`;
            charList.appendChild(li);
        }
        currentDeckEl.appendChild(charList);
    }
    
    // Group action cards by ID to show counts
    const cardCounts = {};
    deck.cards.forEach(card => {
        if (cardCounts[card.id]) {
            cardCounts[card.id].count++;
        } else {
            cardCounts[card.id] = {
                card: card,
                count: 1
            };
        }
    });
    
    // Then display action cards
    if (Object.keys(cardCounts).length > 0) {
        const cardSection = document.createElement('div');
        cardSection.innerHTML = '<h4>行动牌:</h4>';
        currentDeckEl.appendChild(cardSection);
        
        const cardList = document.createElement('ul');
        for (const [id, data] of Object.entries(cardCounts)) {
            const li = document.createElement('li');
            li.textContent = `${data.card.name} x${data.count}`;
            cardList.appendChild(li);
        }
        currentDeckEl.appendChild(cardList);
    }
    
    // If no cards in deck
    if (deck.characters.length === 0 && deck.cards.length === 0) {
        currentDeckEl.innerHTML = '<p>暂无卡牌</p>';
    }
    
    // Update stats according to Genshin Impact Card Game rules:
    // - 3 unique character cards (each character max 1)
    // - 30 action cards max
    charCountEl.textContent = `${Object.keys(characterCounts).length}/3`;
    actionCountEl.textContent = `${deck.cards.length}/30`;
    totalCountEl.textContent = `${deck.cards.length}/30`;
    
    // Check if deck is full and trigger auto-validation
    if (Object.keys(characterCounts).length === 3 && deck.cards.length === 30) {
        // Auto-scroll to validation section
        setTimeout(() => {
            const validationSection = document.querySelector('.section:last-child');
            if (validationSection) {
                validationSection.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }
            
            // Auto-validate the deck after scroll
            setTimeout(validateDeck, 600); // Delay slightly to allow scroll to complete
        }, 100); // Small delay to ensure DOM updates
    }
}

// Reset deck
function resetDeck() {
    deck = { characters: [], cards: [] };
    updateDeckDisplay();
    document.querySelectorAll('.card-item.selected').forEach(item => {
        item.classList.remove('selected');
    });
    document.getElementById('validationResult').innerHTML = '选择卡牌并点击"验证卡组"来检查卡组是否符合规则。';
    document.getElementById('validationResult').className = 'validation-result';
}