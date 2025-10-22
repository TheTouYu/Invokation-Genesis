import { RegisterForm } from "@/components/auth/register-form"
import Link from "next/link"
import { ArrowLeft } from "lucide-react"

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-accent/10 via-background to-background" />

      {/* Back button */}
      <Link
        href="/"
        className="absolute top-6 left-6 flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        返回首页
      </Link>

      <div className="relative z-10 w-full max-w-md space-y-8">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">创建账号</h1>
          <p className="text-muted-foreground">加入七圣召唤，开启你的对战之旅</p>
        </div>

        {/* Register Form */}
        <RegisterForm />

        {/* Login Link */}
        <div className="text-center text-sm">
          <span className="text-muted-foreground">已有账号？</span>{" "}
          <Link href="/login" className="text-primary hover:underline font-medium">
            立即登录
          </Link>
        </div>
      </div>
    </div>
  )
}
