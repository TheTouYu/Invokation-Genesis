# 图片使用位置文档

本文档记录了项目中使用 `/Users/developer/GolandProjects/git/cherf/Invokation-Genesis/image.png` 图片的所有位置。

## 1. Lobby (大厅页面)
**文件**: `/frontend/src/components/Lobby/Lobby.tsx`
- 用作页面背景图片
- 注释位置：第8行
- 样式设置：`backgroundImage: url('/Users/developer/GolandProjects/git/cherf/Invokation-Genesis/image.png')`

## 2. Login (登录页面)
**文件**: `/frontend/src/components/Login/Login.tsx`
- 用作登录页面的圆形头像图标
- 注释位置：第9行
- 样式设置：`backgroundImage: url('/Users/developer/GolandProjects/git/cherf/Invokation-Genesis/image.png')`

## 3. Register (注册页面)
**文件**: `/frontend/src/components/Register/Register.tsx`
- 用作注册页面的圆形头像图标
- 注释位置：第9行
- 样式设置：`backgroundImage: url('/Users/developer/GolandProjects/git/cherf/Invokation-Genesis/image.png')`

## 4. DeckBuilder (卡组构建页面)
**文件**: `/frontend/src/components/DeckBuilder/DeckBuilder.tsx`
- 用作页面标题旁边的图标
- 注释位置：第9行
- 样式设置：`backgroundImage: url('/Users/developer/GolandProjects/git/cherf/Invokation-Genesis/image.png')`

## 5. Card (卡牌组件)
**文件**: `/frontend/src/components/Card/Card.tsx`
- 用作默认卡牌图片（当没有特定卡牌图片时）
- 注释位置：第170行
- 样式设置：`backgroundImage: url('/Users/developer/GolandProjects/git/cherf/Invokation-Genesis/image.png')`

## 6. GameBoard (游戏面板)
**文件**: `/frontend/src/components/GameBoard/GameBoard.tsx`
- 用作游戏面板的背景纹理
- 注释位置：第33行
- 样式设置：`background: ... url('/Users/developer/GolandProjects/git/cherf/Invokation-Genesis/image.png')`

## 7. 主题切换功能新增文件

### 组件文件
- `/frontend/src/contexts/ThemeContext.tsx` - 主题状态管理
- `/frontend/src/components/ThemeToggle/ThemeToggle.tsx` - 主题切换按钮组件
- `/frontend/src/types/theme.ts` - 主题类型定义

### 主题功能说明
- **位置**: 所有页面的右上角
- **功能**: 切换白天、黑夜、护眼三种模式
- **持久化**: 主题选择会保存到localStorage
- **状态管理**: 使用React Context API管理主题状态

## 注意事项

1. 所有图片引用均使用绝对路径 `/Users/developer/GolandProjects/git/cherf/Invokation-Genesis/image.png`
2. 在开发环境中，此路径可能需要调整为相对路径或通过 public 目录提供
3. 在生产环境中，建议将图片放置在 `public` 目录下并通过相对路径引用
4. 如果需要更改图片，请确保所有引用的路径保持一致
5. 新增的主题切换功能使用CSS自定义属性实现，可扩展性强

## 建议的生产环境路径

为了在生产环境中正确显示图片，建议：
1. 将 `image.png` 文件放置于 `/frontend/public/images/` 目录
2. 将所有引用路径更新为 `/images/image.png`