// 卡组验证的模块
// Validate the deck against rules
async function validateDeck() {
    const validationResult = document.getElementById('validationResult');
    validationResult.innerHTML = '正在验证卡组...';
    validationResult.className = 'validation-result';
    
    try {
        const url = '/api/deck/validate';
        const token = getJWTToken();
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // Always include token for deck validation in this context
        if (token) {
            headers['Authorization'] = 'Bearer ' + token;
        }
        
        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                characters: deck.characters.map(c => c.id),
                cards: deck.cards.map(c => c.id),
                deck_name: 'Test Deck'
            })
        });
        
        const result = await response.json();
        
        if (result.valid) {
            validationResult.innerHTML = `
                <div class="success">✓ 卡组验证通过！</div>
                <div><strong>规则检查结果:</strong></div>
                <ul>
                    <li>角色数量: ${result.rules.character_count ? '✓' : '✗'} ${result.rules.character_count_msg}</li>
                    <li>卡牌总数: ${result.rules.deck_size ? '✓' : '✗'} ${result.rules.deck_size_msg}</li>
                    <li>角色限制: ${result.rules.character_limit ? '✓' : '✗'} ${result.rules.character_limit_msg}</li>
                    <li>卡牌限制: ${result.rules.card_limit ? '✓' : '✗'} ${result.rules.card_limit_msg}</li>
                    <li>元素反应: ${result.rules.elemental_synergy ? '✓' : '✗'} ${result.rules.elemental_synergy_msg}</li>
                </ul>
                <div><strong>建议:</strong> ${result.suggestions.join(', ') || '无'}</div>
            `;
            validationResult.className = 'validation-result valid';
        } else {
            validationResult.innerHTML = `
                <div class="error">✗ 卡组验证失败！</div>
                <div><strong>错误详情:</strong></div>
                <ul>
                    <li>角色数量: ${result.rules.character_count ? '✓' : '✗'} ${result.rules.character_count_msg}</li>
                    <li>卡牌总数: ${result.rules.deck_size ? '✓' : '✗'} ${result.rules.deck_size_msg}</li>
                    <li>角色限制: ${result.rules.character_limit ? '✓' : '✗'} ${result.rules.character_limit_msg}</li>
                    <li>卡牌限制: ${result.rules.card_limit ? '✓' : '✗'} ${result.rules.card_limit_msg}</li>
                    <li>元素反应: ${result.rules.elemental_synergy ? '✓' : '✗'} ${result.rules.elemental_synergy_msg}</li>
                </ul>
                <div><strong>错误信息:</strong> ${result.errors.join(', ')}</div>
                <div><strong>建议:</strong> ${result.suggestions.join(', ') || '无'}</div>
            `;
            validationResult.className = 'validation-result invalid';
        }
    } catch (error) {
        validationResult.innerHTML = `验证失败: ${error.message}`;
        validationResult.className = 'validation-result invalid';
    }
}