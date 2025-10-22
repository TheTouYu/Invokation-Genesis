"use client"

import { GameHeader } from "@/components/layout/game-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Plus, Layers, Edit, Trash2, Copy } from "lucide-react"
import Link from "next/link"
import useSWR from "swr"
import { getDecks } from "@/lib/api/decks"
import type { Deck } from "@/lib/api/types"

// SWR fetcher函数
const fetcher = (url: string) => fetch(url).then(res => res.json())

export default function DecksPage() {
  // 使用SWR获取卡组列表
  const { data: decksData, error, isLoading } = useSWR(
    '/api/decks', 
    getDecks,
    {
      onError: (error) => {
        if (error.message && error.message.startsWith('AUTH_ERROR:')) {
          // 重定向到登录页面已经在API客户端中处理
        }
      }
    }
  );

  // 加载状态
  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <GameHeader />
        <main className="flex-1 container py-8 flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
            <p className="text-lg">正在加载卡组数据...</p>
          </div>
        </main>
      </div>
    );
  }

  // 错误状态
  if (error) {
    return (
      <div className="min-h-screen flex flex-col">
        <GameHeader />
        <main className="flex-1 container py-8 flex items-center justify-center">
          <div className="text-center">
            <p className="text-lg text-destructive">加载卡组数据失败</p>
            <p className="text-sm text-muted-foreground">{error.message}</p>
          </div>
        </main>
      </div>
    );
  }

  // 获取卡组数据
  const decks = decksData?.decks || [];

  // 计算统计信息
  const totalWins = decks.reduce((sum, deck) => sum + (deck.wins || 0), 0);
  const totalGames = decks.reduce((sum, deck) => sum + (deck.wins || 0) + (deck.losses || 0), 0);
  const winRate = totalGames > 0 ? Math.round((totalWins / totalGames) * 100) : 0;
  const mostUsedDeck = decks.length > 0 ? decks[0] : null; // 简化：假设第一个是最常用的

  return (
    <div className="min-h-screen flex flex-col">
      <GameHeader />

      <main className="flex-1 container py-8">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <h1 className="text-4xl font-bold tracking-tight">我的卡组</h1>
              <p className="text-muted-foreground text-lg">管理你的所有卡组配置</p>
            </div>
            <Button asChild size="lg" className="gap-2">
              <Link href="/decks/builder">
                <Plus className="w-4 h-4" />
                创建新卡组
              </Link>
            </Button>
          </div>

          {/* Deck Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardDescription>总卡组数</CardDescription>
                <CardTitle className="text-3xl">{decks.length}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">最多可创建 10 个</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>总胜场</CardDescription>
                <CardTitle className="text-3xl">{totalWins}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  胜率 {winRate}%
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>最常用卡组</CardDescription>
                <CardTitle className="text-xl truncate">
                  {mostUsedDeck ? mostUsedDeck.name : '暂无卡组'}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {mostUsedDeck ? (mostUsedDeck.wins || 0) + (mostUsedDeck.losses || 0) + ' 场对战' : '暂无卡组'}
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Decks Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {decks.length > 0 ? (
              decks.map((deck: Deck) => {
                // 计算胜率
                const winRate = (deck.wins || 0) / ((deck.wins || 0) + (deck.losses || 0));
                
                return (
                  <Card key={deck.id} className="hover:border-primary/40 transition-colors">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="space-y-1 flex-1">
                          <CardTitle className="text-2xl">{deck.name}</CardTitle>
                          <CardDescription>{deck.cards?.length || 0} 张卡牌</CardDescription>
                        </div>
                        <Layers className="w-6 h-6 text-muted-foreground" />
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {/* Characters - 这里需要从卡牌信息中提取角色 */}
                      <div>
                        <div className="text-sm text-muted-foreground mb-2">角色配置</div>
                        <div className="flex flex-wrap gap-2">
                          {(deck.cards as Array<any>)?.filter((card: any) => 
                            typeof card === 'object' && card.type === '角色牌'
                          ).slice(0, 3).map((card: any, i) => (
                            <Badge key={i} variant="secondary">
                              {typeof card === 'object' ? card.name : card}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      {/* Stats */}
                      <div>
                        <div className="flex items-center justify-between text-sm mb-2">
                          <span className="text-muted-foreground">战绩</span>
                          <span className="font-medium">
                            {deck.wins || 0}胜 {deck.losses || 0}负
                          </span>
                        </div>
                        <div className="h-2 bg-secondary rounded-full overflow-hidden">
                          <div
                            className="h-full bg-primary rounded-full transition-all"
                            style={{ width: `${winRate * 100}%` }}
                          />
                        </div>
                      </div>

                      <div className="flex items-center justify-between pt-2">
                        <span className="text-sm text-muted-foreground">最后更新: {new Date(deck.updated_at || deck.created_at).toLocaleDateString()}</span>
                      </div>

                      {/* Actions */}
                      <div className="flex gap-2 pt-2">
                        <Button asChild variant="default" className="flex-1">
                          <Link href={`/decks/${deck.id}`}>查看详情</Link>
                        </Button>
                        <Button variant="outline" size="icon">
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button variant="outline" size="icon">
                          <Copy className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="icon"
                          className="text-destructive hover:text-destructive bg-transparent"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                );
              })
            ) : (
              <div className="col-span-full text-center py-12">
                <p className="text-lg text-muted-foreground">还没有创建任何卡组</p>
                <p className="text-sm text-muted-foreground mt-2">点击上方按钮创建你的第一个卡组</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
