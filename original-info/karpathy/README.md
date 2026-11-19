# follows/karpathy — Andrej Karpathy 软件开发与 AI 工程资料库

这是 `@karpathy`（Andrej Karpathy）的软件开发与 AI 工程资料目录，用来长期跟踪他的课程、博客、开源项目、技术演讲，以及他在 X 上提到的站外教程与代码。目录只做索引和摘要，不转载原文。

同级已有 `follows/poteto/`；以后可以继续增加 `follows/<handle>/`，追踪其他人。本目录不覆盖 poteto 的内容。

## 他是谁

| 项 | 内容 |
| :---- | :---- |
| X | [x.com/karpathy](https://x.com/karpathy)，数字 ID `33836629`，展示名 Andrej Karpathy |
| 账号创建 | 2009-04-21（来自公开资料，UTC） |
| 资料简介 | 首次读取时简介为空，地点 Earth，蓝标认证 |
| 个人主页 | [karpathy.ai](https://karpathy.ai/) |
| YouTube | [@AndrejKarpathy](https://www.youtube.com/@AndrejKarpathy)，频道 ID `UCXUPKJO5MZQN11PqgIvyuvQ`（以频道页 canonical/og 为准，不要用页面里插入的相关频道 ID） |
| GitHub | [github.com/karpathy](https://github.com/karpathy) |
| 现行博客 | [karpathy.bearblog.dev](https://karpathy.bearblog.dev/blog/) |
| 历史博客 | [karpathy.github.io](https://karpathy.github.io/)；[Medium](https://karpathy.medium.com/)（本轮 403，未读） |
| 课程 | [Neural Networks: Zero to Hero](https://karpathy.ai/zero-to-hero.html)；斯坦福 [CS231n](https://cs231n.stanford.edu/) |
| 组织 | [Eureka Labs](https://eurekalabs.ai/)（2024-07-16 宣布） |

首次读取时该账号约 10,173 条帖子、约 446 万关注者。这不是“已全部读完 10,173 条”的意思，见下方覆盖说明。

## 本目录里有什么

- [资料索引（表格）](https://docs.google.com/spreadsheets/d/1QX3F036L5xWhYL28bx1AfLWcSk8k3U4FwCypWReknI8/edit)：适合筛选、排序和以后追加行  
- [分类阅读版](https://docs.google.com/document/d/1inBAQrFhcgGuhnnDLFA79eXyO1RZRlEnlGNrKUC328M/edit)：按主题浏览  
- [tracking-state.json](https://drive.google.com/file/d/12gPFZiMc4pACNWltZAjps-v1Pn069GU7/view)：给每日增量任务用的账号 ID、已扫范围、去重键和续扫游标  
- [更新日志](https://docs.google.com/document/d/1JsRXXOb5QlpfyIf7YSTxD5N20Ft3scyvWTlIIC3rUPY/edit)

当前收录 **160** 条（首次整理），分类如下：

- 官方站点与身份：8 条  
- 课程与系统教程：16 条  
- YouTube 通识讲座：4 条  
- 外部平台演讲与访谈：22 条  
- Bear 博客：11 条  
- GitHub Pages 博客：21 条  
- 开源项目与代码：38 条  
- 论文与学术项目：6 条  
- 早期实验与演示：4 条  
- X 技术帖与线程：20 条  
- 推荐的第三方资料：10 条

身份字段区分：本人原创、本人原创（组织）、本人演讲（发布于他方频道）、课程团队/合授、合作论文、推荐他人作品、相关第三方。

## 覆盖了什么，没覆盖什么

已相对完整或本轮系统查过的部分：

- 官方主页、Zero to Hero 课程页、Bear 博客全部 14 篇中与软件/AI 相关的 11 篇（已打开 200）  
- GitHub Pages 博客本轮抓到的技术/工程文章（已打开 200）；Software 2.0 在 Medium，403 未读  
- 公开 GitHub 仓库：未认证 API 列出 63 个公开库、54 个非 fork；目录收录其中与教学/LLM/工具相关的代表作，以及 gist、HackerTube / TristanTube / HN Time Capsule 站点  
- 自己频道：官方 RSS 最近 15 条 \+ Uploads 播放列表 17 个视频 ID；Zero to Hero 九讲（含 “Let’s reproduce GPT-2 (124M)”，ID `l8pRSuU81PU`）和三场通识讲座已用 oembed/RSS 核验标题  
- 官方主页列出的他方频道演讲/访谈：已用 oembed 核验标题，未观看  
- CS231n 官方站点、笔记、2016 大纲与 2016 讲座播放列表（https 200）  
- Eureka Labs 官页与 LLM101n（README 声明课程尚不存在、仓库已归档）  
- 公开 X：按时间窗和项目/链接关键词检索并翻页，作者过滤为 `33836629`，本轮约 26 次公开读取，去重后看到约 514 条候选帖，再从中策展技术条目

X 历史是**按时间窗检索加翻页，不是 10,173 条时间线穷尽**。归档搜索都带了 `start_time`/`end_time`。只收录 `author_id=33836629` 的帖，线程已去重聚合。

本轮已扫到内容的时间范围（不完全连续）：2015–2016、2017–2021 部分、2022 年末、2023–2026 较多；2024 年初、2022 上半年、2016 部分、2014 及更早仍明显不足。未翻完的游标见 `tracking-state.json` 的 `backfill_cursors`。

明确缺口与限制：

- 多个检索窗仍有 `next_token`，应由后续增量任务继续翻页，不要无限循环，也不要宣称已经穷尽历史  
- 未宣称收录已删帖、平台未返回或不可访问的内容  
- Medium（含 Software 2.0 正文）403 未读，不编造摘要  
- Google Scholar 主页本轮 403 未读  
- `www.arxiv-sanity.com` 与 `arxiv-sanity-lite.com` 本轮无法访问，只保留对应 GitHub 仓库  
- EurekaLabsAI 组织页 200，但未认证 API 返回的公开仓库列表为空，未编造组织仓库清单  
- 部分 X 短链（t.co）未展开，推荐条目若没有可靠最终 URL 就留空，避免猜地址  
- 视频只记录已核验标题/说明/链接，未观看，不编造讲解细节  
- `karpathy.ai` 下 year-in-review / llm-os 等路径本轮返回与主页相同的 HTML，不是独立文章  
- 未收入：sci-fi 书单 `books.html`，以及 Bear 上偏生活向的 Chemical hygiene、睡眠追踪、I love calculator、GitHub 博客的 Biohacking Lite；早期游戏预告片也未收  
- 论文项目页有几条仅来自官方主页索引，本轮未逐页 HEAD，已在核验状态里标明  
- 只读公开项目，未 checkout、未修改代码

## 以后每天怎么更新

1. 用公开 X 接口读取 `@karpathy`（ID `33836629`）在 `since_id` 之后的新帖，不要登录个人 X、不要改关注或点赞。  
2. 同时检查 Bear 博客、karpathy.ai、Zero to Hero 课程页、YouTube 频道 RSS（正确频道 ID）、GitHub 用户公开仓库是否有新文章/视频/项目。  
3. 筛软件开发与 AI 工程内容：课程、博文、仓库、演讲、有实质内容的技术回复和长线程；推荐他人作品单独标注。闲聊、纯科幻书单、非技术生活向内容不收。  
4. 抽出站外链接，用 WebFetch 或 curl 打开：200 记已核验，404 标注失效并不再当作活跃入口，403/超时记未读。不要为了 403 去绕过访问控制。无法阅读的原文不要编摘要。  
5. 按 `dedupe_keys`（帖子 ID、conversation\_id、规范化 URL、目录条目 ID）去重后追加到《资料索引》，并在《更新日志》写一行。  
6. 若仍有历史游标，在当日额度内继续补扫，不要无限循环（公开读取限制约为每分钟 30 次、每天 1000 次、每次最多 25 条）。  
7. 更新 `tracking-state.json` 里的 `newest_post_id`、已扫范围和游标。翻完的窗口从 `backfill_cursors` 删除。

日期：有来源才填写。X 的 `created_at` 是 UTC，写入日志或需要时分时应换算到 Asia/Singapore（UTC+8）。
