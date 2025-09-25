# 美甲預約系統 - 共用組件庫

這是美甲預約系統的共用組件庫，包含：

## 內容

- 🎨 **UI 組件** - 基於 shadcn/ui 的共用組件
- 🎨 **樣式檔案** - Tailwind CSS 全域樣式
- ⚙️ **配置檔案** - Tailwind 和 PostCSS 配置
- 🛠️ **工具函數** - 共用的工具函數

## 使用方式

各應用可以通過相對路徑引用共用組件：

```typescript
import { Button } from '../shared/components/ui/button';
import '../shared/styles/globals.css';
```

## 組件列表

- Button, Card, Input, Label
- Dialog, Select, Textarea
- Badge, Switch, Tabs
- Calendar, Chart, Table
- 以及更多...

## 維護

當需要更新共用組件時，請同時更新所有引用此組件庫的應用。
