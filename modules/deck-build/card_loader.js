// 加载卡牌数据的模块
function loadCards() {
    // Load cards from our unified API endpoints that use consistent data structure
    // Prepare headers with or without auth based on the endpoint
    const url1 = '/api/cards?type=角色牌&page=1&per_page=12';
    const headers1 = needsAuth(url1) ? { 
        'Authorization': 'Bearer ' + (getJWTToken() || '') 
    } : {};
    
    // First load character cards with pagination info
    fetch(url1, { headers: headers1 })
        .then(response => {
            if (!response.ok) {
                throw new Error('HTTP error ' + response.status);
            }
            return response.json();
        })
        .then(charData => {
            allCharacterCards = charData.cards || [];
            // Initialize pagination info
            totalCharPages = charData.pages || 1;
            currentCharPage = charData.current_page || 1;
            
            // Prepare headers with or without auth based on the endpoint
            const url2 = '/api/cards?type=非角色牌&page=1&per_page=30';
            const headers2 = needsAuth(url2) ? { 
                'Authorization': 'Bearer ' + (getJWTToken() || '') 
            } : {};
            
            // Then load non-character cards with pagination info
            fetch(url2, { headers: headers2 })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('HTTP error ' + response.status);
                    }
                    return response.json();
                })
                .then(otherData => {
                    allCards = otherData.cards || [];
                    // Initialize pagination info
                    totalCardPages = otherData.pages || 1;
                    currentCardPage = otherData.current_page || 1;
                    
                    // If still no cards, use demo cards
                    if (allCards.length === 0 && allCharacterCards.length === 0) {
                        console.log('No cards loaded from API, using demo cards');
                        loadDemoCards();
                    } else {
                        // Display cards based on current tab
                        if (currentTab === 'character') {
                            displayCharacterCards(allCharacterCards);
                            updateCharacterPagination(charData.total, charData.pages, charData.current_page);
                        } else {
                            displayCards(allCards);
                            updateCardPagination(otherData.total, otherData.pages, otherData.current_page);
                        }
                        console.log(`Loaded ${allCharacterCards.length} character cards and ${allCards.length} other cards`);
                    }
                })
                .catch(error => {
                    console.error('Error loading other cards:', error);
                    loadDemoCards();
                });
        })
        .catch(error => {
            console.error('Error loading character cards:', error);
            loadDemoCards();
        });
}

// Load demo cards as fallback
function loadDemoCards() {
    // Demo character cards
    allCharacterCards = [
        {id: 'char_001', name: '迪卢克', title: '角色牌蒙德单手剑', type: '角色牌', country: '蒙德', element: '火', weapon_type: '单手剑', skills: [{name: '逆焰之刃', type: '元素战技', description: '造成2点火元素伤害', cost: [{type: '火', value: 1}]}]},
        {id: 'char_002', name: '凯亚', title: '角色牌蒙德单手剑', type: '角色牌', country: '蒙德', element: '冰', weapon_type: '单手剑', skills: [{name: '霜袭', type: '元素战技', description: '造成1点冰元素伤害', cost: [{type: '冰', value: 1}]}]},
        {id: 'char_003', name: '七七', title: '角色牌璃月双手剑', type: '角色牌', country: '璃月', element: '冰', weapon_type: '双手剑', skills: [{name: '形寒饮冻', type: '元素战技', description: '治疗自身2点，本角色附属冻结', cost: [{type: '冰', value: 1}]}]},
        {id: 'char_004', name: '申鹤', title: '角色牌璃月长柄武器', type: '角色牌', country: '璃月', element: '冰', weapon_type: '长柄武器', skills: [{name: '冰翎', type: '元素战技', description: '造成1点冰元素伤害，召唤「冰翎」', cost: [{type: '冰', value: 1}]}]},
        {id: 'char_005', name: '甘雨', title: '角色牌璃月弓', type: '角色牌', country: '璃月', element: '冰', weapon_type: '弓', skills: [{name: '霜华矢', type: '元素战技', description: '造成2点冰元素伤害', cost: [{type: '冰', value: 1}]}]}
    ];
    
    // Demo other cards
    allCards = [
        {id: 'wp_001', name: '天空之刃', type: '武器牌', cost: [2], description: '单手剑角色装备，提升元素爆发伤害'},
        {id: 'wp_002', name: '祭礼剑', type: '武器牌', cost: [2], description: '单手剑角色装备，重击返还元素骰'},
        {id: 'art_001', name: '赌徒的耳环', type: '圣遗物牌', cost: [1], description: '角色受到伤害后，有几率生成元素骰'},
        {id: 'talent_001', name: '叛逆的守护', type: '天赋牌', cost: [1], description: '迪卢克专属天赋，提升火元素伤害'},
        {id: 'event_001', name: '元素共鸣：热诚之火', type: '事件牌', cost: [0], description: '获得火元素共鸣效果'},
        {id: 'event_002', name: '最好的伙伴！', type: '事件牌', cost: [0], description: '从牌库中抽取2张牌'},
        {id: 'support_001', name: '提米', type: '支援牌', cost: [1], description: '出战角色使用技能后，生成1个万能元素'}
    ];
    
    // Display cards based on current tab
    if (currentTab === 'character') {
        displayCharacterCards(allCharacterCards);
    } else {
        displayCards(allCards);
    }
    console.log('Loaded demo cards as fallback');
}

// Load character filters (country, element, weapon type)
function loadCharacterFilters() {
    const url = '/api/characters/filters';
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
        // Populate country filter
        const countryFilter = document.getElementById('countryFilter');
        data.countries.forEach(country => {
            const option = document.createElement('option');
            option.value = country;
            option.textContent = country;
            countryFilter.appendChild(option);
        });
        
        // Populate element filter
        const elementFilter = document.getElementById('elementFilter');
        data.elements.forEach(element => {
            const option = document.createElement('option');
            option.value = element;
            option.textContent = element;
            elementFilter.appendChild(option);
        });
        
        // Populate weapon type filter
        const weaponTypeFilter = document.getElementById('weaponTypeFilter');
        data.weapon_types.forEach(weapon => {
            const option = document.createElement('option');
            option.value = weapon;
            option.textContent = weapon;
            weaponTypeFilter.appendChild(option);
        });
    })
    .catch(error => {
        console.error('Error loading character filters:', error);
    });
}