import { GameHeader } from "@/components/layout/game-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Library, Layers, Swords, Trophy, TrendingUp } from "lucide-react"
import Link from "next/link"

export default function DashboardPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <GameHeader />

      <main className="flex-1 container py-8">
        <div className="space-y-8">
          {/* Welcome Section */}
          <div className="space-y-2">
            <h1 className="text-4xl font-bold tracking-tight">欢迎回来，旅行者</h1>
            <p className="text-muted-foreground text-lg">准备好开始新的对决了吗？</p>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="border-primary/20 hover:border-primary/40 transition-colors cursor-pointer group">
              <Link href="/battle">
                <CardHeader>
                  <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-2 group-hover:bg-primary/20 transition-colors">
                    <Swords className="w-6 h-6 text-primary" />
                  </div>
                  <CardTitle>开始对战</CardTitle>
                  <CardDescription>匹配对手，展开激烈对决</CardDescription>
                </CardHeader>
              </Link>
            </Card>

            <Card className="border-accent/20 hover:border-accent/40 transition-colors cursor-pointer group">
              <Link href="/decks/builder">
                <CardHeader>
                  <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center mb-2 group-hover:bg-accent/20 transition-colors">
                    <Layers className="w-6 h-6 text-accent" />
                  </div>
                  <CardTitle>构建卡组</CardTitle>
                  <CardDescription>创建你的专属战术组合</CardDescription>
                </CardHeader>
              </Link>
            </Card>

            <Card className="border-chart-2/20 hover:border-chart-2/40 transition-colors cursor-pointer group">
              <Link href="/cards">
                <CardHeader>
                  <div className="w-12 h-12 rounded-lg bg-chart-2/10 flex items-center justify-center mb-2 group-hover:bg-chart-2/20 transition-colors">
                    <Library className="w-6 h-6 text-chart-2" />
                  </div>
                  <CardTitle>卡牌图鉴</CardTitle>
                  <CardDescription>浏览所有可用卡牌</CardDescription>
                </CardHeader>
              </Link>
            </Card>
          </div>

          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardDescription>总胜场</CardDescription>
                <CardTitle className="text-3xl">127</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-sm text-chart-4">
                  <TrendingUp className="w-4 h-4" />
                  <span>+12% 本周</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>胜率</CardDescription>
                <CardTitle className="text-3xl">68%</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Trophy className="w-4 h-4" />
                  <span>排名 #342</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>拥有卡牌</CardDescription>
                <CardTitle className="text-3xl">89</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground">共 150 张</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>卡组数量</CardDescription>
                <CardTitle className="text-3xl">5</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground">最多 10 个</div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Decks */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">我的卡组</h2>
              <Button asChild variant="outline">
                <Link href="/decks">查看全部</Link>
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[
                { name: "雷电将军速攻", cards: 30, wins: 45, losses: 23 },
                { name: "冰系控制", cards: 30, wins: 38, losses: 19 },
                { name: "火系爆发", cards: 30, wins: 32, losses: 28 },
              ].map((deck, i) => (
                <Card key={i} className="hover:border-primary/40 transition-colors cursor-pointer">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>{deck.name}</span>
                      <Layers className="w-5 h-5 text-muted-foreground" />
                    </CardTitle>
                    <CardDescription>{deck.cards} 张卡牌</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">战绩</span>
                      <span className="font-medium">
                        {deck.wins}胜 {deck.losses}负
                      </span>
                    </div>
                    <div className="mt-2 h-2 bg-secondary rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary rounded-full"
                        style={{ width: `${(deck.wins / (deck.wins + deck.losses)) * 100}%` }}
                      />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Recent Matches */}
          <div className="space-y-4">
            <h2 className="text-2xl font-bold">最近对战</h2>

            <Card>
              <CardContent className="p-0">
                <div className="divide-y divide-border">
                  {[
                    { opponent: "玩家A", result: "胜利", deck: "雷电将军速攻", time: "2小时前" },
                    { opponent: "玩家B", result: "失败", deck: "冰系控制", time: "5小时前" },
                    { opponent: "玩家C", result: "胜利", deck: "雷电将军速攻", time: "1天前" },
                    { opponent: "玩家D", result: "胜利", deck: "火系爆发", time: "1天前" },
                  ].map((match, i) => (
                    <div key={i} className="flex items-center justify-between p-4 hover:bg-muted/50 transition-colors">
                      <div className="flex items-center gap-4">
                        <div
                          className={`w-2 h-2 rounded-full ${match.result === "胜利" ? "bg-chart-4" : "bg-destructive"}`}
                        />
                        <div>
                          <div className="font-medium">对战 {match.opponent}</div>
                          <div className="text-sm text-muted-foreground">{match.deck}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`font-medium ${match.result === "胜利" ? "text-chart-4" : "text-destructive"}`}>
                          {match.result}
                        </div>
                        <div className="text-sm text-muted-foreground">{match.time}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
