"use client"

import { GameHeader } from "@/components/layout/game-header"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { User, Bell, Shield, Palette, Volume2, Save } from "lucide-react"

export default function SettingsPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <GameHeader />

      <main className="flex-1 container py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Header */}
          <div className="space-y-2">
            <h1 className="text-4xl font-bold tracking-tight">设置</h1>
            <p className="text-muted-foreground text-lg">管理你的账号和偏好设置</p>
          </div>

          <Tabs defaultValue="account" className="space-y-6">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="account" className="gap-2">
                <User className="w-4 h-4" />
                <span className="hidden sm:inline">账号</span>
              </TabsTrigger>
              <TabsTrigger value="notifications" className="gap-2">
                <Bell className="w-4 h-4" />
                <span className="hidden sm:inline">通知</span>
              </TabsTrigger>
              <TabsTrigger value="privacy" className="gap-2">
                <Shield className="w-4 h-4" />
                <span className="hidden sm:inline">隐私</span>
              </TabsTrigger>
              <TabsTrigger value="appearance" className="gap-2">
                <Palette className="w-4 h-4" />
                <span className="hidden sm:inline">外观</span>
              </TabsTrigger>
              <TabsTrigger value="audio" className="gap-2">
                <Volume2 className="w-4 h-4" />
                <span className="hidden sm:inline">音效</span>
              </TabsTrigger>
            </TabsList>

            <TabsContent value="account" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>个人信息</CardTitle>
                  <CardDescription>更新你的账号信息</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="username">用户名</Label>
                    <Input id="username" defaultValue="玩家昵称" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">邮箱</Label>
                    <Input id="email" type="email" defaultValue="player@example.com" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="bio">个人简介</Label>
                    <Input id="bio" defaultValue="热爱策略卡牌游戏的玩家" />
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>修改密码</CardTitle>
                  <CardDescription>确保你的账号安全</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="current-password">当前密码</Label>
                    <Input id="current-password" type="password" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="new-password">新密码</Label>
                    <Input id="new-password" type="password" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="confirm-password">确认新密码</Label>
                    <Input id="confirm-password" type="password" />
                  </div>
                </CardContent>
              </Card>

              <div className="flex justify-end">
                <Button size="lg" className="gap-2">
                  <Save className="w-4 h-4" />
                  保存更改
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="notifications" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>通知设置</CardTitle>
                  <CardDescription>选择你想接收的通知类型</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>对战邀请</Label>
                      <p className="text-sm text-muted-foreground">当有玩家邀请你对战时通知</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <Separator />
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>好友上线</Label>
                      <p className="text-sm text-muted-foreground">当好友上线时通知</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <Separator />
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>赛季更新</Label>
                      <p className="text-sm text-muted-foreground">新赛季开始时通知</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <Separator />
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>成就解锁</Label>
                      <p className="text-sm text-muted-foreground">解锁新成就时通知</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <Separator />
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>邮件通知</Label>
                      <p className="text-sm text-muted-foreground">通过邮件接收重要通知</p>
                    </div>
                    <Switch />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="privacy" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>隐私设置</CardTitle>
                  <CardDescription>控制谁可以看到你的信息</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <Label>个人资料可见性</Label>
                    <Select defaultValue="public">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="public">所有人</SelectItem>
                        <SelectItem value="friends">仅好友</SelectItem>
                        <SelectItem value="private">仅自己</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Separator />
                  <div className="space-y-2">
                    <Label>对战历史可见性</Label>
                    <Select defaultValue="public">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="public">所有人</SelectItem>
                        <SelectItem value="friends">仅好友</SelectItem>
                        <SelectItem value="private">仅自己</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Separator />
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>显示在线状态</Label>
                      <p className="text-sm text-muted-foreground">让其他玩家看到你是否在线</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <Separator />
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>允许好友邀请</Label>
                      <p className="text-sm text-muted-foreground">允许其他玩家添加你为好友</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="appearance" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>外观设置</CardTitle>
                  <CardDescription>自定义界面外观</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <Label>主题</Label>
                    <Select defaultValue="dark">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="light">浅色</SelectItem>
                        <SelectItem value="dark">深色</SelectItem>
                        <SelectItem value="system">跟随系统</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Separator />
                  <div className="space-y-2">
                    <Label>语言</Label>
                    <Select defaultValue="zh-CN">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="zh-CN">简体中文</SelectItem>
                        <SelectItem value="zh-TW">繁體中文</SelectItem>
                        <SelectItem value="en">English</SelectItem>
                        <SelectItem value="ja">日本語</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Separator />
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>动画效果</Label>
                      <p className="text-sm text-muted-foreground">启用界面动画效果</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  <Separator />
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>高对比度</Label>
                      <p className="text-sm text-muted-foreground">提高界面对比度以便阅读</p>
                    </div>
                    <Switch />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="audio" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>音效设置</CardTitle>
                  <CardDescription>调整游戏音效和音乐</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between mb-2">
                      <Label>主音量</Label>
                      <span className="text-sm text-muted-foreground">80%</span>
                    </div>
                    <input type="range" className="w-full" defaultValue="80" />
                  </div>
                  <Separator />
                  <div className="space-y-2">
                    <div className="flex items-center justify-between mb-2">
                      <Label>背景音乐</Label>
                      <span className="text-sm text-muted-foreground">60%</span>
                    </div>
                    <input type="range" className="w-full" defaultValue="60" />
                  </div>
                  <Separator />
                  <div className="space-y-2">
                    <div className="flex items-center justify-between mb-2">
                      <Label>音效</Label>
                      <span className="text-sm text-muted-foreground">70%</span>
                    </div>
                    <input type="range" className="w-full" defaultValue="70" />
                  </div>
                  <Separator />
                  <div className="space-y-2">
                    <div className="flex items-center justify-between mb-2">
                      <Label>语音</Label>
                      <span className="text-sm text-muted-foreground">50%</span>
                    </div>
                    <input type="range" className="w-full" defaultValue="50" />
                  </div>
                  <Separator />
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>静音</Label>
                      <p className="text-sm text-muted-foreground">关闭所有声音</p>
                    </div>
                    <Switch />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  )
}
