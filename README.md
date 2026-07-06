# RocoKingdom World - 数据自动更新

自动抓取洛克王国世界相关数据并生成 JSON 文件的脚本。

## 功能

- **果实数据抓取** - 从 wiki 抓取精灵果实图鉴数据
- **精灵数据抓取** - 从 wiki 抓取精灵图鉴数据（包含编号、名称、阶数、图片）
- **商人数据抓取** - 从 API 下载远行商人活动数据，生成 `live.json` 和 `raw.json`

## 输出文件

| 文件 | 说明 |
|------|------|
| `fruits.json` | 精灵果实数据 |
| `pokemon.json` | 精灵图鉴数据 |
| `live.json` | 商人活动原始数据 |
| `raw.json` | 商人活动处理后数据（含时间戳和当前物品） |

## raw.json 数据结构

```json
{
  "sourceUrl": "来源链接",
  "fetchedAt": "获取时间",
  "timezone": "Asia/Shanghai",
  "status": "open/closed",
  "round": 3,
  "startedAtBeijing": "开始时间",
  "nextRefreshBeijing": "下次刷新时间",
  "durationHours": 4,
  "items": [
    {
      "name": "物品名称",
      "price": "价格",
      "priceRaw": "价格(raw)",
      "limit": "限购数量",
      "image": "图片链接",
      "category": "分类",
      "description": "描述",
      "rounds": [1, 3],
      "start_time": 1783296000000,
      "end_time": 1783310100000,
      "start_time_str": "2026-07-06 08:00:00",
      "end_time_str": "2026-07-06 11:55:00"
    }
  ],
  "current_items": [...]
}
```

## 轮次时间

| 轮次 | 时间（北京时间） |
|------|------------------|
| 第1轮 | 08:00 - 11:55 |
| 第2轮 | 12:00 - 15:55 |
| 第3轮 | 16:00 - 19:55 |
| 第4轮 | 20:00 - 23:55 |

## 使用方法

### 安装依赖

```bash
pip install requests beautifulsoup4
```

### 运行脚本

```bash
python api.py
```

## GitHub Actions

项目配置了 GitHub Actions 自动更新工作流，每天北京时间 08:05、12:05、16:05、20:05 自动运行并提交更新。

工作流文件：`.github/workflows/update-data.yml`

## 目录结构

```
newapi/
├── api.py          # 主脚本
├── app.js          # Node.js 版本脚本
├── fruits.json     # 果实数据
├── pokemon.json    # 精灵数据
├── live.json       # 商人原始数据
├── raw.json        # 商人处理后数据
└── .github/
    └── workflows/
        └── update-data.yml  # 自动更新工作流
```

## 许可证

MIT
