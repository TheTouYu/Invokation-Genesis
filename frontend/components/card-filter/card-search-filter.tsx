import { Search, Filter } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { CardFiltersResponse } from "@/lib/api/types";

interface CardSearchFilterProps {
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  debouncedSearchQuery: string;
  elementFilter: string;
  setElementFilter: (value: string) => void;
  countryFilter: string;
  setCountryFilter: (value: string) => void;
  weaponTypeFilter: string;
  setWeaponTypeFilter: (value: string) => void;
  cardTypeFilter: string;
  setCardTypeFilter: (value: string) => void;
  rarityFilter: number | null;
  setRarityFilter: (value: number | null) => void;
  allFilterOptions: CardFiltersResponse | undefined;
  availableTags: string[];
  selectedTags: string[];
  handleTagClick: (tag: string) => void;
  toggleTag: (tag: string) => void;
}

export function CardSearchFilter({
  searchQuery,
  setSearchQuery,
  debouncedSearchQuery,
  elementFilter,
  setElementFilter,
  countryFilter,
  setCountryFilter,
  weaponTypeFilter,
  setWeaponTypeFilter,
  cardTypeFilter,
  setCardTypeFilter,
  rarityFilter,
  setRarityFilter,
  allFilterOptions,
  availableTags,
  selectedTags,
  handleTagClick,
  toggleTag,
}: CardSearchFilterProps) {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="搜索卡牌名称..."
            className="pl-10"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery !== debouncedSearchQuery && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2">
              <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
            </div>
          )}
        </div>
        <Button variant="outline" className="gap-2 bg-transparent">
          <Filter className="w-4 h-4" />
          筛选
        </Button>
      </div>
      
      {/* Filter Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label className="text-sm font-medium text-muted-foreground mb-1 block">元素</label>
          <select 
            className="w-full p-2 border rounded-md bg-background"
            value={elementFilter}
            onChange={(e) => setElementFilter(e.target.value)}
          >
            <option value="">全部</option>
            {allFilterOptions?.elements?.map((element) => (
              <option key={element} value={element}>{element}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="text-sm font-medium text-muted-foreground mb-1 block">国家</label>
          <select 
            className="w-full p-2 border rounded-md bg-background"
            value={countryFilter}
            onChange={(e) => setCountryFilter(e.target.value)}
          >
            <option value="">全部</option>
            {allFilterOptions?.countries?.map((country) => (
              <option key={country} value={country}>{country}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="text-sm font-medium text-muted-foreground mb-1 block">武器类型</label>
          <select 
            className="w-full p-2 border rounded-md bg-background"
            value={weaponTypeFilter}
            onChange={(e) => setWeaponTypeFilter(e.target.value)}
          >
            <option value="">全部</option>
            {allFilterOptions?.weapon_types?.map((weaponType) => (
              <option key={weaponType} value={weaponType}>{weaponType}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label className="text-sm font-medium text-muted-foreground mb-1 block">卡牌类型</label>
          <select 
            className="w-full p-2 border rounded-md bg-background"
            value={cardTypeFilter}
            onChange={(e) => setCardTypeFilter(e.target.value)}
          >
            <option value="">全部</option>
            {allFilterOptions?.card_types?.map((cardType) => (
              <option key={cardType} value={cardType}>{cardType}</option>
            ))}
            <option value="行动牌">行动牌</option>
          </select>
        </div>
        
        <div>
          <label className="text-sm font-medium text-muted-foreground mb-1 block">稀有度</label>
          <select 
            className="w-full p-2 border rounded-md bg-background"
            value={rarityFilter || ""}
            onChange={(e) => setRarityFilter(e.target.value ? parseInt(e.target.value) : null)}
          >
            <option value="">全部</option>
            <option value="1">1星</option>
            <option value="2">2星</option>
            <option value="3">3星</option>
            <option value="4">4星</option>
            <option value="5">5星</option>
          </select>
        </div>
      </div>
      
      {/* Tag Selection - 添加可点击的默认标签行 */}
      <div>
        <label className="text-sm font-medium text-muted-foreground mb-2 block">可用标签</label>
        <div className="flex flex-wrap gap-2 mb-3">
          {allFilterOptions?.tags?.map((tag) => (
            <span 
              key={`available-${tag}`}
              className="inline-flex items-center rounded-full border bg-transparent px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-accent cursor-pointer"
              onClick={() => handleTagClick(tag)}
            >
              {tag}
            </span>
          ))}
        </div>
        
        <label className="text-sm font-medium text-muted-foreground mb-2 block">默认标签</label>
        <div className="flex flex-wrap gap-2 mb-3">
          {availableTags.map((tag) => (
            <span 
              key={`default-${tag}`}
              className="inline-flex items-center rounded-full border bg-transparent px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-secondary text-secondary-foreground hover:bg-accent cursor-pointer"
              onClick={() => handleTagClick(tag)}
            >
              {tag}
            </span>
          ))}
        </div>
        
        <label className="text-sm font-medium text-muted-foreground mb-2 block">已选标签</label>
        <div className="flex flex-wrap gap-2">
          {selectedTags.map((tag) => (
            <span 
              key={tag}
              className="inline-flex items-center rounded-full border bg-transparent px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent bg-primary text-primary-foreground cursor-pointer"
              onClick={() => toggleTag(tag)}
            >
              {tag}
              <button
                type="button"
                className="ml-1 rounded-full hover:text-primary-foreground"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleTag(tag);
                }}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-3 w-3"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </span>
          ))}
          {selectedTags.length === 0 && (
            <p className="text-sm text-muted-foreground">暂无已选标签</p>
          )}
        </div>
      </div>
    </div>
  );
}