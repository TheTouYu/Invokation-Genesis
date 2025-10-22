"use client"

import { GameHeader } from "@/components/layout/game-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Trophy, Target, Swords, TrendingUp, Calendar, Mail, Edit, Loader2 } from "lucide-react"
import { useAuth } from "@/hooks/use-auth"
import useSWR from "swr"
import { getProfile } from "@/lib/api/auth"

export default function ProfilePage() {
  const { user, loading, logout } = useAuth();
  
  // 如果用户未登录，显示加载状态
  if (loading) {
    return (
      <div className="min-h-screen flex flex-col">
        <GameHeader />
        <main className="flex-1 container py-8 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="h-12 w-12 animate-spin text-primary" />
            <p className="text-lg">加载中...</p>
          </div>
        </main>
      </div>
    );
  }

  // 如果用户未登录，显示未登录状态
  if (!user) {
    return (
      <div className="min-h-screen flex flex-col">
        <GameHeader />
        <main className="flex-1 container py-8 flex items-center justify-center">
          <div className="text-center space-y-4">
            <h2 className="text-2xl font-bold">尚未登录</h2>
            <p className="text-muted-foreground">请先登录以查看个人资料</p>
            <div className="flex gap-2 justify-center">
              <Button asChild>
                <a href="/login">登录</a>
              </Button>
              <Button asChild variant="outline">
                <a href="/register">注册</a>
              </Button>
            </div>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <GameHeader />

      <main className="flex-1 container py-8">
        <div className="max-w-5xl mx-auto space-y-8">
          {/* Profile Header */}
          <Card>
            <CardContent className="p-8">
              <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
                <Avatar className="w-24 h-24">
                  <AvatarImage src="/placeholder.svg?height=96&width=96" />
                  <AvatarFallback className="text-2xl">{user?.username?.charAt(0).toUpperCase()}</AvatarFallback>
                </Avatar>
                <div className="flex-1 space-y-3">
                  <div className="flex items-center gap-3">
                    <h1 className="text-3xl font-bold">{user?.username}</h1>
                    <Badge variant="secondary" className="gap-1">
                      <Trophy className="w-3 h-3" />
                      钻石 III
                    </Badge>
                  </div>
                  <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <Mail className="w-4 h-4" />
                      {user?.email || "邮箱未设置"}
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      加入于 2024年1月
                    </div>
                  </div>
                  <p className="text-muted-foreground">热爱策略卡牌游戏的玩家，欢迎来到七圣召唤。</p>
                </div>
                <Button className="gap-2" variant="outline" onClick={logout}>
                  <Edit className="w-4 h-4" />
                  登出
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Stats Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardDescription>总胜场</CardDescription>
                <CardTitle className="text-3xl">--</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2 text-sm text-chart-4">
                  <TrendingUp className="w-4 h-4" />
                  <span>-- 本周</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>总场次</CardDescription>
                <CardTitle className="text-3xl">--</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">--胜 --负</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>胜率</CardDescription>
                <CardTitle className="text-3xl">--%</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-2 bg-secondary rounded-full overflow-hidden">
                  <div className="h-3 h-3 bg-primary rounded-full" style={{ width: "0%" }} />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardDescription>排名</CardDescription>
                <CardTitle className="text-3xl">--</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">全服排名</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Achievements */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Trophy className="w-5 h-5 text-primary" />
                  成就
                </CardTitle>
                <CardDescription>已解锁 --/-- 个成就</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  { name: "初出茅庐", desc: "赢得第一场对战", unlocked: false },
                  { name: "连胜大师", desc: "达成10连胜", unlocked: false },
                  { name: "卡组收藏家", desc: "创建5个不同卡组", unlocked: false },
                  { name: "百战老将", desc: "完成100场对战", unlocked: false },
                ].map((achievement, i) => (
                  <div
                    key={i}
                    className={`flex items-center gap-3 p-3 rounded-lg ${achievement.unlocked ? "bg-primary/10" : "bg-muted opacity-50"}`}
                  >
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center ${achievement.unlocked ? "bg-primary/20" : "bg-muted-foreground/20"}`}
                    >
                      <Trophy
                        className={`w-5 h-5 ${achievement.unlocked ? "text-primary" : "text-muted-foreground"}`}
                      />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium">{achievement.name}</div>
                      <div className="text-sm text-muted-foreground">{achievement.desc}</div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Favorite Cards */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Target className="w-5 h-5 text-accent" />
                  常用卡牌
                </CardTitle>
                <CardDescription>使用次数最多的卡牌</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  { name: "雷电将军", uses: 0, winRate: 0 },
                  { name: "元素爆发", uses: 0, winRate: 0 },
                  { name: "快速切换", uses: 0, winRate: 0 },
                  { name: "神里绫华", uses: 0, winRate: 0 },
                ].map((card, i) => (
                  <div key={i} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{card.name}</span>
                      <div className="flex items-center gap-3 text-sm">
                        <span className="text-muted-foreground">{card.uses} 次</span>
                        <Badge variant="outline">{card.winRate}% 胜率</Badge>
                      </div>
                    </div>
                    <div className="h-2 bg-secondary rounded-full overflow-hidden">
                      <div className="h-full bg-accent rounded-full" style={{ width: `${card.winRate}%` }} />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Match History */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Swords className="w-5 h-5 text-chart-2" />
                对战历史
              </CardTitle>
              <CardDescription>最近的对战记录</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {[
                  { opponent: "系统AI", result: "未开始", deck: "未对战", date: "从未", duration: "--" },
                ].map((match, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div
                        className={`w-2 h-2 rounded-full ${match.result === "胜利" ? "bg-chart-4" : match.result === "失败" ? "bg-destructive" : "bg-secondary"}`}
                      />
                      <div>
                        <div className="font-medium">对战 {match.opponent}</div>
                        <div className="text-sm text-muted-foreground">{match.deck}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`font-medium ${match.result === "胜利" ? "text-chart-4" : match.result === "失败" ? "text-destructive" : "text-secondary-foreground"}`}>
                        {match.result}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {match.date} · {match.duration}
                      </div>
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
