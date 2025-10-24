// 动态加载用户列表
async function loadUsers() {
    try {
        // 调用获取用户列表的API
        const response = await apiRequest('/api/users', 'GET');
        
        // 如果API成功返回用户列表
        if (response && response.users) {
            users = response.users;
        } else {
            // 如果API没有返回预期格式的数据，使用默认用户列表
            users = [
                {id: "user1", username: "玩家1"},
                {id: "user2", username: "玩家2"},
                {id: "user3", username: "玩家3"}
            ];
        }

        // 更新选择框
        updateSelectOptions('player2Id', users, 'id', 'username');

        document.getElementById('authStatus').innerText = '用户列表已刷新';
    } catch (error) {
        console.warn('获取用户列表失败，使用默认选项:', error.message);
        // 使用模拟数据
        users = [
            {id: "user1", username: "玩家1"},
            {id: "user2", username: "玩家2"},
            {id: "user3", username: "玩家3"}
        ];

        // 更新选择框
        updateSelectOptions('player2Id', users, 'id', 'username');

        document.getElementById('authStatus').innerText = '用户列表已加载（使用默认选项）';
    }
}

// 动态加载卡组列表
async function loadUserDecks() {
    try {
        // 调用获取用户卡组列表的API
        const response = await apiRequest('/api/decks', 'GET');
        decks = response.decks || [];

        // 确保卡组数据格式正确
        const formattedDecks = decks.map(deck => ({
            id: deck.id,
            name: deck.name || `卡组 ${deck.id}`
        }));

        // 更新选择框
        updateSelectOptions('deck1Id', formattedDecks, 'id', 'name');
        updateSelectOptions('deck2Id', formattedDecks, 'id', 'name');

        document.getElementById('authStatus').innerText = '卡组列表已刷新';
    } catch (error) {
        console.warn('获取卡组列表失败，使用默认选项:', error.message);
        // 使用模拟数据
        decks = [
            {id: "deck1", name: "卡组1 - 火元素队"},
            {id: "deck2", name: "卡组2 - 水元素队"},
            {id: "deck3", name: "卡组3 - 雷元素队"}
        ];

        // 更新选择框
        updateSelectOptions('deck1Id', decks, 'id', 'name');
        updateSelectOptions('deck2Id', decks, 'id', 'name');

        document.getElementById('authStatus').innerText = '卡组列表已加载（使用默认选项）';
    }
}