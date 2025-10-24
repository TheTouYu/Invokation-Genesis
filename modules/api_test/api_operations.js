// 用于API请求的通用函数
let jwtToken = '';

// 登录函数
async function login() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const loginResult = document.getElementById('loginResult');
    
    if (!username || !password) {
        loginResult.innerHTML = '<div class="error">请输入用户名和密码</div>';
        return;
    }
    
    try {
        const response = await fetch(`${window.location.origin}/api/auth/login`, {
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
            jwtToken = data.access_token;
            localStorage.setItem('jwtToken', jwtToken); // 存储到本地存储
            loginResult.innerHTML = '<div class="success">登录成功！令牌已获取并保存</div>';
            document.getElementById('filtersSection').style.display = 'block';
            loadFilters(); // 自动加载过滤选项
        } else {
            loginResult.innerHTML = `<div class="error">登录失败: ${data.message || data.error}</div>`;
        }
    } catch (error) {
        loginResult.innerHTML = `<div class="error">请求失败: ${error.message}</div>`;
    }
}

// 加载过滤选项
async function loadFilters() {
    if (!jwtToken) {
        document.getElementById('result').innerHTML = '<div class="error">请先登录获取令牌</div>';
        return;
    }
    
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = '<div class="loading"></div> 加载过滤选项中...';
    
    try {
        // 并行加载所有过滤选项
        const [typesRes, elementsRes, countriesRes, weaponTypesRes, tagsRes] = await Promise.all([
            fetch(`${window.location.origin}/api/filters`, {
                headers: { 'Authorization': `Bearer ${jwtToken}` }
            }),
            fetch(`${window.location.origin}/api/filters`, {
                headers: { 'Authorization': `Bearer ${jwtToken}` }
            }),
            fetch(`${window.location.origin}/api/filters`, {
                headers: { 'Authorization': `Bearer ${jwtToken}` }
            }),
            fetch(`${window.location.origin}/api/filters`, {
                headers: { 'Authorization': `Bearer ${jwtToken}` }
            }),
            fetch(`${window.location.origin}/api/filters`, {
                headers: { 'Authorization': `Bearer ${jwtToken}` }
            })
        ]);
        
        const filtersData = await typesRes.json();
        
        // 填充卡牌类型
        const typeSelect = document.getElementById('cardType');
        typeSelect.innerHTML = '<option value="">所有类型</option>';
        filtersData.card_types.forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type;
            typeSelect.appendChild(option);
        });
        
        // 填充元素
        const elementSelect = document.getElementById('element');
        elementSelect.innerHTML = '<option value="">所有元素</option>';
        filtersData.elements.forEach(element => {
            const option = document.createElement('option');
            option.value = element;
            option.textContent = element;
            elementSelect.appendChild(option);
        });
        
        // 填充国家
        const countrySelect = document.getElementById('country');
        countrySelect.innerHTML = '<option value="">所有国家</option>';
        filtersData.countries.forEach(country => {
            const option = document.createElement('option');
            option.value = country;
            option.textContent = country;
            countrySelect.appendChild(option);
        });
        
        // 填充武器类型
        const weaponTypeSelect = document.getElementById('weaponType');
        weaponTypeSelect.innerHTML = '<option value="">所有武器</option>';
        filtersData.weapon_types.forEach(weaponType => {
            const option = document.createElement('option');
            option.value = weaponType;
            option.textContent = weaponType;
            weaponTypeSelect.appendChild(option);
        });
        
        // 填充标签
        const tagSelect = document.getElementById('tag');
        tagSelect.innerHTML = '<option value="">所有标签</option>';
        filtersData.tags.forEach(tag => {
            const option = document.createElement('option');
            option.value = tag;
            option.textContent = tag;
            tagSelect.appendChild(option);
        });
        
        resultDiv.innerHTML = '<div class="success">过滤选项加载完成</div>';
    } catch (error) {
        resultDiv.innerHTML = `<div class="error">加载过滤选项失败: ${error.message}</div>`;
    }
}

// 搜索卡牌
async function searchCards() {
    if (!jwtToken) {
        document.getElementById('result').innerHTML = '<div class="error">请先登录获取令牌</div>';
        return;
    }
    
    // 构建查询参数
    const params = new URLSearchParams();
    const cardType = document.getElementById('cardType').value;
    const element = document.getElementById('element').value;
    const country = document.getElementById('country').value;
    const weaponType = document.getElementById('weaponType').value;
    const characterSubtype = document.getElementById('characterSubtype').value;
    const rarity = document.getElementById('rarity').value;
    const tag = document.getElementById('tag').value;
    const search = document.getElementById('search').value;
    const per_page = document.getElementById('per_page').value || 10;
    const page = document.getElementById('page').value || 1;
    
    if (cardType) params.append('type', cardType);
    if (element) params.append('element', element);
    if (country) params.append('country', country);
    if (weaponType) params.append('weapon_type', weaponType);
    if (characterSubtype) params.append('character_subtype', characterSubtype);
    if (rarity) params.append('rarity', rarity);
    if (tag) params.append('tag', tag); // Note: tag is handled differently, maybe add multiple
    if (search) params.append('search', search);
    params.append('per_page', per_page);
    params.append('page', page);
    
    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = '<div class="loading"></div> 搜索中...';
    
    try {
        const response = await fetch(`${window.location.origin}/api/cards?${params.toString()}`, {
            headers: {
                'Authorization': `Bearer ${jwtToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultDiv.innerHTML = `状态码: ${response.status}\n\n${JSON.stringify(data, null, 2)}`;
        } else {
            resultDiv.innerHTML = `状态码: ${response.status}\n\n错误信息: ${JSON.stringify(data, null, 2)}`;
        }
    } catch (error) {
        resultDiv.innerHTML = `请求失败: ${error.message}`;
    }
}

// 页面加载时检查本地存储中的令牌
window.onload = function() {
    const storedToken = localStorage.getItem('jwtToken');
    if (storedToken) {
        jwtToken = storedToken;
        document.getElementById('filtersSection').style.display = 'block';
        document.getElementById('loginResult').innerHTML = '<div class="success">已从本地存储加载令牌</div>';
    }
};