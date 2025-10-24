import { Sparkles, Zap, Droplet, Flame, Wind, Leaf, Mountain, Snowflake, X } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import Link from "next/link";
import { CardType } from "@/lib/api/types";
import React from "react";

interface CardGridProps {
  cards: CardType[];
  cardType: 'characters' | 'actions';
}

export function CardGrid({ cards, cardType }: CardGridProps) {
  const elementIcons = {
    electro: Zap,
    hydro: Droplet,
    pyro: Flame,
    anemo: Wind,
    dendro: Leaf,
    geo: Mountain,
    cryo: Snowflake,
  };

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

  if (cards.length === 0) {
    return (
      <div className="col-span-full text-center py-8">
        <p className="text-muted-foreground">
          {cardType === 'characters' ? '没有找到匹配的角色牌' : '没有找到匹配的行动牌'}
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card: CardType) => {
        const ElementIcon = getElementTypeIcon(card.element || card.element_type || '');
        // 解析技能数据（如果技能是JSON字符串）
        let processedCard = card;
        if (typeof card.skills === 'string') {
          try {
            processedCard = { ...card, skills: JSON.parse(card.skills) };
          } catch (error) {
            console.error('Failed to parse skills JSON:', error);
            processedCard = { ...card, skills: [] }; // 如果解析失败，设置为空数组
          }
        }

        return (
          <TooltipProvider key={card.id}>
            <Tooltip>
              <TooltipTrigger asChild>
                <Link href={`/cards/${card.id}`}>
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
                      {cardType === 'characters' ? (
                        <div className="flex items-center gap-2">
                          <ElementIcon className="w-4 h-4 text-primary" />
                          <span className="text-sm text-muted-foreground capitalize">{card.element || card.element_type}</span>
                        </div>
                      ) : (
                        <Badge variant="outline" className="text-xs">
                          {card.type}
                        </Badge>
                      )}
                    </CardContent>
                  </Card>
                </Link>
              </TooltipTrigger>
              <TooltipContent className="max-w-md w-auto bg-popover text-popover-foreground border p-4">
                <div className="space-y-2 max-h-[400px] overflow-y-auto">
                  <h4 className="font-bold text-lg">{card.title ? `${card.title} - ${card.name}` : card.name}</h4>
                  <div className="flex flex-wrap gap-2">
                    {cardType === 'characters' ? (
                      <>
                        <Badge variant="secondary" className="capitalize">
                          {card.element_type || card.element || "无元素"}
                        </Badge>
                        {card.country && (
                          <Badge variant="outline">
                            {card.country}
                          </Badge>
                        )}
                        {card.weapon_type && (
                          <Badge variant="outline">
                            {card.weapon_type}
                          </Badge>
                        )}
                      </>
                    ) : (
                      <>
                        <Badge variant="secondary" className="capitalize">
                          {card.type || "无类型"}
                        </Badge>
                        {card.element_type && (
                          <Badge variant="outline">
                            {card.element_type}
                          </Badge>
                        )}
                        {card.country && (
                          <Badge variant="outline">
                            {card.country}
                          </Badge>
                        )}
                      </>
                    )}
                    <div className="flex items-center gap-1">
                      {[...Array(card.rarity)].map((_, i) => (
                        <Sparkles key={i} className="w-3 h-3 fill-current" />
                      ))}
                    </div>
                  </div>
                  <div className="text-sm">
                    {cardType === 'characters' && (
                      <p><span className="font-semibold">生命值:</span> {card.health || "N/A"}</p>
                    )}
                    {card.description && <p><span className="font-semibold">描述:</span> {card.description}</p>}
                    <div className="pt-1">
                      <span className="font-semibold">费用: </span>
                      {card.cost && card.cost.length > 0 ? (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {card.cost.map((costItem, index) => (
                            <span key={index} className="inline-flex items-center gap-0.5 bg-secondary px-2 py-0.5 rounded-md text-xs">
                              {(() => {
                                const CostIcon = getElementTypeIcon(costItem.type);
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
                  {processedCard.skills && Array.isArray(processedCard.skills) && processedCard.skills.length > 0 && (
                    <div className="pt-2 border-t">
                      <h5 className="font-semibold mb-1">技能:</h5>
                      <ul className="space-y-1">
                        {processedCard.skills.map((skill, idx) => (
                          <li key={idx} className="text-sm">
                            <span className="font-medium">{skill.name}</span>
                            <div className="text-xs mt-1 ml-2">
                              {skill.cost && Array.isArray(skill.cost) && skill.cost.length > 0 && (
                                <div className="inline-flex flex-wrap gap-1 mr-2">
                                  {skill.cost.map((cost, costIdx) => {
                                    const CostIcon = getElementTypeIcon(cost.type);
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
        );
      })}
    </div>
  );
}