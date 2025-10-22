"use client"

import { GameHeader } from "@/components/layout/game-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { ArrowLeft, Save, Sparkles, Zap, Droplet, Flame, Plus, Minus, Trash2, Swords, Shield, Target, RotateCcw, AlertCircle, CheckCircle } from "lucide-react"
import Link from "next/link"
import { useState, useEffect, useMemo } from "react"
import useSWR from "swr"
import { getCharacters, getEquipments, getSupports, getEvents } from "@/lib/api/cards"
import { createDeck, updateDeck, validateDeck } from "@/lib/api/decks"
import { Card as CardType, ValidateDeckRequest, DeckValidationResponse } from "@/lib/api/types"
import { toast } from "sonner"
import { useAuth } from "@/hooks/use-auth"

// SWR fetcher函数
const fetcher = (url: string) => fetch(url).then(res => res.json())

export default function DeckBuilderPage() {
  const { user, isAuthenticated } = useAuth()
  const [failedImages, setFailedImages] = useState<Set<string>>(new Set())
  
  // 记忆化已失败的图片集合，以提高性能
  const failedImagesMemo = useMemo(() => failedImages, [failedImages])
  const [deckName, setDeckName] = useState("")
  const [selectedCharacters, setSelectedCharacters] = useState<string[]>([])
  const [selectedActions, setSelectedActions] = useState<{ id: string; count: number }[]>([])
  const [validationResult, setValidationResult] = useState<DeckValidationResponse | null>(null)
  const [isSaving, setIsSaving] = useState(false)

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
  
  // 使用SWR获取角色数据
  const charactersSWR = useSWR("/api/characters", getCharacters, {
    refreshInterval: 0, // 不自动刷新
    revalidateOnFocus: false, // 窗口聚焦时不重新验证
    revalidateOnReconnect: false, // 重连时不重新验证
    dedupingInterval: 0, // 禁用去重
    focusThrottleInterval: 0, // 禁用焦点节流
  })
  const { data: charactersData, error: charactersError } = charactersSWR
  
  // 使用SWR获取行动牌数据（包括装备、支援、事件）
  const equipmentsSWR = useSWR("/api/equipments", getEquipments, {
    refreshInterval: 0, // 不自动刷新
    revalidateOnFocus: false, // 窗口聚焦时不重新验证
    revalidateOnReconnect: false, // 重连时不重新验证
    dedupingInterval: 0, // 禁用去重
    focusThrottleInterval: 0, // 禁用焦点节流
  })
  const { data: equipmentsData, error: equipmentsError } = equipmentsSWR
  
  const supportsSWR = useSWR("/api/supports", getSupports, {
    refreshInterval: 0, // 不自动刷新
    revalidateOnFocus: false, // 窗口聚焦时不重新验证
    revalidateOnReconnect: false, // 重连时不重新验证
    dedupingInterval: 0, // 禁用去重
    focusThrottleInterval: 0, // 禁用焦点节流
  })
  const { data: supportsData, error: supportsError } = supportsSWR
  
  const eventsSWR = useSWR("/api/events", getEvents, {
    refreshInterval: 0, // 不自动刷新
    revalidateOnFocus: false, // 窗口聚焦时不重新验证
    revalidateOnReconnect: false, // 重连时不重新验证
    dedupingInterval: 0, // 禁用去重
    focusThrottleInterval: 0, // 禁用焦点节流
  })
  const { data: eventsData, error: eventsError } = eventsSWR

  // 合并所有行动牌
  const allActions = [
    ...(equipmentsData || []),
    ...(supportsData || []),
    ...(eventsData || [])
  ]

  // 检查数据是否已加载
  if (!charactersData || !equipmentsData || !supportsData || !eventsData) {
    return <div className="flex items-center justify-center h-40">
      <p className="text-muted-foreground">正在加载卡牌数据...</p>
    </div>
  }

  // 处理加载和错误状态
  if (charactersError || equipmentsError || supportsError || eventsError) {
    console.error("加载卡牌数据失败:", { 
      charactersError, 
      equipmentsError, 
      supportsError, 
      eventsError 
    })
    return <div>加载卡牌数据失败</div>
  }

  // 组件挂载时重新验证数据
  useEffect(() => {
    if (typeof window !== 'undefined') { // 确保在客户端执行
      // 重新验证所有SWR数据
      charactersSWR.mutate()
      equipmentsSWR.mutate()
      supportsSWR.mutate()
      eventsSWR.mutate()
    }
  }, [])

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

              <Tabs defaultValue="characters" className="space-y-4">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="characters">选择角色 ({selectedCharacters.length}/3)</TabsTrigger>
                  <TabsTrigger value="actions">
                    选择行动牌 ({selectedActions.reduce((sum, a) => sum + a.count, 0)}/30)
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="characters" className="space-y-4">
                  {charactersData ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {charactersData.map((char: CardType) => {
                        const isSelected = selectedCharacters.includes(char.id)
                        return (
                          <Card
                            key={char.id}
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
                        )
                      })}
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-40">
                      <p className="text-muted-foreground">正在加载角色数据...</p>
                    </div>
                  )}
                </TabsContent>

                <TabsContent value="actions" className="space-y-4">
                  {allActions.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      {allActions.map((action: CardType) => {
                        const selected = selectedActions.find((a) => a.id === action.id)
                        const count = selected?.count || 0
                        return (
                          <Card
                            key={action.id}
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
                        )
                      })}
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-40">
                      <p className="text-muted-foreground">正在加载行动牌数据...</p>
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
