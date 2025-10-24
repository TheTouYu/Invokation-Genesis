// 动态加载游戏会话列表
async function loadGameSessions() {
    try {
        // 获取用户参与的游戏历史记录作为游戏会话列表
        const response = await apiRequest('/api/game_sessions', 'GET');

        // 注意：标准实现中可能没有直接获取游戏会话列表的API
        // 这里使用游戏历史记录来模拟，实际需要后端实现相应API
        gameSessions = response.game_sessions || response.games || [];

        // 如果API响应中没有游戏会话数据，使用模拟数据
        if (!gameSessions || gameSessions.length === 0) {
            gameSessions = [
                {id: "game1", name: "游戏会话1"},
                {id: "game2", name: "游戏会话2"},
                {id: "game3", name: "游戏会话3"}
            ];
        }

        const formattedSessions = gameSessions.map(session => ({
            id: session.id || session.game_id,
            name: session.name || session.game_id || `游戏 ${session.id || session.game_id}`
        }));

        // 更新所有游戏相关的选择框
        updateSelectOptions('gameSessionId', formattedSessions, 'id', 'name');
        updateSelectOptions('actionGameSessionId', formattedSessions, 'id', 'name');
        updateSelectOptions('endGameSessionId', formattedSessions, 'id', 'name');
        updateSelectOptions('spectateGameSessionId', formattedSessions, 'id', 'name');

        document.getElementById('authStatus').innerText = '游戏会话列表已刷新';
    } catch (error) {
        console.warn('获取游戏会话列表失败，使用默认选项:', error.message);
        // 使用模拟数据
        gameSessions = [
            {id: "game1", name: "游戏会话1"},
            {id: "game2", name: "游戏会话2"},
            {id: "game3", name: "游戏会话3"}
        ];

        // 更新所有游戏相关的选择框
        updateSelectOptions('gameSessionId', gameSessions, 'id', 'name');
        updateSelectOptions('actionGameSessionId', gameSessions, 'id', 'name');
        updateSelectOptions('endGameSessionId', gameSessions, 'id', 'name');
        updateSelectOptions('spectateGameSessionId', gameSessions, 'id', 'name');

        document.getElementById('authStatus').innerText = '游戏会话列表已加载（使用默认选项）';
    }
}

// 动态加载回放列表
async function loadReplays() {
    try {
        // 获取回放列表
        const response = await apiRequest('/api/replays');
        replays = response.replays || [];

        // 更新选择框
        updateSelectOptions('replayId', replays, 'replay_id', 'replay_id');

        document.getElementById('authStatus').innerText = '回放列表已刷新';
    } catch (error) {
        document.getElementById('authStatus').innerText = `加载回放列表时出错: ${error.message}`;
    }
}