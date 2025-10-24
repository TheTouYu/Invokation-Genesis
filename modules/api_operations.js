// 创建游戏会话
async function createGameSession() {
    // 尝试从选择框获取值，如果为空则使用文本框
    const player2Id = document.getElementById('player2Id').value || document.getElementById('player2IdText').value;
    const deck1Id = document.getElementById('deck1Id').value || document.getElementById('deck1IdText').value;
    const deck2Id = document.getElementById('deck2Id').value || document.getElementById('deck2IdText').value;
    
    try {
        const response = await apiRequest('/api/game_sessions', 'POST', {
            player2_id: player2Id || undefined,
            deck1_id: deck1Id,
            deck2_id: deck2Id || undefined
        });
        
        document.getElementById('createGameResponse').innerText = JSON.stringify(response, null, 2);
        
        // 刷新游戏会话列表
        loadGameSessions();
    } catch (error) {
        document.getElementById('createGameResponse').innerText = `错误: ${error.message}`;
    }
}

// 获取游戏状态
async function getGameState() {
    // 尝试从选择框获取值，如果为空则使用文本框
    const gameSessionId = document.getElementById('gameSessionId').value || document.getElementById('gameSessionIdText').value;
    
    if (!gameSessionId) {
        document.getElementById('getGameStateResponse').innerText = '请输入游戏会话ID';
        return;
    }
    
    try {
        const response = await apiRequest(`/api/game_sessions/${gameSessionId}`);
        
        document.getElementById('getGameStateResponse').innerText = '游戏状态获取成功';
        
        // 显示游戏状态详情
        const gameStateDisplay = document.getElementById('gameStateDisplay');
        gameStateDisplay.innerText = JSON.stringify(response.game_state, null, 2);
        gameStateDisplay.classList.remove('hidden');
    } catch (error) {
        document.getElementById('getGameStateResponse').innerText = `错误: ${error.message}`;
        document.getElementById('gameStateDisplay').classList.add('hidden');
    }
}

// 提交玩家操作
async function submitAction() {
    // 尝试从选择框获取值，如果为空则使用文本框
    const gameSessionId = document.getElementById('actionGameSessionId').value || document.getElementById('actionGameSessionIdText').value;
    const actionType = document.getElementById('actionType').value;
    const actionPayloadStr = document.getElementById('actionPayload').value;
    
    if (!gameSessionId) {
        document.getElementById('submitActionResponse').innerText = '请输入游戏会话ID';
        return;
    }
    
    let actionPayload = {};
    if (actionPayloadStr) {
        try {
            actionPayload = JSON.parse(actionPayloadStr);
        } catch (e) {
            document.getElementById('submitActionResponse').innerText = `操作载荷JSON格式错误: ${e.message}`;
            return;
        }
    }
    
    try {
        const response = await apiRequest(`/api/game_sessions/${gameSessionId}/actions`, 'POST', {
            action: actionType,
            payload: actionPayload
        });
        
        document.getElementById('submitActionResponse').innerText = JSON.stringify(response, null, 2);
    } catch (error) {
        document.getElementById('submitActionResponse').innerText = `错误: ${error.message}`;
    }
}

// 结束游戏
async function endGame() {
    // 尝试从选择框获取值，如果为空则使用文本框
    const gameSessionId = document.getElementById('endGameSessionId').value || document.getElementById('endGameSessionIdText').value;
    
    if (!gameSessionId) {
        document.getElementById('endGameResponse').innerText = '请输入游戏会话ID';
        return;
    }
    
    try {
        const response = await apiRequest(`/api/game_sessions/${gameSessionId}/end`, 'POST');
        
        document.getElementById('endGameResponse').innerText = JSON.stringify(response, null, 2);
    } catch (error) {
        document.getElementById('endGameResponse').innerText = `错误: ${error.message}`;
    }
}

// 获取回放列表
async function getReplayList() {
    try {
        const response = await apiRequest('/api/replays');
        
        document.getElementById('replayListResponse').innerText = JSON.stringify(response, null, 2);
        
        // 更新回放列表
        replays = response.replays || [];
        updateSelectOptions('replayId', replays, 'replay_id', 'replay_id');
    } catch (error) {
        document.getElementById('replayListResponse').innerText = `错误: ${error.message}`;
    }
}

// 获取特定回放
async function getReplay() {
    // 尝试从选择框获取值，如果为空则使用文本框
    const replayId = document.getElementById('replayId').value || document.getElementById('replayIdText').value;
    
    if (!replayId) {
        document.getElementById('replayResponse').innerText = '请输入回放ID';
        return;
    }
    
    try {
        const response = await apiRequest(`/api/replays/${replayId}`);
        
        document.getElementById('replayResponse').innerText = JSON.stringify(response, null, 2);
    } catch (error) {
        document.getElementById('replayResponse').innerText = `错误: ${error.message}`;
    }
}

// 加入观战
async function joinSpectate() {
    // 尝试从选择框获取值，如果为空则使用文本框
    const gameSessionId = document.getElementById('spectateGameSessionId').value || document.getElementById('spectateGameSessionIdText').value;
    
    if (!gameSessionId) {
        document.getElementById('spectateResponse').innerText = '请输入游戏会话ID';
        return;
    }
    
    try {
        const response = await apiRequest(`/api/spectator/${gameSessionId}/join`, 'POST');
        
        document.getElementById('spectateResponse').innerText = JSON.stringify(response, null, 2);
    } catch (error) {
        document.getElementById('spectateResponse').innerText = `错误: ${error.message}`;
    }
}

// 获取可观看游戏
async function getActiveGames() {
    try {
        const response = await apiRequest('/api/spectator/active_games');
        
        document.getElementById('activeGamesResponse').innerText = JSON.stringify(response, null, 2);
        
        // 更新游戏列表
        const games = response.active_games || [];
        updateSelectOptions('spectateGameSessionId', games, 'game_id', 'game_id');
    } catch (error) {
        document.getElementById('activeGamesResponse').innerText = `错误: ${error.message}`;
    }
}