# follows/mattpocockuk — Matt Pocock 软件开发与 AI 工程资料库

这是 `@mattpocockuk`（Matt Pocock）的软件开发、TypeScript 与 AI 工程资料目录，用来长期跟踪他的课程、博客、开源项目、技术演讲，以及他在 X 上提到的站外教程与代码。目录只做索引和摘要，不转载原文，不购买或展开付费课时。

同级已有 `follows/poteto/` 与 `follows/karpathy/`；本目录不覆盖前两人的内容。暂时只跟踪这三位，不再扩展其他人。

## 他是谁

| 项 | 内容 |
| :---- | :---- |
| X | [x.com/mattpocockuk](https://x.com/mattpocockuk)，数字 ID `346640777`，展示名 Matt Pocock |
| 账号创建 | 2011-08-01（来自公开资料，UTC） |
| 资料简介 | I teach devs for a living. Author of Total TypeScript and AI Hero. Ex-@vercel. Used to be a voice coach. |
| 资料链接 | [aihero.dev](https://aihero.dev)（www\.aihero.dev 可打开；apex 域本轮曾 403） |
| 个人主页 | [mattpocock.com](https://www.mattpocock.com/)（本轮访问不稳定，成功打开过一次） |
| Total TypeScript | [totaltypescript.com](https://www.totaltypescript.com/) |
| GitHub | [github.com/mattpocock](https://github.com/mattpocock)，组织 [total-typescript](https://github.com/total-typescript) |
| YouTube | [@mattpocockuk](https://www.youtube.com/@mattpocockuk)，频道 ID `UCswG6FSbgZjbWtdf_hMLaow` |

首次读取时该账号约 37,683 条帖子、约 39.5 万关注者。这不是“已全部读完”的意思，见下方覆盖说明。置顶帖 ID `2115538750147023323` 本轮返回 not found。

## 本目录里有什么

- [资料索引（表格）](https://docs.google.com/spreadsheets/d/1_6WNb1YgrW-SWE1STQTBek5bXJRD-ZeK_HvHh8Qhe0s/edit)：适合筛选、排序和以后追加行  
- [分类阅读版](https://docs.google.com/document/d/1am3ByZMJ3z7TV8a0f6XgM6VotWmYtcuepP6gFeaOBDM/edit)：按主题浏览  
- [tracking-state.json](https://drive.google.com/file/d/1GxtF43B5cO4pd_t4JcT0TrJrovEiqzfi/view)：给每日增量任务用的账号 ID、已扫范围、去重键和续扫游标  
- [更新日志](https://docs.google.com/document/d/1yjRYjvANeTSsow_fCcG5394N8dFhEDaCgwQlS4Z9K4Q/edit)

当前收录 **161** 条（首次整理），分类如下：

- 官方站点与身份：8 条  
- Total TypeScript 免费教程：4 条  
- Total TypeScript 付费课程介绍：5 条  
- Total TypeScript 系列与工具：5 条  
- Total TypeScript 文章：83 条  
- AI Hero 教程与文章：19 条  
- YouTube 视频与播放列表：9 条  
- 开源项目与代码：16 条  
- X 技术帖与线程：8 条  
- 推荐的第三方资料：4 条

身份字段区分：本人原创、本人账号、本人相关组织、本人访谈/主持、推荐他人作品。付费工作坊只保留公开介绍。

## 覆盖了什么，没覆盖什么

已相对完整或本轮系统查过的部分：

- 官方身份：X 资料、GitHub 用户与组织、YouTube 频道 ID、AI Hero 与 Total TypeScript 主站  
- Total TypeScript 官方 RSS 全部 126 条：83 篇文章（全部建目）、4 个免费教程、5 个付费工作坊公开介绍、34 条 Tips 作为系列而非逐条重复  
- AI Hero 官方 RSS：对路线图、SDK/MCP 教程、Home Repo、skills 目录、Grill Me、Ralph、Plan Mode 等公开文章做了分层收录；不把每条技能说明和 changelog 单独建目  
- 公开 GitHub：分页合并后的非 fork 仓库，以及 total-typescript 组织仓库；只收录代表作  
- YouTube：5 个播放列表标题，以及最近 RSS 中的长视频；Shorts 只作系列说明  
- 公开 X：时间线 1 页 \+ 链接/关键词检索约 8 次读取，作者过滤为 `346640777`，去重后约 156 条候选，再策展技术帖与推荐

X 历史是**按时间窗检索加翻页，不是 37,683 条时间线穷尽**。本轮实际看到的候选帖主要集中在 **2026**，另有一页 **2023 年末** 链接帖；2022、2024、2025 大部分仍待补扫。未翻完的游标见 `tracking-state.json`。

明确缺口与限制：

- 多个检索窗仍有 `next_token`  
- 站点存在间歇 403（WAF）：同一 URL 有时 200、有时 403。403 的文章保留官方 RSS 标题、日期与摘要，不把拦截当成页面不存在，也不编造未读正文  
- `www.mattpocock.com` 与部分 AI Hero/TT 深链不稳定  
- YouTube RSS 只返回最近 15 条，不是全部上传历史  
- 置顶帖 not found  
- 部分 X 短链未展开的推荐条目不猜最终 URL  
- 视频未观看  
- 付费课时未购买、未注册、未收录  
- 只读公开项目，未 checkout、未修改代码  
- 未收入生活闲聊；早期与开发无关的声乐教练经历只在身份说明中提及

## 以后每天怎么更新

1. 用公开 X 接口读取 `@mattpocockuk`（ID `346640777`）在 `since_id` 之后的新帖，不要登录个人 X、不要改关注或点赞。  
2. 同时检查 Total TypeScript RSS、AI Hero RSS、YouTube 频道 RSS（ID `UCswG6FSbgZjbWtdf_hMLaow`）和 GitHub 公开仓库。  
3. 筛 TypeScript / 软件开发 / AI 工程内容；推荐他人作品单独标注。同一教程的文章、视频、推文要去重聚合。付费内容只更新公开介绍。  
4. 站外链接用 WebFetch 或 curl 打开：200 记已核验，404 标注失效，403/超时记未读。不要为了 403 去绕过访问控制。无法阅读的原文不要编摘要。  
5. 按 `dedupe_keys` 追加到《资料索引》，并在《更新日志》写一行。  
6. 若仍有历史游标，在当日额度内继续补扫，不要无限循环（约每分钟 30 次、每天 1000 次、每次最多 25 条）。  
7. 更新 `tracking-state.json` 里的 `newest_post_id`、已扫范围和游标。

日期：有来源才填写。X/RSS 的时间是 UTC，需要时分时换算到 Asia/Singapore（UTC+8）。
