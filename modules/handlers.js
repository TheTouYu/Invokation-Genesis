// 处理用户选择
function handlePlayer2Select(select) {
    if (select.value === 'refresh') {
        loadUsers();
        select.value = '';
    } else {
        document.getElementById('player2IdText').value = select.value;
    }
}

// 处理卡组1选择
function handleDeck1Select(select) {
    if (select.value === 'refresh') {
        loadUserDecks();
        select.value = '';
    } else {
        document.getElementById('deck1IdText').value = select.value;
    }
}

// 处理卡组2选择
function handleDeck2Select(select) {
    if (select.value === 'refresh') {
        loadUserDecks();
        select.value = '';
    } else {
        document.getElementById('deck2IdText').value = select.value;
    }
}

// 处理游戏会话选择
function handleGameSessionSelect(select) {
    if (select.value === 'refresh') {
        loadGameSessions();
        select.value = '';
    } else {
        document.getElementById('gameSessionIdText').value = select.value;
    }
}

// 处理操作游戏会话选择
function handleActionGameSessionSelect(select) {
    if (select.value === 'refresh') {
        loadGameSessions();
        select.value = '';
    } else {
        document.getElementById('actionGameSessionIdText').value = select.value;
    }
}

// 处理结束游戏选择
function handleEndGameSelect(select) {
    if (select.value === 'refresh') {
        loadGameSessions();
        select.value = '';
    } else {
        document.getElementById('endGameSessionIdText').value = select.value;
    }
}

// 处理回放选择
function handleReplaySelect(select) {
    if (select.value === 'refresh') {
        loadReplays();
        select.value = '';
    } else {
        document.getElementById('replayIdText').value = select.value;
    }
}

// 处理观战选择
function handleSpectateSelect(select) {
    if (select.value === 'refresh') {
        loadGameSessions();
        select.value = '';
    } else {
        document.getElementById('spectateGameSessionIdText').value = select.value;
    }
}

// 更新操作载荷助手
function updatePayloadHelper() {
    // 这里可以根据选择的操作类型显示不同的载荷示例
    // 目前我们通过点击示例来填充
}