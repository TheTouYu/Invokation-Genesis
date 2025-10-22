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
import React from "react"

export default function CardDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = React.use(params);

  // 使用SWR获取卡牌详情
  const { data: cardDetail, error, isLoading } = useSWR(
    `/api/cards/${id}`,
    () => getCardDetail(id),
    {
      refreshInterval: 0, // 不自动刷新
      revalidateOnFocus: false, // 窗口聚焦时不重新验证
      onError: (error) => {
        if (error.message && error.message.startsWith('AUTH_ERROR:')) {
          // 重定向到登录页面已经在API客户端中处理
        }
      }
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
      充能: Zap,
      无色: Sparkles,
    };

    return elementIcons[element?.toLowerCase() || element || ''] || Sparkles;
  };
  
  // 根据技能类型选择图标
  const getSkillTypeIcon = (skillType: string) => {
    const skillTypeIcons: Record<string, any> = {
      '普通攻击': Droplet, // 使用水元素图标表示普通攻击
      '元素战技': Zap,    // 使用雷元素图标表示元素战技
      '元素爆发': Flame,  // 使用火元素图标表示元素爆发
      '被动技能': Leaf,   // 使用草元素图标表示被动技能
    };

    return skillTypeIcons[skillType] || Sparkles;
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
                      <div className="absolute top-4 right-4">
                        <Badge variant="secondary" className="gap-1">
                          {[...Array(card.rarity)].map((_, i) => (
                            <Sparkles key={i} className="w-3 h-3 fill-current" />
                          ))}
                        </Badge>
                      </div>
                      <div className="absolute bottom-4 left-4">
                        <div className="flex flex-wrap gap-1">
                          {card.cost && card.cost.map((costItem, index) => {
                            const CostIcon = getElementIcon(costItem.type);
                            return (
                              <div 
                                key={index} 
                                className="w-8 h-8 rounded-full bg-background/90 backdrop-blur flex items-center justify-center font-bold text-sm"
                              >
                                <div className="flex items-center gap-1">
                                  {React.createElement(CostIcon, { className: "w-4 h-4" })}
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
                        <div className="flex flex-wrap gap-1">
                          {card.cost && card.cost.map((costItem, index) => {
                            const CostIcon = getElementIcon(costItem.type);
                            return (
                              <div 
                                key={index} 
                                className="w-8 h-8 rounded-full bg-background/90 backdrop-blur flex items-center justify-center font-bold text-sm"
                              >
                                <div className="flex items-center gap-1">
                                  {React.createElement(CostIcon, { className: "w-4 h-4" })}
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
                              <div className="flex items-center gap-2">
                                <h4 className="font-medium">{skill.name}</h4>
                                <Badge variant="outline" className="text-xs flex items-center gap-1">
                                  {React.createElement(getSkillTypeIcon(skill.type), { className: "w-3 h-3" })}
                                  {skill.type}
                                </Badge>
                              </div>
                              <div className="flex flex-wrap justify-end gap-1 ml-2">
                                {skill.cost && skill.cost.map((costItem, costIndex) => {
                                  const CostIcon = getElementIcon(costItem.type);
                                  return (
                                    <div 
                                      key={costIndex} 
                                      className="flex items-center gap-1 px-2 py-1 rounded-full bg-muted text-xs"
                                    >
                                      {React.createElement(CostIcon, { className: "w-3 h-3" })}
                                      {costItem.value > 0 ? costItem.value : ''}
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                            <p className="text-sm text-muted-foreground">{skill.description}</p>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}

                {(card.health !== undefined || card.max_health !== undefined || card.energy !== undefined || card.max_energy !== undefined || card.weapon_type) && (
                  <div>
                    <h3 className="font-semibold mb-2">角色属性</h3>
                    <div className="grid grid-cols-2 gap-3">
                      {card.max_health !== undefined && (
                        <div className="p-3 rounded-lg bg-muted">
                          <div className="text-sm text-muted-foreground mb-1">最大生命值</div>
                          <div className="text-2xl font-bold">{card.max_health}</div>
                        </div>
                      )}
                      {card.health !== undefined && card.health !== card.max_health && (
                        <div className="p-3 rounded-lg bg-muted">
                          <div className="text-sm text-muted-foreground mb-1">当前生命值</div>
                          <div className="text-2xl font-bold">{card.health}</div>
                        </div>
                      )}
                      {card.max_energy !== undefined && (
                        <div className="p-3 rounded-lg bg-muted">
                          <div className="text-sm text-muted-foreground mb-1">最大能量</div>
                          <div className="text-2xl font-bold">{card.max_energy}</div>
                        </div>
                      )}
                      {card.energy !== undefined && (
                        <div className="p-3 rounded-lg bg-muted">
                          <div className="text-sm text-muted-foreground mb-1">当前能量</div>
                          <div className="text-2xl font-bold">{card.energy}</div>
                        </div>
                      )}
                      {card.weapon_type && (
                        <div className="p-3 rounded-lg bg-muted col-span-2">
                          <div className="text-sm text-muted-foreground mb-1">武器类型</div>
                          <div className="text-xl font-bold">{card.weapon_type}</div>
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
