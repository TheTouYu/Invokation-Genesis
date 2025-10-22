"use client"

import { GameHeader } from "@/components/layout/game-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Swords, Users, Trophy, Clock, Play, RefreshCw } from "lucide-react"
import { useState } from "react"

const onlineRooms = [
  { id: 1, host: "玩家A", rank: "钻石", players: "1/2", mode: "排位赛" },
  { id: 2, host: "玩家B", rank: "铂金", players: "1/2", mode: "休闲赛" },
  { id: 3, host: "玩家C", rank: "黄金", players: "1/2", mode: "排位赛" },
  { id: 4, host: "玩家D", rank: "白银", players: "1/2", mode: "休闲赛" },
]

export default function BattlePage() {
  const [isMatching, setIsMatching] = useState(false)

  return (
    <div className="min-h-screen flex flex-col">
      <GameHeader />

      <main className="flex-1 container py-8">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Header */}
          <div className="space-y-2">
            <h1 className="text-4xl font-bold tracking-tight">对战大厅</h1>
            <p className="text-muted-foreground text-lg">选择对战模式，开始你的征程</p>
          </div>

          {/* Quick Match */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="border-primary/40 hover:border-primary transition-colors">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-2">
                  <Swords className="w-6 h-6 text-primary" />
                </div>
                <CardTitle className="text-2xl">快速匹配</CardTitle>
                <CardDescription>自动匹配实力相近的对手</CardDescription>
              </CardHeader>
              <CardContent>
                <Button
                  size="lg"
                  className="w-full gap-2"
                  onClick={() => setIsMatching(!isMatching)}
                  disabled={isMatching}
                >
                  {isMatching ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      匹配中...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4" />
                      开始匹配
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            <Card className="border-accent/40 hover:border-accent transition-colors">
              <CardHeader>
                <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center mb-2">
                  <Trophy className="w-6 h-6 text-accent" />
                </div>
                <CardTitle className="text-2xl">排位赛</CardTitle>
                <CardDescription>竞技模式，提升你的段位</CardDescription>
              </CardHeader>
              <CardContent>
                <Button size="lg" variant="outline" className="w-full gap-2 bg-transparent">
                  <Play className="w-4 h-4" />
                  进入排位
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardDescription>当前段位</CardDescription>
                <CardTitle className="text-2xl">钻石 III</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <Trophy className="w-4 h-4 text-primary" />
                  <span className="text-sm text-muted-foreground">1850 分</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>本赛季胜率</CardDescription>
                <CardTitle className="text-2xl">68%</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-2 bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-primary rounded-full" style={{ width: "68%" }} />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>在线玩家</CardDescription>
                <CardTitle className="text-2xl">1,234</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4 text-chart-2" />
                  <span className="text-sm text-muted-foreground">正在对战</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>平均对战时长</CardDescription>
                <CardTitle className="text-2xl">12分</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">每场</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Online Rooms */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">在线房间</h2>
              <Button variant="outline" size="sm" className="gap-2 bg-transparent">
                <RefreshCw className="w-4 h-4" />
                刷新
              </Button>
            </div>

            <Card>
              <CardContent className="p-0">
                <div className="divide-y divide-border">
                  {onlineRooms.map((room) => (
                    <div
                      key={room.id}
                      className="flex items-center justify-between p-4 hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                          <Users className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                          <div className="font-medium">{room.host} 的房间</div>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant="outline" className="text-xs">
                              {room.rank}
                            </Badge>
                            <Badge variant="secondary" className="text-xs">
                              {room.mode}
                            </Badge>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <div className="text-sm text-muted-foreground">玩家</div>
                          <div className="font-medium">{room.players}</div>
                        </div>
                        <Button size="sm">加入</Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Create Room */}
          <Card className="border-dashed">
            <CardContent className="p-8 text-center">
              <h3 className="font-bold text-xl mb-2">创建自定义房间</h3>
              <p className="text-muted-foreground mb-4">邀请好友进行私人对战</p>
              <Button size="lg" variant="outline">
                创建房间
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
