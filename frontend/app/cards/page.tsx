"use client"

import { GameHeader } from "@/components/layout/game-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Search, Filter, Sparkles, Zap, Droplet, Flame, Wind, Leaf, Mountain, Snowflake } from "lucide-react"
import Link from "next/link"
import { useState } from "react"
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
  return elementIcons[element as keyof typeof elementIcons] || Sparkles;
};

export default function CardsPage() {
  const [searchQuery, setSearchQuery] = useState("")
  
  // 使用SWR获取角色牌数据
  const characterFilters: CardFilters = { type: "角色牌", search: searchQuery }
  const { data: characterData, error: characterError, isLoading: characterLoading } = useSWR(
    `/api/cards?type=${encodeURIComponent("角色牌")}${searchQuery ? `&search=${encodeURIComponent(searchQuery)}` : ""}`,
    () => getCards(characterFilters)
  )
  
  // 使用SWR获取行动牌数据
  const actionFilters: CardFilters = { type: "行动牌", search: searchQuery }
  const { data: actionData, error: actionError, isLoading: actionLoading } = useSWR(
    `/api/cards?type=${encodeURIComponent("行动牌")}${searchQuery ? `&search=${encodeURIComponent(searchQuery)}` : ""}`,
    () => getCards(actionFilters)
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
                              <div className="w-8 h-8 rounded-full bg-background/90 backdrop-blur flex items-center justify-center font-bold">
                                {card.cost?.length || 0}
                              </div>
                            </div>
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
                              <div className="w-8 h-8 rounded-full bg-background/90 backdrop-blur flex items-center justify-center font-bold">
                                {card.cost?.length || 0}
                              </div>
                            </div>
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
