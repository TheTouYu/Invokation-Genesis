import { GameHeader } from "@/components/layout/game-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Edit, Copy, Trash2, Play, Zap, Sparkles } from "lucide-react"
import Link from "next/link"

export default function DeckDetailPage() {
  const deck = {
    name: "雷电将军速攻",
    cards: 30,
    wins: 45,
    losses: 23,
    characters: [
      { name: "雷电将军", element: "electro", cost: 3 },
      { name: "九条裟罗", element: "electro", cost: 3 },
      { name: "班尼特", element: "pyro", cost: 3 },
    ],
    actions: [
      { name: "元素爆发", count: 2, cost: 3 },
      { name: "快速切换", count: 2, cost: 1 },
      { name: "护盾强化", count: 2, cost: 2 },
      { name: "元素共鸣", count: 2, cost: 2 },
      { name: "能量充能", count: 2, cost: 1 },
    ],
    recentMatches: [
      { opponent: "玩家A", result: "胜利", date: "2小时前" },
      { opponent: "玩家B", result: "胜利", date: "3小时前" },
      { opponent: "玩家C", result: "失败", date: "5小时前" },
    ],
  }

  const winRate = Math.round((deck.wins / (deck.wins + deck.losses)) * 100)

  return (
    <div className="min-h-screen flex flex-col">
      <GameHeader />

      <main className="flex-1 container py-8">
        <div className="max-w-5xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <Button asChild variant="ghost" className="gap-2">
              <Link href="/decks">
                <ArrowLeft className="w-4 h-4" />
                返回卡组列表
              </Link>
            </Button>
            <div className="flex gap-2">
              <Button variant="outline" size="icon">
                <Edit className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="icon">
                <Copy className="w-4 h-4" />
              </Button>
              <Button variant="outline" size="icon" className="text-destructive hover:text-destructive bg-transparent">
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Deck Info */}
          <div className="space-y-2">
            <h1 className="text-4xl font-bold">{deck.name}</h1>
            <p className="text-muted-foreground text-lg">{deck.cards} 张卡牌</p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardDescription>总场次</CardDescription>
                <CardTitle className="text-3xl">{deck.wins + deck.losses}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">
                  {deck.wins}胜 {deck.losses}负
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>胜率</CardDescription>
                <CardTitle className="text-3xl">{winRate}%</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-2 bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-primary rounded-full" style={{ width: `${winRate}%` }} />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>连胜</CardDescription>
                <CardTitle className="text-3xl">5</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">最高连胜记录</p>
              </CardContent>
            </Card>
          </div>

          <Button size="lg" className="w-full gap-2">
            <Play className="w-4 h-4" />
            使用此卡组开始对战
          </Button>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Characters */}
            <Card>
              <CardHeader>
                <CardTitle>角色配置</CardTitle>
                <CardDescription>3 个角色</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {deck.characters.map((char, i) => (
                  <div key={i} className="flex items-center gap-4 p-3 rounded-lg bg-muted">
                    <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary/20 to-accent/10 flex items-center justify-center">
                      <Zap className="w-6 h-6 text-primary" />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium">{char.name}</div>
                      <div className="text-sm text-muted-foreground capitalize">{char.element}</div>
                    </div>
                    <Badge variant="outline">费用 {char.cost}</Badge>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Actions */}
            <Card>
              <CardHeader>
                <CardTitle>行动牌</CardTitle>
                <CardDescription>{deck.actions.reduce((sum, a) => sum + a.count, 0)} 张</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                {deck.actions.map((action, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-muted">
                    <div className="flex items-center gap-3">
                      <Sparkles className="w-4 h-4 text-accent" />
                      <span className="font-medium">{action.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-xs">
                        费用 {action.cost}
                      </Badge>
                      <Badge variant="secondary">×{action.count}</Badge>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Recent Matches */}
          <Card>
            <CardHeader>
              <CardTitle>最近对战</CardTitle>
              <CardDescription>使用此卡组的最近战绩</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {deck.recentMatches.map((match, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-muted">
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-2 h-2 rounded-full ${match.result === "胜利" ? "bg-chart-4" : "bg-destructive"}`}
                      />
                      <span className="font-medium">对战 {match.opponent}</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className={`font-medium ${match.result === "胜利" ? "text-chart-4" : "text-destructive"}`}>
                        {match.result}
                      </span>
                      <span className="text-sm text-muted-foreground">{match.date}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
