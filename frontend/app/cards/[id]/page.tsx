"use client"

import { GameHeader } from "@/components/layout/game-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { ArrowLeft, Sparkles, Zap, Plus, Flame, Wind, Leaf, Mountain, Snowflake, Droplet } from "lucide-react"
import Link from "next/link"
import useSWR from 'swr'
import { getCardDetail } from "@/lib/api/cards"
import { Card as CardType } from "@/lib/api/types"
import { notFound } from "next/navigation"

export default function CardDetailPage({ params }: { params: { id: string } }) {
  const { id } = params;

  // 使用SWR获取卡牌详情
  const { data: cardDetail, error, isLoading } = useSWR(
    `/api/cards/${id}`,
    () => getCardDetail(id),
    {
      refreshInterval: 0, // 不自动刷新
      revalidateOnFocus: false, // 窗口聚焦时不重新验证
    }
  );

  // 如果卡牌不存在，显示404页面
  if (error && error.status === 404) {
    notFound();
  }

  // 加载状态
  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <GameHeader />
        <main className="flex-1 container py-8 flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
            <p className="text-lg">正在加载卡牌详情...</p>
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
            <p className="text-lg text-destructive">加载卡牌详情失败</p>
            <p className="text-sm text-muted-foreground">{error.message}</p>
          </div>
        </main>
      </div>
    );
  }

  // 获取卡牌数据
  const card: CardType | undefined = cardDetail?.card;

  if (!card) {
    return (
      <div className="min-h-screen flex flex-col">
        <GameHeader />
        <main className="flex-1 container py-8 flex items-center justify-center">
          <div className="text-center">
            <p className="text-lg text-destructive">卡牌数据不存在</p>
          </div>
        </main>
      </div>
    );
  }

  // 根据元素类型选择图标
  const getElementIcon = (element: string) => {
    const elementIcons: Record<string, any> = {
      electro: Zap,
      hydro: Droplet,
      pyro: Flame,
      anemo: Wind,
      dendro: Leaf,
      geo: Mountain,
      cryo: Snowflake,
    };

    return elementIcons[element?.toLowerCase() || ''] || Zap;
  };

  const ElementIcon = getElementIcon(card.element || card.element_type || '');

  return (
    <div className="min-h-screen flex flex-col">
      <GameHeader />

      <main className="flex-1 container py-8">
        <div className="max-w-5xl mx-auto space-y-6">
          {/* Back Button */}
          <Button asChild variant="ghost" className="gap-2">
            <Link href="/cards">
              <ArrowLeft className="w-4 h-4" />
              返回图鉴
            </Link>
          </Button>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Card Display */}
            <div className="space-y-4">
              <Card className="overflow-hidden">
                <div className="aspect-[3/4] bg-gradient-to-br from-primary/20 via-accent/10 to-background relative">
                  <div className="absolute inset-0 flex items-center justify-center">
                    <ElementIcon className="w-48 h-48 text-primary/20" />
                  </div>
                  <div className="absolute top-4 right-4">
                    <Badge variant="secondary" className="gap-1">
                      {[...Array(card.rarity)].map((_, i) => (
                        <Sparkles key={i} className="w-3 h-3 fill-current" />
                      ))}
                    </Badge>
                  </div>
                  <div className="absolute bottom-4 left-4">
                    <div className="w-12 h-12 rounded-full bg-background/90 backdrop-blur flex items-center justify-center font-bold text-xl">
                      {card.cost?.length || 0}
                    </div>
                  </div>
                </div>
              </Card>

              <Button className="w-full gap-2" size="lg">
                <Plus className="w-4 h-4" />
                添加到卡组
              </Button>
            </div>

            {/* Card Info */}
            <div className="space-y-6">
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <h1 className="text-4xl font-bold">{card.title ? `${card.title} - ${card.name}` : card.name}</h1>
                  <Badge variant="outline" className="gap-1">
                    <ElementIcon className="w-3 h-3" />
                    {(card.element || card.element_type) || '未知元素'}
                  </Badge>
                </div>
                <p className="text-muted-foreground text-lg">{card.type} · {card.country || '未知国家'}</p>
              </div>

              <Separator />

              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold mb-2">卡牌描述</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {card.description || '暂无卡牌描述'}
                  </p>
                </div>

                {card.skills && card.skills.length > 0 && (
                  <div>
                    <h3 className="font-semibold mb-3">技能</h3>
                    <div className="space-y-3">
                      {card.skills.map((skill, index) => (
                        <Card 
                          key={index} 
                          className={index === card.skills!.length - 1 ? "border-primary/40" : ""}
                        >
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between mb-2">
                              <h4 className="font-medium">{skill.name}</h4>
                              <Badge 
                                variant={index === card.skills!.length - 1 ? "default" : "secondary"}
                                className={index === card.skills!.length - 1 ? "bg-primary" : ""}
                              >
                                {skill.cost?.length || 0}费
                              </Badge>
                            </div>
                            <p className="text-sm text-muted-foreground">{skill.description}</p>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}

                {(card.health || card.max_health || card.energy) && (
                  <div>
                    <h3 className="font-semibold mb-2">卡牌属性</h3>
                    <div className="grid grid-cols-2 gap-3">
                      {card.max_health !== undefined && (
                        <div className="p-3 rounded-lg bg-muted">
                          <div className="text-sm text-muted-foreground mb-1">生命值</div>
                          <div className="text-2xl font-bold">{card.max_health}</div>
                        </div>
                      )}
                      {card.energy !== undefined && (
                        <div className="p-3 rounded-lg bg-muted">
                          <div className="text-sm text-muted-foreground mb-1">能量</div>
                          <div className="text-2xl font-bold">{card.energy}</div>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
