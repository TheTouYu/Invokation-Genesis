"use client"

import { GameHeader } from "@/components/layout/game-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Search, Filter, Sparkles, Zap, Droplet, Flame, Wind, Leaf, Mountain, Snowflake, X } from "lucide-react"
import Link from "next/link"
import { useState } from "react"
import React from "react"
import useSWR from "swr"
import { getCards, getCharacterFilters } from "@/lib/api/cards"
import type { Card as CardType, CardFilters } from "@/lib/api/types"

const elementIcons = {
  electro: Zap,
  hydro: Droplet,
  pyro: Flame,
  anemo: Wind,
  dendro: Leaf,
  geo: Mountain,
  cryo: Snowflake,
}

// SWR fetcher函数
const fetcher = (url: string) => fetch(url).then(res => res.json())

// 根据卡牌类型获取图标
const getElementTypeIcon = (element: string) => {
  const elementIcons: Record<string, any> = {
    electro: Zap,
    hydro: Droplet,
    pyro: Flame,
    anemo: Wind,
    dendro: Leaf,
    geo: Mountain,
    cryo: Snowflake,
    充能: Zap,
    无色: Sparkles,
    冰: Snowflake,
    水: Droplet,
    火: Flame,
    雷: Zap,
    风: Wind,
    岩: Mountain,
    草: Leaf,
  };

  return elementIcons[element?.toLowerCase() || element || ''] || Sparkles;
};

export default function CardsPage() {
  const [searchQuery, setSearchQuery] = useState("")
  const [elementFilter, setElementFilter] = useState("")
  const [countryFilter, setCountryFilter] = useState("")
  const [weaponTypeFilter, setWeaponTypeFilter] = useState("")
  const [characterSubtypeFilter, setCharacterSubtypeFilter] = useState("")
  const [rarityFilter, setRarityFilter] = useState<number | null>(null)
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  
  // 可选标签
  const availableTags = ["充能", "卡牌", "舍弃", "调和", "伤害"]
  
  // 切换标签
  const toggleTag = (tag: string) => {
    setSelectedTags(prev => 
      prev.includes(tag) 
        ? prev.filter(t => t !== tag) 
        : [...prev, tag]
    )
  }
  
  // 使用SWR获取角色牌数据
  const characterFilters: CardFilters = { 
    type: "角色牌", 
    search: searchQuery,
    element: elementFilter,
    country: countryFilter,
    weapon_type: weaponTypeFilter,
    character_subtype: characterSubtypeFilter,
    rarity: rarityFilter || undefined,
    tag: selectedTags.length > 0 ? selectedTags : undefined
  }
  const { data: characterData, error: characterError, isLoading: characterLoading } = useSWR(
    JSON.stringify(characterFilters), // 使用filters对象作为key
    () => getCards(characterFilters),
    {
      onError: (error) => {
        if (error.message && error.message.startsWith('AUTH_ERROR:')) {
          // 重定向到登录页面已经在API客户端中处理
        }
      }
    }
  )
  
  // 使用SWR获取行动牌数据
  const actionFilters: CardFilters = { 
    type: "行动牌", 
    search: searchQuery,
    element: elementFilter,
    country: countryFilter,
    weapon_type: weaponTypeFilter,
    character_subtype: characterSubtypeFilter,
    rarity: rarityFilter || undefined,
    tag: selectedTags.length > 0 ? selectedTags : undefined
  }
  const { data: actionData, error: actionError, isLoading: actionLoading } = useSWR(
    JSON.stringify(actionFilters), // 使用filters对象作为key
    () => getCards(actionFilters),
    {
      onError: (error) => {
        if (error.message && error.message.startsWith('AUTH_ERROR:')) {
          // 重定向到登录页面已经在API客户端中处理
        }
      }
    }
  )

  // 显示加载状态
  if (characterLoading || actionLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <GameHeader />
        <main className="flex-1 container py-8 flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
            <p className="text-lg">正在加载卡牌数据...</p>
          </div>
        </main>
      </div>
    );
  }

  // 错误处理
  if (characterError || actionError) {
    return (
      <div className="min-h-screen flex flex-col">
        <GameHeader />
        <main className="flex-1 container py-8 flex items-center justify-center">
          <div className="text-center">
            <p className="text-lg text-destructive">加载卡牌数据失败</p>
            <p className="text-sm text-muted-foreground">{characterError?.message || actionError?.message}</p>
          </div>
        </main>
      </div>
    );
  }

  // 获取卡牌数据
  const characterCards = characterData?.cards || [];
  const actionCards = actionData?.cards || [];

  return (
    <div className="min-h-screen flex flex-col">
      <GameHeader />

      <main className="flex-1 container py-8">
        <div className="space-y-6">
          {/* Header */}
          <div className="space-y-2">
            <h1 className="text-4xl font-bold tracking-tight">卡牌图鉴</h1>
            <p className="text-muted-foreground text-lg">浏览和收集所有卡牌</p>
          </div>

          {/* Search and Filter */}
          <div className="flex flex-col gap-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  placeholder="搜索卡牌名称..."
                  className="pl-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Button variant="outline" className="gap-2 bg-transparent">
                <Filter className="w-4 h-4" />
                筛选
              </Button>
            </div>
            
            {/* Filter Options */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="text-sm font-medium text-muted-foreground mb-1 block">元素</label>
                <select 
                  className="w-full p-2 border rounded-md bg-background"
                  value={elementFilter}
                  onChange={(e) => setElementFilter(e.target.value)}
                >
                  <option value="">全部</option>
                  <option value="火">火</option>
                  <option value="水">水</option>
                  <option value="雷">雷</option>
                  <option value="风">风</option>
                  <option value="岩">岩</option>
                  <option value="草">草</option>
                  <option value="冰">冰</option>
                </select>
              </div>
              
              <div>
                <label className="text-sm font-medium text-muted-foreground mb-1 block">国家</label>
                <select 
                  className="w-full p-2 border rounded-md bg-background"
                  value={countryFilter}
                  onChange={(e) => setCountryFilter(e.target.value)}
                >
                  <option value="">全部</option>
                  <option value="蒙德">蒙德</option>
                  <option value="璃月">璃月</option>
                  <option value="稻妻">稻妻</option>
                  <option value="须弥">须弥</option>
                  <option value="枫丹">枫丹</option>
                  <option value="纳塔">纳塔</option>
                  <option value="至冬">至冬</option>
                </select>
              </div>
              
              <div>
                <label className="text-sm font-medium text-muted-foreground mb-1 block">武器类型</label>
                <select 
                  className="w-full p-2 border rounded-md bg-background"
                  value={weaponTypeFilter}
                  onChange={(e) => setWeaponTypeFilter(e.target.value)}
                >
                  <option value="">全部</option>
                  <option value="单手剑">单手剑</option>
                  <option value="双手剑">双手剑</option>
                  <option value="长柄武器">长柄武器</option>
                  <option value="弓">弓</option>
                  <option value="法器">法器</option>
                </select>
              </div>
              
              <div>
                <label className="text-sm font-medium text-muted-foreground mb-1 block">稀有度</label>
                <select 
                  className="w-full p-2 border rounded-md bg-background"
                  value={rarityFilter || ""}
                  onChange={(e) => setRarityFilter(e.target.value ? parseInt(e.target.value) : null)}
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
            
            {/* Tag Selection */}
            <div>
              <label className="text-sm font-medium text-muted-foreground mb-2 block">标签</label>
              <div className="flex flex-wrap gap-2">
                {availableTags.map((tag) => (
                  <Badge 
                    key={tag}
                    variant={selectedTags.includes(tag) ? "default" : "outline"}
                    className="cursor-pointer"
                    onClick={() => toggleTag(tag)}
                  >
                    {tag}
                    {selectedTags.includes(tag) && (
                      <X className="ml-1 h-3 w-3" />
                    )}
                  </Badge>
                ))}
              </div>
            </div>
          </div>

          {/* Tabs */}
          <Tabs defaultValue="characters" className="space-y-6">
            <TabsList className="grid w-full max-w-md grid-cols-2">
              <TabsTrigger value="characters">角色牌</TabsTrigger>
              <TabsTrigger value="actions">行动牌</TabsTrigger>
            </TabsList>

            <TabsContent value="characters" className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {characterCards.length > 0 ? (
                  characterCards.map((card: CardType) => {
                    const ElementIcon = getElementTypeIcon(card.element || card.element_type || '')
                    return (
                      <Link key={card.id} href={`/cards/${card.id}`}>
                        <Card className="overflow-hidden hover:border-primary/40 transition-all hover:shadow-lg hover:shadow-primary/10 cursor-pointer group">
                          <div className="aspect-[3/4] bg-gradient-to-br from-primary/20 via-accent/10 to-background relative overflow-hidden">
                            {card.image_url ? (
                              <div className="w-full h-full relative">
                                <img 
                                  src={card.image_url} 
                                  alt={card.name} 
                                  className="w-full h-full object-cover"
                                  onError={(e) => {
                                    const target = e.target as HTMLImageElement;
                                    target.onerror = null; // 避免无限循环
                                    target.style.display = 'none';
                                  }}
                                />
                                <div className="absolute top-3 right-3">
                                  <Badge variant="secondary" className="gap-1">
                                    {[...Array(card.rarity)].map((_, i) => (
                                      <Sparkles key={i} className="w-3 h-3 fill-current" />
                                    ))}
                                  </Badge>
                                </div>
                                <div className="absolute bottom-3 left-3">
                                  <div className="flex flex-wrap gap-1">
                                    {card.cost && card.cost.map((costItem, index) => {
                                      const CostIcon = getElementTypeIcon(costItem.type);
                                      return (
                                        <div 
                                          key={index} 
                                          className="w-6 h-6 rounded-full bg-background/90 backdrop-blur flex items-center justify-center font-bold text-xs"
                                        >
                                          <div className="flex items-center gap-0.5">
                                            {React.createElement(CostIcon, { className: "w-3 h-3" })}
                                            {costItem.value}
                                          </div>
                                        </div>
                                      );
                                    })}
                                  </div>
                                </div>
                              </div>
                            ) : (
                              <>
                                <div className="absolute inset-0 flex items-center justify-center">
                                  <ElementIcon className="w-24 h-24 text-primary/20 group-hover:scale-110 transition-transform" />
                                </div>
                                <div className="absolute top-3 right-3">
                                  <Badge variant="secondary" className="gap-1">
                                    {[...Array(card.rarity)].map((_, i) => (
                                      <Sparkles key={i} className="w-3 h-3 fill-current" />
                                    ))}
                                  </Badge>
                                </div>
                                <div className="absolute bottom-3 left-3">
                                  <div className="flex flex-wrap gap-1">
                                    {card.cost && card.cost.map((costItem, index) => {
                                      const CostIcon = getElementTypeIcon(costItem.type);
                                      return (
                                        <div 
                                          key={index} 
                                          className="w-6 h-6 rounded-full bg-background/90 backdrop-blur flex items-center justify-center font-bold text-xs"
                                        >
                                          <div className="flex items-center gap-0.5">
                                            {React.createElement(CostIcon, { className: "w-3 h-3" })}
                                            {costItem.value}
                                          </div>
                                        </div>
                                      );
                                    })}
                                  </div>
                                </div>
                              </>
                            )}
                          </div>
                          <CardContent className="p-4">
                            <h3 className="font-bold text-lg mb-1">{card.title ? `${card.title} - ${card.name}` : card.name}</h3>
                            <div className="flex items-center gap-2">
                              <ElementIcon className="w-4 h-4 text-primary" />
                              <span className="text-sm text-muted-foreground capitalize">{card.element || card.element_type}</span>
                            </div>
                          </CardContent>
                        </Card>
                      </Link>
                    )
                  })
                ) : (
                  <div className="col-span-full text-center py-8">
                    <p className="text-muted-foreground">没有找到匹配的角色牌</p>
                  </div>
                )}
              </div>
            </TabsContent>

            <TabsContent value="actions" className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {actionCards.length > 0 ? (
                  actionCards.map((card: CardType) => {
                    const ElementIcon = getElementTypeIcon(card.element || card.element_type || '')
                    return (
                      <Link key={card.id} href={`/cards/${card.id}`}>
                        <Card className="overflow-hidden hover:border-accent/40 transition-all hover:shadow-lg hover:shadow-accent/10 cursor-pointer group">
                          <div className="aspect-[3/4] bg-gradient-to-br from-accent/20 via-chart-2/10 to-background relative overflow-hidden">
                            {card.image_url ? (
                              <div className="w-full h-full relative">
                                <img 
                                  src={card.image_url} 
                                  alt={card.name} 
                                  className="w-full h-full object-cover"
                                  onError={(e) => {
                                    const target = e.target as HTMLImageElement;
                                    target.onerror = null; // 避免无限循环
                                    target.style.display = 'none';
                                  }}
                                />
                                <div className="absolute top-3 right-3">
                                  <Badge variant="secondary" className="gap-1">
                                    {[...Array(card.rarity)].map((_, i) => (
                                      <Sparkles key={i} className="w-3 h-3 fill-current" />
                                    ))}
                                  </Badge>
                                </div>
                                <div className="absolute bottom-3 left-3">
                                  <div className="flex flex-wrap gap-1">
                                    {card.cost && card.cost.map((costItem, index) => {
                                      const CostIcon = getElementTypeIcon(costItem.type);
                                      return (
                                        <div 
                                          key={index} 
                                          className="w-6 h-6 rounded-full bg-background/90 backdrop-blur flex items-center justify-center font-bold text-xs"
                                        >
                                          <div className="flex items-center gap-0.5">
                                            {React.createElement(CostIcon, { className: "w-3 h-3" })}
                                            {costItem.value}
                                          </div>
                                        </div>
                                      );
                                    })}
                                  </div>
                                </div>
                              </div>
                            ) : (
                              <>
                                <div className="absolute inset-0 flex items-center justify-center">
                                  <ElementIcon className="w-24 h-24 text-accent/20 group-hover:scale-110 transition-transform" />
                                </div>
                                <div className="absolute top-3 right-3">
                                  <Badge variant="secondary" className="gap-1">
                                    {[...Array(card.rarity)].map((_, i) => (
                                      <Sparkles key={i} className="w-3 h-3 fill-current" />
                                    ))}
                                  </Badge>
                                </div>
                                <div className="absolute bottom-3 left-3">
                                  <div className="flex flex-wrap gap-1">
                                    {card.cost && card.cost.map((costItem, index) => {
                                      const CostIcon = getElementTypeIcon(costItem.type);
                                      return (
                                        <div 
                                          key={index} 
                                          className="w-6 h-6 rounded-full bg-background/90 backdrop-blur flex items-center justify-center font-bold text-xs"
                                        >
                                          <div className="flex items-center gap-0.5">
                                            {React.createElement(CostIcon, { className: "w-3 h-3" })}
                                            {costItem.value}
                                          </div>
                                        </div>
                                      );
                                    })}
                                  </div>
                                </div>
                              </>
                            )}
                          </div>
                          <CardContent className="p-4">
                            <h3 className="font-bold text-lg mb-1">{card.name}</h3>
                            <Badge variant="outline" className="text-xs">
                              {card.type}
                            </Badge>
                          </CardContent>
                        </Card>
                      </Link>
                    )
                  })
                ) : (
                  <div className="col-span-full text-center py-8">
                    <p className="text-muted-foreground">没有找到匹配的行动牌</p>
                  </div>
                )}
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  )
}
