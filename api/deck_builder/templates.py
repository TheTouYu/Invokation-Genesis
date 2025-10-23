DECK_BUILDER_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>七圣召唤 - 卡组构建器</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
            margin: 0;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.12);
            padding: 25px;
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 25px;
            font-size: 2.2em;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        }
        .section {
            background: #f8fafc;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
        }
        h3 {
            color: #34495e;
            margin-top: 0;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .card-item {
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            min-width: 200px;
        }
        .card-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-color: #3498db;
        }
        .card-item.selected {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            border-color: #2980b9;
        }
        .card-item.selected .card-count {
            color: white;
        }
        .card-item.selected .card-details {
            color: #e8f4fc;
        }
        .deck-preview {
            background: #e8f5e8;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 20px;
        }
        .validation-result {
            border-radius: 8px;
            padding: 20px;
        }
        .valid {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }
        .invalid {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        button {
            padding: 12px 20px;
            margin: 5px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        .validate-btn {
            background: linear-gradient(135deg, #28a745 0%, #218838 100%);
            color: white;
        }
        .reset-btn {
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
        }
        .random-btn {
            background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
            color: white;
        }
        input, select {
            padding: 10px;
            border: 1px solid #cbd5e0;
            border-radius: 4px;
            font-size: 14px;
        }
        .deck-info-section {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border: 1px solid #90caf9;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            margin-top: 15px;
            background: linear-gradient(135deg, #e3f9ff 0%, #d1ecff 100%);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #7abaff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .error {
            color: #e74c3c;
            font-weight: bold;
        }
        .success {
            color: #27ae60;
            font-weight: bold;
        }
        .tabs {
            display: flex;
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-radius: 8px 8px 0 0;
            overflow: hidden;
            margin-bottom: -1px;
        }
        .tab {
            padding: 15px 25px;
            cursor: pointer;
            background: rgba(227, 242, 253, 0.7);
            border-right: 1px solid #bbdefb;
            font-weight: 600;
            color: #1976d2;
            transition: all 0.3s ease;
            flex: 1;
            text-align: center;
        }
        .tab:last-child {
            border-right: none;
        }
        .tab:hover {
            background: linear-gradient(135deg, #64b5f6 0%, #2196f3 100%);
            color: white;
            transform: translateY(-2px);
        }
        .tab.active {
            background: linear-gradient(135deg, white 0%, #f0f8ff 100%);
            color: #1565c0;
            border-bottom: 4px solid #2196f3;
        }
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .character-filters {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 20px;
            border-radius: 10px;
            margin: 15px 0;
            border: 1px solid #dee2e6;
            box-shadow: 0 3px 10px rgba(0,0,0,0.08);
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: end;
        }
        .filter-group {
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 5px;
            min-width: 140px;
        }
        .filter-group label {
            font-weight: 600;
            color: #2c3e50;
            font-size: 0.9em;
        }
        .filter-group select, .filter-group input {
            min-width: 140px;
            padding: 8px 10px;
            border-radius: 6px;
            border: 1px solid #bdc3c7;
            background-color: white;
            font-size: 14px;
            box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);
        }
        .filter-group select:focus, .filter-group input:focus {
            outline: none;
            border-color: #3498db;
            box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
        }
        .filter-group button {
            margin: 2px !important;
            margin-top: 5px !important;
            padding: 8px 12px !important;
            min-width: auto;
        }
        
        /* 卡牌选择区域 */
        .card-selection {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
            gap: 14px;
            margin-top: 15px;
        }
        
        /* 随机按钮样式 */
        .random-btn {
            background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
            color: white;
        }
        
        .random-btn:hover {
            background: linear-gradient(135deg, #e67e22 0%, #d35400 100%);
        }
        
        /* 其他卡牌UI美化 */
        .card-type-info {
            font-size: 0.9em;
            color: #e74c3c;
            font-weight: bold;
            margin: 4px 0;
        }
        .card-description {
            font-size: 0.82em;
            color: #7f8c8d;
            margin: 6px 0;
            line-height: 1.4;
            min-height: 32px;
        }
        
        /* 标签按钮样式 */
        .tag-btn {
            display: inline-block;
            background: linear-gradient(135deg, #bdc3c7 0%, #95a5a6 100%);
            color: #2c3e50;
            border: none;
            border-radius: 15px;
            padding: 6px 14px;
            margin: 4px;
            cursor: pointer;
            font-size: 0.82em;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .tag-btn:hover {
            background: linear-gradient(135deg, #a0a7ae 0%, #7f8c8c 100%);
            transform: translateY(-1px);
        }
        
        .tag-btn-selected {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
        }
        
        .tag-btn-selected:hover {
            background: linear-gradient(135deg, #2980b9 0%, #1c6ea4 100%);
        }
        
        /* 扩展角色卡样式 */
        .expanded-character {
            min-height: 190px;
            display: flex;
            flex-direction: column;
            transition: all 0.2s ease;
        }
        
        .character-header {
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 10px;
        }
        
        .character-name {
            font-size: 1.25em;
            color: #e67e22;
            font-weight: bold;
        }
        
        .character-info {
            font-size: 0.95em;
            color: #7f8c8d;
            margin-top: 5px;
        }
        
        .character-details {
            flex-grow: 1;
            overflow-y: auto;
            max-height: 130px;
        }
        
        .skills-section {
            margin-top: 8px;
        }
        
        .skills-section ul {
            margin: 5px 0;
            padding-left: 20px;
        }
        
        .skills-section li {
            margin-bottom: 8px;
            font-size: 0.85em;
            line-height: 1.35;
        }
        
        /* 快速搜索按钮样式 */
        .quick-search-btn {
            background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
            color: white;
            border: none;
            border-radius: 5px;
            padding: 6px 12px;
            margin: 4px;
            cursor: pointer;
            font-size: 0.82em;
        }
        
        .quick-search-btn:hover {
            background: linear-gradient(135deg, #8e44ad 0%, #7d3c98 100%);
            transform: translateY(-1px);
        }
        
        /* 卡牌选择区域 */
        .card-selection {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
            gap: 14px;
            margin-top: 15px;
        }
        
        /* 随机按钮样式 */
        .random-btn {
            background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
            color: white;
        }
        
        .random-btn:hover {
            background: linear-gradient(135deg, #e67e22 0%, #d35400 100%);
        }
        
        /* 分页按钮样式 */
        .pagination button {
            background: linear-gradient(135deg, #7f8c8d 0%, #95a5a6 100%);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 15px;
            margin: 0 5px;
            cursor: pointer;
            font-weight: bold;
        }
        
        .pagination button:hover {
            background: linear-gradient(135deg, #95a5a6 0%, #bdc3c7 100%);
            transform: translateY(-1px);
        }
        
        .pagination button:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
            opacity: 0.6;
        }
        
        .pagination span {
            font-weight: bold;
            color: #2c3e50;
            margin: 0 15px;
            vertical-align: middle;
        }
        
        /* Login section styles */
        #loginForm {
            display: flex;
            gap: 10px;
            align-items: center;
            margin-bottom: 10px;
        }
        
        #loginForm input {
            padding: 8px;
            border: 1px solid #cbd5e0;
            border-radius: 4px;
            font-size: 14px;
        }
        
        #loginForm button, #userInfo button {
            padding: 8px 15px;
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        
        #userInfo {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        #loginStatus {
            margin-top: 10px;
        }
        
        .success-message {
            color: #27ae60;
            font-weight: bold;
        }
        
        .error-message {
            color: #e74c3c;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>七圣召唤 - 卡组构建器</h1>
        
        <!-- Login Section -->
        <div class="section" id="loginSection">
            <h3>用户认证</h3>
            <div id="loginForm">
                <label>用户名: <input type="text" id="usernameInput" value="test"></label>
                <label>密码: <input type="password" id="passwordInput" value="test"></label>
                <button onclick="loginUser()">登录</button>
            </div>
            <div id="userInfo" style="display:none;">
                <p>已登录: <span id="currentUsername"></span> | 
                <button onclick="logoutUser()">登出</button></p>
            </div>
            <div id="loginStatus"></div>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="switchTab('character')">角色选择</div>
            <div class="tab" onclick="switchTab('other')">行动牌</div>
        </div>
        
        <div id="characterTab" class="tab-content active">
            <div class="section">
                <h3>角色选择</h3>
                <div>
                    <label>搜索角色: <input type="text" id="characterSearchInput" placeholder="输入角色名称..." onkeyup="searchCharacterCards()"></label>
                    <div class="character-filters">
                        <div class="filter-group">
                            <label>国家:</label>
                            <select id="countryFilter" onchange="filterCharacterCards()">
                                <option value="">全部国家</option>
                            </select>
                        </div>
                        <div class="filter-group">
                            <label>元素:</label>
                            <select id="elementFilter" onchange="filterCharacterCards()">
                                <option value="">全部元素</option>
                            </select>
                        </div>
                        <div class="filter-group">
                            <label>武器类型:</label>
                            <select id="weaponTypeFilter" onchange="filterCharacterCards()">
                                <option value="">全部武器</option>
                            </select>
                        </div>
                        <button class="random-btn" onclick="selectRandomCharacter()">随机选择角色</button>
                        <button class="random-btn" onclick="selectRandomCharacter(3)">随机选择3个角色</button>
                    </div>
                </div>
                <div id="characterCardSelection" class="card-selection">
                    <!-- 角色卡牌将在这里显示 -->
                </div>
                <div id="characterPagination" class="pagination" style="text-align: center; margin-top: 20px; display: none;">
                    <button onclick="changeCharacterPage(-1)">上一页</button>
                    <span id="characterPageInfo"></span>
                    <button onclick="changeCharacterPage(1)">下一页</button>
                </div>
            </div>
        </div>
        
        <div id="otherTab" class="tab-content">
            <div class="section">
                <h3>行动牌选择</h3>
                <div>
                    <label>搜索卡牌: <input type="text" id="searchInput" placeholder="输入卡牌名称..." onkeyup="searchCards()"></label>
                    <label>费用: 
                        <select id="costFilter" onchange="filterCards()">
                            <option value="">全部费用</option>
                            <option value="0">0</option>
                            <option value="1">1</option>
                            <option value="2">2</option>
                            <option value="3">3</option>
                            <option value="other">其他</option>
                        </select>
                    </label>
                    <label>特殊标签: 
                        <div id="tagButtonsContainer" style="display: inline-block;">
                            <!-- 标签按钮将由JavaScript动态生成 -->
                        </div>
                    </label>
                    <!-- 添加默认搜索按钮 -->
                    <div style="margin-top: 10px;">
                        <button type="button" onclick="quickSearch('充能')" class="quick-search-btn">充能</button>
                        <button type="button" onclick="quickSearch('天赋')" class="quick-search-btn">天赋</button>
                        <button type="button" onclick="quickSearch('舍弃')" class="quick-search-btn">舍弃</button>
                        <button type="button" onclick="quickSearch('夜魂值')" class="quick-search-btn">夜魂值</button>
                        <button type="button" onclick="quickSearch('手牌')" class="quick-search-btn">手牌</button>
                    </div>
                    <div style="margin-top: 10px;">
                        <button class="random-btn" onclick="selectRandomCard()">随机选择行动牌</button>
                        <button class="random-btn" onclick="selectRandomCard(30)">随机选择30张行动牌</button>
                    </div>
                </div>
                <div id="cardSelection" class="card-selection">
                    <!-- Cards will be populated here -->
                </div>
                <div id="cardPagination" class="pagination" style="text-align: center; margin-top: 20px; display: none;">
                    <button onclick="changeCardPage(-1)">上一页</button>
                    <span id="cardPageInfo"></span>
                    <button onclick="changeCardPage(1)">下一页</button>
                </div>
            </div>
        </div>
        
        <!-- 卡组信息显示在顶部 -->
        <div class="section deck-info-section">
            <h3>卡组信息</h3>
            <div class="stats">
                <div>角色牌: <span id="charCount">0</span>/3 (每个角色限1张)</div>
                <div>行动牌: <span id="actionCount">0</span>/30 (每个行动牌限2张)</div>
                <div>卡组总数: <span id="totalCount">0</span>/30 (不含角色牌)</div>
            </div>
            <div id="deckPreview" class="deck-preview">
                <p>当前卡组内容:</p>
                <div id="currentDeck">暂无卡牌</div>
            </div>
            
            <div class="controls">
                <button class="validate-btn" onclick="validateDeck()">验证卡组</button>
                <button class="reset-btn" onclick="resetDeck()">重置卡组</button>
                <button class="random-btn" onclick="scrollToBottom()">滑到底部</button>
            </div>
        </div>
        
        <div class="section">
            <h3>验证结果</h3>
            <div id="validationResult" class="validation-result">
                选择卡牌并点击"验证卡组"来检查卡组是否符合规则。
            </div>
        </div>
    </div>

    <script>
        // Deck data structure
        let deck = {
            characters: [],
            cards: []
        };
        
        // Available cards
        let allCards = [];
        let allCharacterCards = []; // 单独存储角色卡牌
        
        // Page state
        let currentTab = 'character';
        
        // Initialize the page
        document.addEventListener('DOMContentLoaded', function() {
            loadCards(); // Load cards from API
            loadCharacterFilters(); // Load character filter options
            populateTagCheckboxes(); // Initialize tag buttons for other cards
        });
        
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
        
        // Load all cards from backend
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
        
        // Filter cards using backend API
        function filterCards() {
            const searchTerm = document.getElementById('searchInput').value;
            const costFilter = document.getElementById('costFilter').value;
            
            // Get selected tags from buttons
            const selectedTags = getSelectedTags();
            
            // Build query parameters
            const params = new URLSearchParams();
            params.append('type', '非角色牌');  // Only filter non-character cards
            params.append('page', '1');
            params.append('per_page', '30');  // 限制每页30张卡牌
            if (costFilter) params.append('cost', costFilter);
            if (searchTerm) params.append('search', searchTerm);
            
            // Add tags as separate parameters
            selectedTags.forEach(tag => {
                params.append('tag', tag);
            });
            
            // Get token and set headers
            const token = getJWTToken();
            const headers = token ? { 
                'Authorization': 'Bearer ' + token 
            } : {};
            
            // Call backend API to filter cards
            fetch(`/api/cards/filter?${params.toString()}`, {
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
                .catch(error => {
                    console.error('Error filtering cards:', error);
                    // Fallback to showing all cards if API fails
                    displayCards(allCards);
                });
        }
        
        // Filter character cards using backend API
        function filterCharacterCards() {
            const searchTerm = document.getElementById('characterSearchInput').value;
            const countryFilter = document.getElementById('countryFilter').value;
            const elementFilter = document.getElementById('elementFilter').value;
            const weaponTypeFilter = document.getElementById('weaponTypeFilter').value;
            
            // Build query parameters
            const params = new URLSearchParams();
            params.append('type', '角色牌');  // Only filter character cards
            params.append('page', '1');
            params.append('per_page', '12');  // 限制每页12张角色卡
            if (countryFilter) params.append('country', countryFilter);
            if (elementFilter) params.append('element', elementFilter);
            if (weaponTypeFilter) params.append('weapon_type', weaponTypeFilter);
            if (searchTerm) params.append('search', searchTerm);
            
            // Get token and set headers
            const token = getJWTToken();
            const headers = token ? { 
                'Authorization': 'Bearer ' + token 
            } : {};
            
            // Call backend API to filter character cards
            fetch(`/api/cards/filter?${params.toString()}`, {
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
                .catch(error => {
                    console.error('Error filtering character cards:', error);
                    // Fallback to showing all character cards if API fails
                    displayCharacterCards(allCharacterCards);
                });
        }
        
        // Search cards by name (just calls filterCards)
        function searchCards() {
            filterCards();
        }
        
        // Search character cards by name (just calls filterCharacterCards)
        function searchCharacterCards() {
            filterCharacterCards();
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
        
        // Get all selected tags
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
        
        // 分页相关状态
        let currentCharPage = 1;
        let totalCharPages = 1;
        let currentCardPage = 1;
        let totalCardPages = 1;
        
        // 分页相关的过滤参数
        let currentCharFilters = { country: '', element: '', weaponType: '', search: '' };
        let currentCardFilters = { cost: '', search: '', tags: [] };
        
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
                    updateCharacterPagination(data.total, data.pages, data.current_page);
                })
                .catch(error => {
                    console.error('Error loading character cards page:', error);
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
                    updateCardPagination(data.total, data.pages, data.current_page);
                })
                .catch(error => {
                    console.error('Error loading card page:', error);
                });
        }
        
        // 更新角色卡分页信息
        function updateCharacterPagination(total, totalPages, currentPage) {
            totalCharPages = totalPages;
            currentCharPage = currentPage;
            
            const pageInfo = document.getElementById('characterPageInfo');
            pageInfo.textContent = `第 ${currentPage} 页，共 ${totalPages} 页 (共 ${total} 张)`;
            
            const prevButton = document.querySelector('#characterPagination button:first-child');
            const nextButton = document.querySelector('#characterPagination button:last-child');
            
            prevButton.disabled = currentPage <= 1;
            nextButton.disabled = currentPage >= totalPages;
            
            document.getElementById('characterPagination').style.display = totalPages > 1 ? 'block' : 'none';
        }
        
        // 更新行动牌分页信息
        function updateCardPagination(total, totalPages, currentPage) {
            totalCardPages = totalPages;
            currentCardPage = currentPage;
            
            const pageInfo = document.getElementById('cardPageInfo');
            pageInfo.textContent = `第 ${currentPage} 页，共 ${totalPages} 页 (共 ${total} 张)`;
            
            const prevButton = document.querySelector('#cardPagination button:first-child');
            const nextButton = document.querySelector('#cardPagination button:last-child');
            
            prevButton.disabled = currentPage <= 1;
            nextButton.disabled = currentPage >= totalPages;
            
            document.getElementById('cardPagination').style.display = totalPages > 1 ? 'block' : 'none';
        }
        
        // 重写过滤和搜索函数以支持分页
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
        
        function searchCharacterCards() {
            // 更新搜索条件
            currentCharFilters.search = document.getElementById('characterSearchInput').value;
            
            // 重置到第一页
            currentCharPage = 1;
            loadCharacterCardsPage();
        }
        
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
        
        function searchCards() {
            // 更新搜索条件
            currentCardFilters.search = document.getElementById('searchInput').value;
            
            // 重置到第一页
            currentCardPage = 1;
            loadCardPage();
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
        
        // Check if user is already logged in when page loads
        document.addEventListener('DOMContentLoaded', function() {
            const token = localStorage.getItem('jwt_token');
            if (token) {
                // Check if token is valid by making a simple request
                fetch('/api/auth/profile', {
                    headers: {
                        'Authorization': 'Bearer ' + token
                    }
                })
                .then(response => {
                    if (response.ok) {
                        // Token is valid, update UI
                        document.getElementById('loginForm').style.display = 'none';
                        document.getElementById('userInfo').style.display = 'flex';
                        // We can't get username from token directly, so we'll just show generic text
                        document.getElementById('currentUsername').textContent = '已登录用户';
                    } else {
                        // Token is invalid, remove it
                        localStorage.removeItem('jwt_token');
                    }
                })
                .catch(() => {
                    // Error occurred, remove token
                    localStorage.removeItem('jwt_token');
                });
            }
            
            loadCards(); // Load cards from API
            loadCharacterFilters(); // Load character filter options
            populateTagCheckboxes(); // Initialize tag buttons for other cards
        });
    </script>
</body>
</html>
"""
