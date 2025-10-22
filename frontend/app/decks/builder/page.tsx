"use client"

import { GameHeader } from "@/components/layout/game-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { ArrowLeft, Save, Sparkles, Zap, Droplet, Flame, Plus, Minus, Trash2 } from "lucide-react"
import Link from "next/link"
import { useState } from "react"

const availableCharacters = [
  { id: 1, name: "雷电将军", element: "electro", cost: 3, icon: Zap },
  { id: 2, name: "神里绫华", element: "cryo", cost: 3, icon: Droplet },
  { id: 3, name: "胡桃", element: "pyro", cost: 3, icon: Flame },
]

const availableActions = [
  { id: 101, name: "元素爆发", cost: 3, category: "技能" },
  { id: 102, name: "快速切换", cost: 1, category: "战术" },
  { id: 103, name: "护盾强化", cost: 2, category: "防御" },
  { id: 104, name: "元素共鸣", cost: 2, category: "增益" },
]

export default function DeckBuilderPage() {
  const [deckName, setDeckName] = useState("")
  const [selectedCharacters, setSelectedCharacters] = useState<number[]>([])
  const [selectedActions, setSelectedActions] = useState<{ id: number; count: number }[]>([])

  const addCharacter = (id: number) => {
    if (selectedCharacters.length < 3 && !selectedCharacters.includes(id)) {
      setSelectedCharacters([...selectedCharacters, id])
    }
  }

  const removeCharacter = (id: number) => {
    setSelectedCharacters(selectedCharacters.filter((cid) => cid !== id))
  }

  const addAction = (id: number) => {
    const existing = selectedActions.find((a) => a.id === id)
    const totalActions = selectedActions.reduce((sum, a) => sum + a.count, 0)

    if (totalActions < 30) {
      if (existing && existing.count < 2) {
        setSelectedActions(selectedActions.map((a) => (a.id === id ? { ...a, count: a.count + 1 } : a)))
      } else if (!existing) {
        setSelectedActions([...selectedActions, { id, count: 1 }])
      }
    }
  }

  const removeAction = (id: number) => {
    const existing = selectedActions.find((a) => a.id === id)
    if (existing) {
      if (existing.count > 1) {
        setSelectedActions(selectedActions.map((a) => (a.id === id ? { ...a, count: a.count - 1 } : a)))
      } else {
        setSelectedActions(selectedActions.filter((a) => a.id !== id))
      }
    }
  }

  const totalCards = selectedCharacters.length + selectedActions.reduce((sum, a) => sum + a.count, 0)

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
            <Button size="lg" className="gap-2">
              <Save className="w-4 h-4" />
              保存卡组
            </Button>
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
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {availableCharacters.map((char) => {
                      const Icon = char.icon
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
                              <div className="w-16 h-16 rounded-lg bg-gradient-to-br from-primary/20 to-accent/10 flex items-center justify-center">
                                <Icon className="w-8 h-8 text-primary" />
                              </div>
                              <div className="flex-1">
                                <h3 className="font-bold mb-1">{char.name}</h3>
                                <div className="flex items-center gap-2">
                                  <Badge variant="outline" className="text-xs">
                                    费用 {char.cost}
                                  </Badge>
                                  <Badge variant="secondary" className="text-xs capitalize">
                                    {char.element}
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
                </TabsContent>

                <TabsContent value="actions" className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {availableActions.map((action) => {
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
                            <div className="flex items-center justify-between mb-3">
                              <div>
                                <h3 className="font-bold mb-1">{action.name}</h3>
                                <div className="flex items-center gap-2">
                                  <Badge variant="outline" className="text-xs">
                                    费用 {action.cost}
                                  </Badge>
                                  <Badge variant="secondary" className="text-xs">
                                    {action.category}
                                  </Badge>
                                </div>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
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
                          const char = availableCharacters.find((c) => c.id === id)
                          if (!char) return null
                          const Icon = char.icon
                          return (
                            <div key={id} className="flex items-center justify-between p-2 rounded-lg bg-muted">
                              <div className="flex items-center gap-2">
                                <Icon className="w-4 h-4 text-primary" />
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
                          const action = availableActions.find((a) => a.id === id)
                          if (!action) return null
                          return (
                            <div key={id} className="flex items-center justify-between p-2 rounded-lg bg-muted">
                              <span className="text-sm font-medium">{action.name}</span>
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
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
