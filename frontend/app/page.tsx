import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Sparkles, Swords, Users } from "lucide-react"

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Hero Section */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-12 relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/20 via-background to-background" />

        <div className="relative z-10 max-w-4xl mx-auto text-center space-y-8">
          {/* Logo/Title */}
          <div className="space-y-4">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20">
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-sm font-medium text-primary">策略卡牌对战</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-balance">七圣召唤</h1>

            <p className="text-xl md:text-2xl text-muted-foreground text-balance max-w-2xl mx-auto">
              构建你的专属卡组，召唤强大角色，在策略对决中证明你的实力
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button asChild size="lg" className="w-full sm:w-auto text-lg px-8">
              <Link href="/login">开始游戏</Link>
            </Button>
            <Button asChild size="lg" variant="outline" className="w-full sm:w-auto text-lg px-8 bg-transparent">
              <Link href="/register">创建账号</Link>
            </Button>
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-12">
            <div className="flex flex-col items-center gap-3 p-6 rounded-lg bg-card border border-border">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-primary" />
              </div>
              <h3 className="font-semibold text-lg">丰富卡牌</h3>
              <p className="text-sm text-muted-foreground text-center">收集角色牌和行动牌，打造独特战术</p>
            </div>

            <div className="flex flex-col items-center gap-3 p-6 rounded-lg bg-card border border-border">
              <div className="w-12 h-12 rounded-full bg-accent/10 flex items-center justify-center">
                <Swords className="w-6 h-6 text-accent" />
              </div>
              <h3 className="font-semibold text-lg">策略对决</h3>
              <p className="text-sm text-muted-foreground text-center">实时联机对战，展现你的战术智慧</p>
            </div>

            <div className="flex flex-col items-center gap-3 p-6 rounded-lg bg-card border border-border">
              <div className="w-12 h-12 rounded-full bg-chart-2/10 flex items-center justify-center">
                <Users className="w-6 h-6 text-chart-2" />
              </div>
              <h3 className="font-semibold text-lg">卡组构建</h3>
              <p className="text-sm text-muted-foreground text-center">自由组合卡牌，创造专属卡组</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-6 px-4 border-t border-border">
        <div className="max-w-7xl mx-auto text-center text-sm text-muted-foreground">
          <p>© 2025 七圣召唤. 所有权利保留.</p>
        </div>
      </footer>
    </div>
  )
}
