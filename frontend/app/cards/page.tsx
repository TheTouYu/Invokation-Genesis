"use client"

import { useState, useEffect } from "react";
import { GameHeader } from "@/components/layout/game-header";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CardType, CardFilters, CardFiltersResponse } from "@/lib/api/types";
import { getCards, getAllFilters } from "@/lib/api/cards";
import useSWR from "swr";
import { CardSearchFilter } from "@/components/card-filter/card-search-filter";
import { CardGrid } from "@/components/card-filter/card-grid";

export default function CardsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [elementFilter, setElementFilter] = useState("");
  const [countryFilter, setCountryFilter] = useState("");
  const [weaponTypeFilter, setWeaponTypeFilter] = useState("");
  const [cardTypeFilter, setCardTypeFilter] = useState("");
  const [rarityFilter, setRarityFilter] = useState<number | null>(null);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  // 状态用于跟踪当前活动的标签页
  const [activeTab, setActiveTab] = useState<"characters" | "actions">("characters");

  // 从后端获取的过滤选项
  const { data: allFilterOptions, error: filterError } = useSWR(
    "/api/filters",
    () => getAllFilters(),
    {
      onError: (error) => {
        if (error.message && error.message.startsWith('AUTH_ERROR:')) {
          // 重定向到登录页面已经在API客户端中处理
        }
      }
    }
  );

  // 可选标签 - 添加更多默认标签
  const availableTags = ["充能", "卡牌", "舍弃", "调和", "伤害", "反应"];

  // 切换标签
  const toggleTag = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag)
        ? prev.filter((t) => t !== tag)
        : [...prev, tag]
    );
  };

  // 使用防抖处理搜索查询
  const [debouncedSearchQuery, setDebouncedSearchQuery] = useState(searchQuery);

  useEffect(() => {
    // 只有当搜索查询不为空时才设置防抖延迟
    if (searchQuery) {
      const timer = setTimeout(() => {
        setDebouncedSearchQuery(searchQuery);
      }, 1000); // 1秒防抖延迟

      return () => clearTimeout(timer);
    } else {
      // 如果搜索查询为空，立即更新（清空搜索）
      setDebouncedSearchQuery(searchQuery);
    }
  }, [searchQuery]);

  // 点击标签，添加到已选标签列表（用于过滤，而不是搜索）
  const handleTagClick = (tag: string) => {
    if (!selectedTags.includes(tag)) {
      setSelectedTags((prev) => [...prev, tag]);
    }
  };

  // 构建过滤器对象 - 根据当前标签页调整type过滤
  let filters: CardFilters;
  if (cardTypeFilter) {
    // 如果选择了具体的卡牌类型，则使用该类型过滤
    filters = {
      type: cardTypeFilter,
      search: debouncedSearchQuery,
      element: elementFilter,
      country: countryFilter,
      weapon_type: weaponTypeFilter,
      rarity: rarityFilter || undefined,
      tag: selectedTags.length > 0 ? selectedTags : undefined,
    };
  } else if (activeTab === "characters") {
    // 如果在角色牌标签页且未选择具体类型，则只获取角色牌
    filters = {
      type: "角色牌",
      search: debouncedSearchQuery,
      element: elementFilter,
      country: countryFilter,
      weapon_type: weaponTypeFilter,
      rarity: rarityFilter || undefined,
      tag: selectedTags.length > 0 ? selectedTags : undefined,
    };
  } else {
    // 如果在行动牌标签页且未选择具体类型，则只获取行动牌
    filters = {
      type: "行动牌",
      search: debouncedSearchQuery,
      element: elementFilter,
      country: countryFilter,
      weapon_type: weaponTypeFilter,
      rarity: rarityFilter || undefined,
      tag: selectedTags.length > 0 ? selectedTags : undefined,
    };
  }

  // 使用SWR获取卡牌数据
  const { data: cardsData, error: cardsError, isLoading } = useSWR(
    JSON.stringify(filters), // 使用filters对象作为key
    () => getCards(filters),
    {
      onError: (error) => {
        if (error.message && error.message.startsWith('AUTH_ERROR:')) {
          // 重定向到登录页面已经在API客户端中处理
        }
      }
    }
  );

  // 按类型分类卡牌
  const allCards = cardsData?.cards || [];
  const characterCards = allCards.filter((card: CardType) => card.type === "角色牌");
  const actionCards = allCards.filter((card: CardType) => card.type !== "角色牌");

  // 显示加载状态
  if (isLoading) {
    return (
      <div className="min-h-screen flex flex-col">
        <GameHeader />
        <main className="flex-1 container py-8 flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary mb-4"></div>
            <p className="text-lg">正在加载卡牌数据...</p>
          </div>
        </main>
      </div>
    );
  }

  // 错误处理
  if (cardsError || filterError) {
    return (
      <div className="min-h-screen flex flex-col">
        <GameHeader />
        <main className="flex-1 container py-8 flex items-center justify-center">
          <div className="text-center">
            <p className="text-lg text-destructive">加载卡牌数据失败</p>
            <p className="text-sm text-muted-foreground">
              {cardsError?.message || filterError?.message}
            </p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col">
      <GameHeader />

      <main className="flex-1 container py-8">
        <div className="space-y-6">
          {/* Header */}
          <div className="space-y-2">
            <h1 className="text-4xl font-bold tracking-tight">卡牌图鉴</h1>
            <p className="text-muted-foreground text-lg">浏览和收集所有卡牌</p>
          </div>

          <CardSearchFilter
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            debouncedSearchQuery={debouncedSearchQuery}
            elementFilter={elementFilter}
            setElementFilter={setElementFilter}
            countryFilter={countryFilter}
            setCountryFilter={setCountryFilter}
            weaponTypeFilter={weaponTypeFilter}
            setWeaponTypeFilter={setWeaponTypeFilter}
            cardTypeFilter={cardTypeFilter}
            setCardTypeFilter={setCardTypeFilter}
            rarityFilter={rarityFilter}
            setRarityFilter={setRarityFilter}
            allFilterOptions={allFilterOptions}
            availableTags={availableTags}
            selectedTags={selectedTags}
            handleTagClick={handleTagClick}
            toggleTag={toggleTag}
          />

          {/* Tabs */}
          <Tabs 
            value={activeTab}
            onValueChange={(value) => setActiveTab(value as "characters" | "actions")}
            className="space-y-6"
          >
            <TabsList className="grid w-full max-w-md grid-cols-2">
              <TabsTrigger value="characters">角色牌</TabsTrigger>
              <TabsTrigger value="actions">行动牌</TabsTrigger>
            </TabsList>

            <TabsContent value="characters" className="space-y-4">
              <CardGrid cards={characterCards} cardType="characters" />
            </TabsContent>

            <TabsContent value="actions" className="space-y-4">
              <CardGrid cards={actionCards} cardType="actions" />
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
}