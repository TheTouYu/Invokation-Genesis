"use client"

import { GameHeader } from "@/components/layout/game-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Search, Filter, ArrowLeft, Save, Sparkles, Zap, Droplet, Flame, Plus, Minus, Trash2, Swords, Shield, Target, RotateCcw, AlertCircle, CheckCircle, X } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import Link from "next/link"
import { useState, useEffect, useMemo } from "react"
import useSWR from "swr"
import { getCards, getCharacters, getEquipments, getSupports, getEvents, getAllFilters } from "@/lib/api/cards"
import { createDeck, updateDeck, validateDeck } from "@/lib/api/decks"
import { Card as CardType, ValidateDeckRequest, DeckValidationResponse, CardFiltersResponse } from "@/lib/api/types"
import { toast } from "sonner"
import { useAuth } from "@/hooks/use-auth"

// SWR fetcher函数
const fetcher = (url: string) => fetch(url).then(res => res.json())

export default function DeckBuilderPage() {
  const { user, isAuthenticated, loading } = useAuth()
  const [failedImages, setFailedImages] = useState<Set<string>>(new Set())
  
  // 记忆化已失败的图片集合，以提高性能
  const failedImagesMemo = useMemo(() => failedImages, [failedImages])
  const [deckName, setDeckName] = useState("")
  const [selectedCharacters, setSelectedCharacters] = useState<string[]>([])
  const [selectedActions, setSelectedActions] = useState<{ id: string; count: number }[]>([])
  const [validationResult, setValidationResult] = useState<DeckValidationResponse | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [activeTab, setActiveTab] = useState("characters")
  
  // 过滤器状态
  const [characterSearchQuery, setCharacterSearchQuery] = useState("")
  const [characterElementFilter, setCharacterElementFilter] = useState("")
  const [characterCountryFilter, setCharacterCountryFilter] = useState("")
  const [characterWeaponTypeFilter, setCharacterWeaponTypeFilter] = useState("")
  const [characterRarityFilter, setCharacterRarityFilter] = useState<number | null>(null)
  const [selectedCharacterTags, setSelectedCharacterTags] = useState<string[]>([])
  
  const [actionSearchQuery, setActionSearchQuery] = useState("")
  const [actionElementFilter, setActionElementFilter] = useState("")
  const [actionCountryFilter, setActionCountryFilter] = useState("")
  const [actionTypeFilter, setActionTypeFilter] = useState("")
  const [actionRarityFilter, setActionRarityFilter] = useState<number | null>(null)
  const [selectedActionTags, setSelectedActionTags] = useState<string[]>([])
  
  // 防抖搜索状态
  const [debouncedCharacterSearchQuery, setDebouncedCharacterSearchQuery] = useState(characterSearchQuery)
  const [debouncedActionSearchQuery, setDebouncedActionSearchQuery] = useState(actionSearchQuery)
  
  // 从后端获取过滤选项
  const { data: allFilterOptions } = useSWR(
    "/api/filters",
    () => getAllFilters(),
    {
      onError: (error) => {
        if (error.message && error.message.startsWith('AUTH_ERROR:')) {
          // 重定向到登录页面已经在API客户端中处理
        }
      }
    }
  )

  // 使用统一的API端点获取所有卡牌数据
  const allCardsSWR = useSWR(
    JSON.stringify({}), // 获取所有卡牌
    () => getCards({}),
    {
      refreshInterval: 0, // 不自动刷新
      revalidateOnFocus: false, // 窗口聚焦时不重新验证
      revalidateOnReconnect: false, // 重连时不重新验证
      dedupingInterval: 0, // 禁用去重
      focusThrottleInterval: 0, // 禁用焦点节流
    }
  )

  const { data: allCardsData, error: allCardsError } = allCardsSWR

  // 当卡组完整时（3个角色+30张行动牌）自动验证卡组
  useEffect(() => {
    // 仅在卡组完整时才自动验证（3个角色+30张行动牌=33张）
    if (deckName && 
        selectedCharacters.length === 3 && 
        selectedActions.reduce((sum, a) => sum + a.count, 0) === 30) {
      
      const validate = async () => {
        const validationData: ValidateDeckRequest = {
          deck_name: deckName,
          characters: selectedCharacters,
          cards: selectedActions.flatMap(({ id, count }) => Array(count).fill(id))
        }
        
        try {
          await validateDeckAndUpdateResult(validationData)
        } catch (error) {
          console.error("验证卡组时出错:", error)
        }
      }
      
      validate()
    } else if (selectedCharacters.length < 3 || 
               selectedActions.reduce((sum, a) => sum + a.count, 0) < 30) {
      // 如果卡组不完整，清空验证结果
      setValidationResult(null)
    }
  }, [deckName, selectedCharacters, selectedActions])
  
  // 防抖处理角色搜索查询
  useEffect(() => {
    if (characterSearchQuery) {
      const timer = setTimeout(() => {
        setDebouncedCharacterSearchQuery(characterSearchQuery)
      }, 1000) // 1秒防抖延迟
      
      return () => clearTimeout(timer)
    } else {
      // 如果搜索查询为空，立即更新（清空搜索）
      setDebouncedCharacterSearchQuery(characterSearchQuery)
    }
  }, [characterSearchQuery])
  
  // 防抖处理行动牌搜索查询
  useEffect(() => {
    if (actionSearchQuery) {
      const timer = setTimeout(() => {
        setDebouncedActionSearchQuery(actionSearchQuery)
      }, 1000) // 1秒防抖延迟
      
      return () => clearTimeout(timer)
    } else {
      // 如果搜索查询为空，立即更新（清空搜索）
      setDebouncedActionSearchQuery(actionSearchQuery)
    }
  }, [actionSearchQuery])
  
  // 组件挂载时重新验证数据
  useEffect(() => {
    if (typeof window !== 'undefined') { // 确保在客户端执行
      // 重新验证所有SWR数据
      allCardsSWR.mutate()
    }
  }, [])
  
  // 切换角色标签
  const toggleCharacterTag = (tag: string) => {
    setSelectedCharacterTags(prev => 
      prev.includes(tag) 
        ? prev.filter(t => t !== tag) 
        : [...prev, tag]
    )
  }
  
  // 切换行动牌标签
  const toggleActionTag = (tag: string) => {
    setSelectedActionTags(prev => 
      prev.includes(tag) 
        ? prev.filter(t => t !== tag) 
        : [...prev, tag]
    )
  }
  
  // 点击标签，添加到已选标签列表
  const handleTagClick = (tag: string, isCharacterTab: boolean) => {
    if (isCharacterTab) {
      if (!selectedCharacterTags.includes(tag)) {
        setSelectedCharacterTags(prev => [...prev, tag])
      }
    } else {
      if (!selectedActionTags.includes(tag)) {
        setSelectedActionTags(prev => [...prev, tag])
      }
    }
  }

  // 构建角色卡过滤器对象
  const characterFilters = {
    type: "角色牌",
    search: debouncedCharacterSearchQuery,
    element: characterElementFilter,
    country: characterCountryFilter,
    weapon_type: characterWeaponTypeFilter,
    rarity: characterRarityFilter || undefined,
    tag: selectedCharacterTags.length > 0 ? selectedCharacterTags : undefined,
  };

  // 使用SWR根据过滤器获取角色卡数据
  const characterCardsSWR = useSWR(
    JSON.stringify(characterFilters), // 使用filters对象作为key
    () => getCards(characterFilters),
    {
      refreshInterval: 0, // 不自动刷新
      revalidateOnFocus: false, // 窗口聚焦时不重新验证
      revalidateOnReconnect: false, // 重连时不重新验证
      dedupingInterval: 0, // 禁用去重
      focusThrottleInterval: 0, // 禁用焦点节流
    }
  )

  // 构建行动牌过滤器对象
  // 如果没有指定特定类型，则不设置type参数，让后端返回所有类型的卡牌，然后在前端过滤
  const actionFilters = {
    type: actionTypeFilter,  // 只在用户明确选择时才设置类型，否则为 undefined
    search: debouncedActionSearchQuery,
    element: actionElementFilter,
    country: actionCountryFilter,
    rarity: actionRarityFilter || undefined,
    tag: selectedActionTags.length > 0 ? selectedActionTags : undefined,
  };

  // 使用SWR根据过滤器获取行动牌数据
  const actionCardsSWR = useSWR(
    JSON.stringify(actionFilters), // 使用filters对象作为key
    () => getCards(actionFilters),
    {
      refreshInterval: 0, // 不自动刷新
      revalidateOnFocus: false, // 窗口聚焦时不重新验证
      revalidateOnReconnect: false, // 重连时不重新验证
      dedupingInterval: 0, // 禁用去重
      focusThrottleInterval: 0, // 禁用焦点节流
    }
  )

  const { data: characterCardsData, error: characterCardsError } = characterCardsSWR
  const { data: actionCardsData, error: actionCardsError } = actionCardsSWR

  // 检查所有数据是否已加载
  if (!allCardsData || !characterCardsData || (activeTab === 'actions' && !actionCardsData)) {
    return <div className="flex items-center justify-center h-40">
      <p className="text-muted-foreground">正在加载卡牌数据...</p>
    </div>
  }

  // 检查错误状态
  if (allCardsError || characterCardsError || (activeTab === 'actions' && actionCardsError)) {
    console.error("加载卡牌数据失败:", { 
      allCardsError,
      characterCardsError,
      actionCardsError
    })
    return <div>加载卡牌数据失败</div>
  }

  // 根据类型分类所有卡牌（用于其他功能，如卡组验证）
  const allCharactersData = allCardsData.cards.filter((card: CardType) => card.type === "角色牌");
  const allActions = allCardsData.cards.filter((card: CardType) => 
    card.type === "事件牌" || 
    card.type === "支援牌" || 
    card.type === "装备牌"
  );

  // 使用根据过滤条件获取的卡牌数据，并确保行动牌只包含非角色牌
  const charactersData = characterCardsData?.cards || [];
  const filteredActions = (actionCardsData?.cards || []).filter((card: CardType) => 
    card.type === "事件牌" || 
    card.type === "支援牌" || 
    card.type === "装备牌"
  );

  // 计算总卡牌数
  const totalCards = selectedCharacters.length + selectedActions.reduce((sum, a) => sum + a.count, 0)

  // 添加角色到卡组（最多3个）
  const addCharacter = (id: string) => {
    if (selectedCharacters.length < 3 && !selectedCharacters.includes(id)) {
      setSelectedCharacters([...selectedCharacters, id])
    }
  }

  // 从卡组移除角色
  const removeCharacter = (id: string) => {
    setSelectedCharacters(selectedCharacters.filter((cid) => cid !== id))
  }

  // 添加行动牌到卡组（最多30张，同名最多2张）
  const addAction = (id: string) => {
    const existing = selectedActions.find((a) => a.id === id)
    const totalActions = selectedActions.reduce((sum, a) => sum + a.count, 0)

    // 检查是否已达到30张行动牌的上限
    if (totalActions >= 30) return

    let newSelectedActions: { id: string; count: number }[]
    
    if (existing) {
      // 检查是否已达到同名卡的2张上限
      if (existing.count < 2) {
        newSelectedActions = selectedActions.map((a) => 
          a.id === id ? { ...a, count: a.count + 1 } : a
        )
      } else {
        return // 达到同名卡上限，不执行操作
      }
    } else {
      // 添加第一张新牌
      newSelectedActions = [...selectedActions, { id, count: 1 }]
    }
    
    setSelectedActions(newSelectedActions)
  }

  // 从卡组移除行动牌
  const removeAction = (id: string) => {
    const existing = selectedActions.find((a) => a.id === id)
    if (existing) {
      let newSelectedActions: { id: string; count: number }[]
      
      if (existing.count > 1) {
        newSelectedActions = selectedActions.map((a) => 
          a.id === id ? { ...a, count: a.count - 1 } : a
        )
      } else {
        newSelectedActions = selectedActions.filter((a) => a.id !== id)
      }
      
      setSelectedActions(newSelectedActions)
    }
  }

  // 验证卡组并更新结果
  const validateDeckAndUpdateResult = async (validationData: ValidateDeckRequest) => {
    // 检查是否已登录，如果 auth 状态还在加载中，稍后再试
    if (loading) {
      toast.error("认证信息正在加载，请稍后再试")
      return
    }
    
    if (!isAuthenticated) {
      toast.error("请先登录以验证卡组")
      return
    }
    
    try {
      const result = await validateDeck(validationData)
      setValidationResult(result)
      
      if (result.valid) {
        toast.success("卡组验证成功！")
      } else {
        toast.error("卡组验证失败，请检查错误信息")
      }
    } catch (error: any) {
      console.error("验证卡组时出错:", error)
      if (error.message.includes("401") || error.message.includes("Authorization")) {
        toast.error("请先登录以验证卡组")
      } else {
        toast.error("验证卡组时出现错误：" + error.message)
      }
    }
  }

  // 验证卡组
  const validateAndSetResult = async () => {
    // 检查是否已登录，如果 auth 状态还在加载中，稍后再试
    if (loading) {
      toast.error("认证信息正在加载，请稍后再试")
      return
    }
    
    if (!isAuthenticated) {
      toast.error("请先登录以验证卡组")
      return
    }

    if (!deckName) {
      toast.error("请输入卡组名称")
      return
    }

    if (selectedCharacters.length !== 3) {
      toast.error("请选择3个角色")
      return
    }

    if (totalCards !== 33) {
      toast.error("卡组必须包含33张卡牌（3个角色+30张行动牌）")
      return
    }

    try {
      const validationData: ValidateDeckRequest = {
        deck_name: deckName,
        characters: selectedCharacters,
        cards: selectedActions.flatMap(({ id, count }) => Array(count).fill(id))
      }

      await validateDeckAndUpdateResult(validationData)
    } catch (error) {
      console.error("验证卡组时出错:", error)
      toast.error("验证卡组时出现错误")
    }
  }

  // 保存卡组
  const saveDeck = async () => {
    // 检查是否已登录，如果 auth 状态还在加载中，稍后再试
    if (loading) {
      toast.error("认证信息正在加载，请稍后再试")
      return
    }

    if (!isAuthenticated) {
      toast.error("请先登录以保存卡组")
      return
    }

    if (!deckName) {
      toast.error("请输入卡组名称")
      return
    }

    if (selectedCharacters.length !== 3) {
      toast.error("请选择3个角色")
      return
    }

    if (totalCards !== 33) {
      toast.error("卡组必须包含33张卡牌（3个角色+30张行动牌）")
      return
    }

    try {
      setIsSaving(true)
      
      // 在保存前再次验证卡组
      const validationData: ValidateDeckRequest = {
        deck_name: deckName,
        characters: selectedCharacters,
        cards: selectedActions.flatMap(({ id, count }) => Array(count).fill(id))
      }

      const validationResult = await validateDeck(validationData)
      if (!validationResult.valid) {
        toast.error("卡组验证失败，无法保存")
        setValidationResult(validationResult)
        return
      }
      
      const cardList = selectedActions.flatMap(({ id, count }) => Array(count).fill(id))
      const deckData = {
        name: deckName,
        description: `由${selectedCharacters.length}个角色和${selectedActions.reduce((sum, a) => sum + a.count, 0)}张行动牌组成的卡组`,
        cards: [...selectedCharacters, ...cardList]
      }

      await createDeck(deckData)
      toast.success("卡组保存成功！")
    } catch (error: any) {
      console.error("保存卡组时出错:", error)
      if (error.message.includes("401") || error.message.includes("Authorization")) {
        toast.error("请先登录以保存卡组")
      } else {
        toast.error("保存卡组时出现错误：" + error.message)
      }
    } finally {
      setIsSaving(false)
    }
  }

  // 获取图标组件根据元素类型
  const getElementIcon = (element: string) => {
    switch (element?.toLowerCase()) {
      case 'electro':
        return Zap
      case 'cryo':
        return Droplet // 应该是Snowflake，但这里使用已导入的Droplet
      case 'pyro':
        return Flame
      case 'hydro':
        return Droplet
      case 'anemo':
        return Target // 使用Target作为风元素图标
      case 'geo':
        return RotateCcw // 使用RotateCcw作为岩元素图标
      case 'dendro':
        return Shield // 使用Shield作为草元素图标
      default:
        return Target
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <GameHeader />

      <main className="flex-1 container py-8">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <Button asChild variant="ghost" className="gap-2">
              <Link href="/decks">
                <ArrowLeft className="w-4 h-4" />
                返回卡组列表
              </Link>
            </Button>
            <div className="flex gap-2">
              <Button 
                size="lg" 
                variant="outline" 
                className="gap-2"
                onClick={validateAndSetResult}
              >
                <CheckCircle className="w-4 h-4" />
                验证卡组
              </Button>
              <Button 
                size="lg" 
                className="gap-2"
                onClick={saveDeck}
                disabled={isSaving}
              >
                {isSaving ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                    保存中...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    保存卡组
                  </>
                )}
              </Button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Card Selection */}
            <div className="lg:col-span-2 space-y-6">
              <Card>
                <CardContent className="p-6 space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="deckName">卡组名称</Label>
                    <Input
                      id="deckName"
                      placeholder="输入卡组名称..."
                      value={deckName}
                      onChange={(e) => setDeckName(e.target.value)}
                    />
                  </div>
                </CardContent>
              </Card>

              <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="characters">选择角色 ({selectedCharacters.length}/3)</TabsTrigger>
                  <TabsTrigger value="actions">
                    选择行动牌 ({selectedActions.reduce((sum, a) => sum + a.count, 0)}/30)
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="characters" className="space-y-4">
                  {/* 过滤选项 */}
                  <div className="space-y-4">
                    <div className="flex flex-col sm:flex-row gap-4">
                      <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <Input
                          placeholder="搜索角色..."
                          className="pl-10"
                          value={characterSearchQuery}
                          onChange={(e) => setCharacterSearchQuery(e.target.value)}
                        />
                        {characterSearchQuery !== debouncedCharacterSearchQuery && (
                          <div className="absolute right-3 top-1/2 -translate-y-1/2">
                            <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div>
                        <label className="text-sm font-medium text-muted-foreground mb-1 block">元素</label>
                        <select 
                          className="w-full p-2 border rounded-md bg-background"
                          value={characterElementFilter}
                          onChange={(e) => setCharacterElementFilter(e.target.value)}
                        >
                          <option value="">全部</option>
                          {allFilterOptions?.elements?.map((element) => (
                            <option key={`char-element-${element}`} value={element}>{element}</option>
                          ))}
                        </select>
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium text-muted-foreground mb-1 block">国家</label>
                        <select 
                          className="w-full p-2 border rounded-md bg-background"
                          value={characterCountryFilter}
                          onChange={(e) => setCharacterCountryFilter(e.target.value)}
                        >
                          <option value="">全部</option>
                          {allFilterOptions?.countries?.map((country) => (
                            <option key={`char-country-${country}`} value={country}>{country}</option>
                          ))}
                        </select>
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium text-muted-foreground mb-1 block">武器类型</label>
                        <select 
                          className="w-full p-2 border rounded-md bg-background"
                          value={characterWeaponTypeFilter}
                          onChange={(e) => setCharacterWeaponTypeFilter(e.target.value)}
                        >
                          <option value="">全部</option>
                          {allFilterOptions?.weapon_types?.map((weaponType) => (
                            <option key={`char-weapon-${weaponType}`} value={weaponType}>{weaponType}</option>
                          ))}
                        </select>
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium text-muted-foreground mb-1 block">稀有度</label>
                        <select 
                          className="w-full p-2 border rounded-md bg-background"
                          value={characterRarityFilter || ""}
                          onChange={(e) => setCharacterRarityFilter(e.target.value ? parseInt(e.target.value) : null)}
                        >
                          <option value="">全部</option>
                          <option value="1">1星</option>
                          <option value="2">2星</option>
                          <option value="3">3星</option>
                          <option value="4">4星</option>
                          <option value="5">5星</option>
                        </select>
                      </div>
                    </div>
                    
                    {/* 标签选择 */}
                    <div>
                      <label className="text-sm font-medium text-muted-foreground mb-2 block">可用标签</label>
                      <div className="flex flex-wrap gap-2 mb-3">
                        {allFilterOptions?.tags?.map((tag) => (
                          <Badge 
                            key={`char-available-${tag}`}
                            variant="outline"
                            className="cursor-pointer hover:bg-accent"
                            onClick={() => handleTagClick(tag, true)}
                          >
                            {tag}
                          </Badge>
                        ))}
                      </div>
                      
                      <label className="text-sm font-medium text-muted-foreground mb-2 block">已选标签</label>
                      <div className="flex flex-wrap gap-2">
                        {selectedCharacterTags.map((tag) => (
                          <Badge 
                            key={`char-selected-${tag}`}
                            variant="default"
                            className="cursor-pointer"
                            onClick={() => toggleCharacterTag(tag)}
                          >
                            {tag}
                            <X className="ml-1 h-3 w-3" />
                          </Badge>
                        ))}
                        {selectedCharacterTags.length === 0 && (
                          <p className="text-sm text-muted-foreground">暂无已选标签</p>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {charactersData && charactersData.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {charactersData.map((char: CardType) => {
                          const isSelected = selectedCharacters.includes(char.id)
                          return (
                            <TooltipProvider key={char.id}>
                              <Tooltip>
                                <TooltipTrigger asChild>
                                  <Card
                                    className={`cursor-pointer transition-all ${
                                      isSelected ? "border-primary bg-primary/5" : "hover:border-primary/40"
                                    }`}
                                    onClick={() => (isSelected ? removeCharacter(char.id) : addCharacter(char.id))}
                                  >
                                    <CardContent className="p-4">
                                      <div className="flex items-center gap-4">
                                        <div className="w-16 h-16 rounded-lg overflow-hidden">
                                          {char.image_url && !failedImagesMemo.has(char.id) ? (
                                            <img 
                                              src={char.image_url} 
                                              alt={char.name} 
                                              className="w-full h-full object-cover"
                                              onError={() => {
                                                setFailedImages(prev => new Set(prev).add(char.id))
                                              }}
                                            />
                                          ) : (
                                            <div className="w-full h-full bg-gradient-to-br from-primary/20 to-accent/10 flex items-center justify-center">
                                              {(() => {
                                                const Icon = getElementIcon(char.element_type || char.element || "")
                                                return <Icon className="w-8 h-8 text-primary" />
                                              })()}
                                            </div>
                                          )}
                                        </div>
                                        <div className="flex-1">
                                          <h3 className="font-bold mb-1">{char.name}</h3>
                                          <div className="flex items-center gap-2">
                                            <Badge variant="outline" className="text-xs">
                                              费用 {char.cost?.reduce((sum, c) => sum + c.count, 0) || 1}
                                            </Badge>
                                            <Badge variant="secondary" className="text-xs capitalize">
                                              {char.element_type || char.element || "none"}
                                            </Badge>
                                          </div>
                                        </div>
                                        {isSelected && (
                                          <div className="w-6 h-6 rounded-full bg-primary flex items-center justify-center">
                                            <Sparkles className="w-4 h-4 text-primary-foreground" />
                                          </div>
                                        )}
                                      </div>
                                    </CardContent>
                                  </Card>
                                </TooltipTrigger>
                                <TooltipContent className="max-w-md w-auto bg-popover text-popover-foreground border p-4">
                                  <div className="space-y-2 max-h-[400px] overflow-y-auto">
                                    <h4 className="font-bold text-lg">{char.title ? `${char.title} - ${char.name}` : char.name}</h4>
                                    <div className="flex flex-wrap gap-2">
                                      <Badge variant="secondary" className="capitalize">
                                        {char.element_type || char.element || "无元素"}
                                      </Badge>
                                      <Badge variant="outline">
                                        {char.country || "无国家"}
                                      </Badge>
                                      {char.weapon_type && (
                                        <Badge variant="outline">
                                          {char.weapon_type}
                                        </Badge>
                                      )}
                                      <div className="flex items-center gap-1">
                                        {[...Array(char.rarity)].map((_, i) => (
                                          <Sparkles key={i} className="w-3 h-3 fill-current" />
                                        ))}
                                      </div>
                                    </div>
                                    <div className="text-sm">
                                      <p><span className="font-semibold">生命值:</span> {char.health || "N/A"}</p>
                                      <p><span className="font-semibold">能量:</span> {char.energy || "N/A"}/{char.max_energy || "N/A"}</p>
                                      {char.description && (
                                        <p><span className="font-semibold">描述:</span> {char.description}</p>
                                      )}
                                    </div>
                                    {char.skills && Array.isArray(char.skills) && char.skills.length > 0 && (
                                      <div className="pt-2 border-t">
                                        <h5 className="font-semibold mb-1">技能:</h5>
                                        <ul className="space-y-1">
                                          {char.skills.map((skill, idx) => (
                                            <li key={idx} className="text-sm">
                                              <span className="font-medium">{skill.name}</span>
                                              <div className="text-xs mt-1 ml-2">
                                                {skill.cost && Array.isArray(skill.cost) && skill.cost.length > 0 && (
                                                  <div className="inline-flex flex-wrap gap-1 mr-2">
                                                    {skill.cost.map((cost, costIdx) => {
                                                      const CostIcon = getElementIcon(cost.type);
                                                      return (
                                                        <span key={costIdx} className="inline-flex items-center gap-0.5 bg-secondary px-1.5 py-0.5 rounded text-xs">
                                                          <CostIcon className="w-2.5 h-2.5" />
                                                          {cost.value}
                                                        </span>
                                                      );
                                                    })}
                                                  </div>
                                                )}
                                              </div>
                                              <p className="mt-1">{skill.description}</p>
                                            </li>
                                          ))}
                                        </ul>
                                      </div>
                                    )}
                                  </div>
                                </TooltipContent>
                              </Tooltip>
                            </TooltipProvider>
                          )
                        })}
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-40">
                      <p className="text-muted-foreground">
                        {charactersData ? "没有找到匹配的角色牌" : "正在加载角色数据..."}
                      </p>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="actions" className="space-y-4">
                  {/* 过滤选项 */}
                  <div className="space-y-4">
                    <div className="flex flex-col sm:flex-row gap-4">
                      <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <Input
                          placeholder="搜索行动牌..."
                          className="pl-10"
                          value={actionSearchQuery}
                          onChange={(e) => setActionSearchQuery(e.target.value)}
                        />
                        {actionSearchQuery !== debouncedActionSearchQuery && (
                          <div className="absolute right-3 top-1/2 -translate-y-1/2">
                            <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                      <div>
                        <label className="text-sm font-medium text-muted-foreground mb-1 block">元素</label>
                        <select 
                          className="w-full p-2 border rounded-md bg-background"
                          value={actionElementFilter}
                          onChange={(e) => setActionElementFilter(e.target.value)}
                        >
                          <option value="">全部</option>
                          {allFilterOptions?.elements?.map((element) => (
                            <option key={`action-element-${element}`} value={element}>{element}</option>
                          ))}
                        </select>
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium text-muted-foreground mb-1 block">国家</label>
                        <select 
                          className="w-full p-2 border rounded-md bg-background"
                          value={actionCountryFilter}
                          onChange={(e) => setActionCountryFilter(e.target.value)}
                        >
                          <option value="">全部</option>
                          {allFilterOptions?.countries?.map((country) => (
                            <option key={`action-country-${country}`} value={country}>{country}</option>
                          ))}
                        </select>
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium text-muted-foreground mb-1 block">卡牌类型</label>
                        <select 
                          className="w-full p-2 border rounded-md bg-background"
                          value={actionTypeFilter}
                          onChange={(e) => setActionTypeFilter(e.target.value)}
                        >
                          <option value="">全部</option>
                          {allFilterOptions?.card_types?.map((cardType) => (
                            <option key={`action-type-${cardType}`} value={cardType}>{cardType}</option>
                          ))}
                        </select>
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium text-muted-foreground mb-1 block">稀有度</label>
                        <select 
                          className="w-full p-2 border rounded-md bg-background"
                          value={actionRarityFilter || ""}
                          onChange={(e) => setActionRarityFilter(e.target.value ? parseInt(e.target.value) : null)}
                        >
                          <option value="">全部</option>
                          <option value="1">1星</option>
                          <option value="2">2星</option>
                          <option value="3">3星</option>
                          <option value="4">4星</option>
                          <option value="5">5星</option>
                        </select>
                      </div>
                    </div>
                    
                    {/* 标签选择 */}
                    <div>
                      <label className="text-sm font-medium text-muted-foreground mb-2 block">可用标签</label>
                      <div className="flex flex-wrap gap-2 mb-3">
                        {allFilterOptions?.tags?.map((tag) => (
                          <Badge 
                            key={`action-available-${tag}`}
                            variant="outline"
                            className="cursor-pointer hover:bg-accent"
                            onClick={() => handleTagClick(tag, false)}
                          >
                            {tag}
                          </Badge>
                        ))}
                      </div>
                      
                      <label className="text-sm font-medium text-muted-foreground mb-2 block">已选标签</label>
                      <div className="flex flex-wrap gap-2">
                        {selectedActionTags.map((tag) => (
                          <Badge 
                            key={`action-selected-${tag}`}
                            variant="default"
                            className="cursor-pointer"
                            onClick={() => toggleActionTag(tag)}
                          >
                            {tag}
                            <X className="ml-1 h-3 w-3" />
                          </Badge>
                        ))}
                        {selectedActionTags.length === 0 && (
                          <p className="text-sm text-muted-foreground">暂无已选标签</p>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {filteredActions && filteredActions.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {filteredActions.map((action: CardType) => {
                        const selected = selectedActions.find((a) => a.id === action.id)
                        const count = selected?.count || 0
                        return (
                          <TooltipProvider key={action.id}>
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Card
                                  className={`transition-all ${
                                    count > 0 ? "border-accent bg-accent/5" : "hover:border-accent/40"
                                  }`}
                                >
                                  <CardContent className="p-4">
                                    <div className="flex items-center gap-4">
                                      <div className="w-16 h-16 rounded-lg overflow-hidden">
                                        {action.image_url && !failedImagesMemo.has(action.id) ? (
                                          <img 
                                            src={action.image_url} 
                                            alt={action.name} 
                                            className="w-full h-full object-cover"
                                            onError={() => {
                                              setFailedImages(prev => new Set(prev).add(action.id))
                                            }}
                                          />
                                        ) : (
                                          <div className="w-full h-full bg-gradient-to-br from-primary/20 to-accent/10 flex items-center justify-center">
                                            {(() => {
                                              const Icon = getElementIcon(action.element_type || action.element || "")
                                              return <Icon className="w-8 h-8 text-primary" />
                                            })()}
                                          </div>
                                        )}
                                      </div>
                                      <div className="flex-1">
                                        <h3 className="font-bold mb-1">{action.name}</h3>
                                        <div className="flex items-center gap-2">
                                          <Badge variant="outline" className="text-xs">
                                            费用 {action.cost?.reduce((sum, c) => sum + c.count, 0) || 1}
                                          </Badge>
                                          <Badge variant="secondary" className="text-xs">
                                            {action.type}
                                          </Badge>
                                        </div>
                                      </div>
                                    </div>
                                    <div className="flex items-center gap-2 mt-3">
                                      <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => removeAction(action.id)}
                                        disabled={count === 0}
                                      >
                                        <Minus className="w-3 h-3" />
                                      </Button>
                                      <div className="flex-1 text-center font-bold">{count}</div>
                                      <Button
                                        size="sm"
                                        variant="outline"
                                        onClick={() => addAction(action.id)}
                                        disabled={count >= 2 || totalCards >= 33}
                                      >
                                        <Plus className="w-3 h-3" />
                                      </Button>
                                    </div>
                                  </CardContent>
                                </Card>
                              </TooltipTrigger>
                              <TooltipContent className="max-w-md w-auto bg-popover text-popover-foreground border p-4">
                                <div className="space-y-2 max-h-[400px] overflow-y-auto">
                                  <h4 className="font-bold text-lg">{action.name}</h4>
                                  <div className="flex flex-wrap gap-2">
                                    <Badge variant="secondary" className="capitalize">
                                      {action.type || "无类型"}
                                    </Badge>
                                    {action.element_type && (
                                      <Badge variant="outline">
                                        {action.element_type}
                                      </Badge>
                                    )}
                                    {action.country && (
                                      <Badge variant="outline">
                                        {action.country}
                                      </Badge>
                                    )}
                                    <div className="flex items-center gap-1">
                                      {[...Array(action.rarity)].map((_, i) => (
                                        <Sparkles key={i} className="w-3 h-3 fill-current" />
                                      ))}
                                    </div>
                                  </div>
                                  <div className="text-sm">
                                    {action.description && <p><span className="font-semibold">描述:</span> {action.description}</p>}
                                    <div className="pt-1">
                                      <span className="font-semibold">费用: </span>
                                      {action.cost && action.cost.length > 0 ? (
                                        <div className="flex flex-wrap gap-1 mt-1">
                                          {action.cost.map((costItem, index) => (
                                            <span key={index} className="inline-flex items-center gap-0.5 bg-secondary px-2 py-0.5 rounded-md text-xs">
                                              {(() => {
                                                const CostIcon = getElementIcon(costItem.type);
                                                return <CostIcon className="w-3 h-3" />;
                                              })()}
                                              {costItem.value}
                                            </span>
                                          ))}
                                        </div>
                                      ) : (
                                        <span>无费用</span>
                                      )}
                                    </div>
                                  </div>
                                  {action.skills && Array.isArray(action.skills) && action.skills.length > 0 && (
                                    <div className="pt-2 border-t">
                                      <h5 className="font-semibold mb-1">技能:</h5>
                                      <ul className="space-y-1">
                                        {action.skills.map((skill, idx) => (
                                          <li key={idx} className="text-sm">
                                            <span className="font-medium">{skill.name}</span>
                                            <div className="text-xs mt-1 ml-2">
                                              {skill.cost && Array.isArray(skill.cost) && skill.cost.length > 0 && (
                                                <div className="inline-flex flex-wrap gap-1 mr-2">
                                                  {skill.cost.map((cost, costIdx) => {
                                                    const CostIcon = getElementIcon(cost.type);
                                                    return (
                                                      <span key={costIdx} className="inline-flex items-center gap-0.5 bg-secondary px-1.5 py-0.5 rounded text-xs">
                                                        <CostIcon className="w-2.5 h-2.5" />
                                                        {cost.value}
                                                      </span>
                                                    );
                                                  })}
                                                </div>
                                              )}
                                            </div>
                                            <p className="mt-1">{skill.description}</p>
                                          </li>
                                        ))}
                                      </ul>
                                    </div>
                                  )}
                                </div>
                              </TooltipContent>
                            </Tooltip>
                          </TooltipProvider>
                        )
                      })}
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-40">
                      <p className="text-muted-foreground">
                        {actionCardsData ? "没有找到匹配的行动牌" : "正在加载行动牌数据..."}
                      </p>
                    </div>
                  )}
                </TabsContent>
              </Tabs>
            </div>

            {/* Deck Summary */}
            <div className="space-y-4">
              <Card className="sticky top-20">
                <CardContent className="p-6 space-y-4">
                  <div className="space-y-2">
                    <h3 className="font-bold text-lg">卡组概览</h3>
                    <p className="text-sm text-muted-foreground">{deckName || "未命名卡组"}</p>
                  </div>

                  <Separator />

                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">总卡牌数</span>
                      <span className="font-bold text-lg">{totalCards}/33</span>
                    </div>
                    <div className="h-2 bg-secondary rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary rounded-full transition-all"
                        style={{ width: `${(totalCards / 33) * 100}%` }}
                      />
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {totalCards < 33 ? `还需 ${33 - totalCards} 张牌` : totalCards > 33 ? "超过数量限制" : "卡组已满"}
                    </div>
                  </div>

                  <Separator />

                  {/* Selected Characters */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <h4 className="font-semibold text-sm">角色卡</h4>
                      <span className="text-sm text-muted-foreground">{selectedCharacters.length}/3</span>
                    </div>
                    {selectedCharacters.length > 0 ? (
                      <div className="space-y-2">
                        {selectedCharacters.map((id) => {
                          const char = charactersData?.find((c: CardType) => c.id === id)
                          if (!char) return null
                          return (
                            <div key={id} className="flex items-center justify-between p-2 rounded-lg bg-muted">
                              <div className="flex items-center gap-2">
                                <div className="w-6 h-6 rounded overflow-hidden">
                                  {char.image_url && !failedImagesMemo.has(char.id) ? (
                                    <img 
                                      src={char.image_url} 
                                      alt={char.name} 
                                      className="w-full h-full object-cover"
                                      onError={() => {
                                        setFailedImages(prev => new Set(prev).add(char.id))
                                      }}
                                    />
                                  ) : (
                                    <div className="w-full h-full bg-gradient-to-br from-primary/20 to-accent/10 flex items-center justify-center">
                                      {(() => {
                                        const Icon = getElementIcon(char.element_type || char.element || "")
                                        return <Icon className="w-4 h-4 text-primary" />
                                      })()}
                                    </div>
                                  )}
                                </div>
                                <span className="text-sm font-medium">{char.name}</span>
                              </div>
                              <Button size="sm" variant="ghost" onClick={() => removeCharacter(id)}>
                                <Trash2 className="w-3 h-3" />
                              </Button>
                            </div>
                          )
                        })}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">未选择角色</p>
                    )}
                  </div>

                  <Separator />

                  {/* Selected Actions */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <h4 className="font-semibold text-sm">行动牌</h4>
                      <span className="text-sm text-muted-foreground">
                        {selectedActions.reduce((sum, a) => sum + a.count, 0)}/30
                      </span>
                    </div>
                    {selectedActions.length > 0 ? (
                      <div className="space-y-2">
                        {selectedActions.map(({ id, count }) => {
                          const action = allActions.find((a: CardType) => a.id === id)
                          if (!action) return null
                          return (
                            <div key={id} className="flex items-center justify-between p-2 rounded-lg bg-muted">
                              <div className="flex items-center gap-2">
                                <div className="w-6 h-6 rounded overflow-hidden">
                                  {action.image_url && !failedImagesMemo.has(action.id) ? (
                                    <img 
                                      src={action.image_url} 
                                      alt={action.name} 
                                      className="w-full h-full object-cover"
                                      onError={() => {
                                        setFailedImages(prev => new Set(prev).add(action.id))
                                      }}
                                    />
                                  ) : (
                                    <div className="w-full h-full bg-gradient-to-br from-primary/20 to-accent/10 flex items-center justify-center">
                                      {(() => {
                                        const Icon = getElementIcon(action.element_type || action.element || "")
                                        return <Icon className="w-4 h-4 text-primary" />
                                      })()}
                                    </div>
                                  )}
                                </div>
                                <span className="text-sm font-medium">{action.name}</span>
                              </div>
                              <div className="flex items-center gap-2">
                                <Badge variant="secondary" className="text-xs">
                                  ×{count}
                                </Badge>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => {
                                    setSelectedActions(selectedActions.filter((a) => a.id !== id))
                                  }}
                                >
                                  <Trash2 className="w-3 h-3" />
                                </Button>
                              </div>
                            </div>
                          )
                        })}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">未选择行动牌</p>
                    )}
                  </div>

                  {totalCards === 33 && (
                    <div className="p-3 rounded-lg bg-primary/10 border border-primary/20">
                      <p className="text-sm text-primary font-medium text-center">卡组已完成！</p>
                    </div>
                  )}

                  {/* Validation Result */}
                  {validationResult && (
                    <div className="pt-4">
                      <Separator />
                      <div className="pt-4">
                        <h4 className="font-semibold text-sm mb-2">验证结果</h4>
                        {validationResult.valid ? (
                          <div className="flex items-center gap-2 text-green-600">
                            <CheckCircle className="w-4 h-4" />
                            <span>卡组有效</span>
                          </div>
                        ) : (
                          <div className="space-y-2">
                            <div className="flex items-center gap-2 text-red-600">
                              <AlertCircle className="w-4 h-4" />
                              <span>卡组无效</span>
                            </div>
                            <ul className="text-sm text-red-500 list-disc pl-5 space-y-1">
                              {validationResult.errors?.map((error, index) => (
                                <li key={index}>{error}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
