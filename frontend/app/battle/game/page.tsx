"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Heart, Zap, Hand, Clock, Settings } from "lucide-react"

export default function GamePage() {
  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Game Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur">
        <div className="container flex items-center justify-between h-14 px-4">
          <div className="flex items-center gap-4">
            <Clock className="w-4 h-4 text-muted-foreground" />
            <span className="font-mono font-bold text-lg">05:32</span>
          </div>
          <div className="flex items-center gap-2">
            <Badge variant="outline">回合 3</Badge>
            <Button variant="ghost" size="icon">
              <Settings className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </header>

      <main className="flex-1 container py-4 space-y-4">
        {/* Opponent Area */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-destructive/20 flex items-center justify-center">
                <span className="font-bold">对</span>
              </div>
              <div>
                <div className="font-medium">对手玩家</div>
                <div className="text-sm text-muted-foreground">钻石 II</div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Hand className="w-4 h-4 text-muted-foreground" />
                <span className="font-mono">5</span>
              </div>
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-primary" />
                <span className="font-mono">3</span>
              </div>
            </div>
          </div>

          {/* Opponent Characters */}
          <div className="grid grid-cols-3 gap-3">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="border-destructive/40">
                <CardContent className="p-3 space-y-2">
                  <div className="aspect-square bg-gradient-to-br from-destructive/20 to-background rounded-lg flex items-center justify-center">
                    <Zap className="w-12 h-12 text-destructive/40" />
                  </div>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Heart className="w-3 h-3 text-destructive" />
                      <Progress value={80} className="flex-1 h-2" />
                      <span className="text-xs font-mono">8/10</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Zap className="w-3 h-3 text-primary" />
                      <Progress value={60} className="flex-1 h-2" />
                      <span className="text-xs font-mono">2/3</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Battle Field */}
        <div className="py-8 flex items-center justify-center">
          <div className="text-center space-y-2">
            <Badge variant="secondary" className="text-lg px-4 py-2">
              对手回合
            </Badge>
            <p className="text-sm text-muted-foreground">等待对手行动...</p>
          </div>
        </div>

        {/* Player Characters */}
        <div className="space-y-3">
          <div className="grid grid-cols-3 gap-3">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="border-primary/40 cursor-pointer hover:border-primary transition-colors">
                <CardContent className="p-3 space-y-2">
                  <div className="aspect-square bg-gradient-to-br from-primary/20 to-background rounded-lg flex items-center justify-center">
                    <Zap className="w-12 h-12 text-primary/60" />
                  </div>
                  <div className="space-y-1">
                    <div className="text-sm font-medium text-center">雷电将军</div>
                    <div className="flex items-center gap-2">
                      <Heart className="w-3 h-3 text-chart-4" />
                      <Progress value={100} className="flex-1 h-2" />
                      <span className="text-xs font-mono">10/10</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Zap className="w-3 h-3 text-primary" />
                      <Progress value={100} className="flex-1 h-2" />
                      <span className="text-xs font-mono">3/3</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                <span className="font-bold">我</span>
              </div>
              <div>
                <div className="font-medium">我的昵称</div>
                <div className="text-sm text-muted-foreground">钻石 III</div>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-primary" />
                <span className="font-mono font-bold text-lg">5</span>
              </div>
            </div>
          </div>
        </div>

        {/* Hand Cards */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <Hand className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium">手牌</span>
          </div>
          <div className="flex gap-2 overflow-x-auto pb-2">
            {[1, 2, 3, 4, 5].map((i) => (
              <Card
                key={i}
                className="flex-shrink-0 w-32 cursor-pointer hover:border-primary transition-all hover:-translate-y-2"
              >
                <CardContent className="p-2">
                  <div className="aspect-[3/4] bg-gradient-to-br from-accent/20 to-background rounded flex items-center justify-center mb-2">
                    <Zap className="w-8 h-8 text-accent/60" />
                  </div>
                  <div className="text-xs font-medium text-center">元素爆发</div>
                  <div className="text-center mt-1">
                    <Badge variant="outline" className="text-xs">
                      3费
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-2">
          <Button variant="outline" className="flex-1 bg-transparent">
            切换角色
          </Button>
          <Button variant="outline" className="flex-1 bg-transparent">
            使用技能
          </Button>
          <Button className="flex-1">结束回合</Button>
        </div>
      </main>
    </div>
  )
}
