# follows/poteto — Lauren Tan 软件开发资料库

这是 `@poteto`（Lauren Tan）的软件开发资料目录，用来长期跟踪她的博客、演讲、开源项目，以及她在 X 上提到的站外教程与代码。目录只做索引和摘要，不转载原文。

同级以后可以继续增加 `follows/<handle>/`，追踪其他人。

## 她是谁

| 项 | 内容 |
| :---- | :---- |
| X | [x.com/poteto](https://x.com/poteto)，数字 ID `2832427459`，展示名 lauren |
| 账号创建 | 2014-09-26（来自公开资料，UTC） |
| 曾用 handle | 早期回复里普遍称呼 `@sugarpirate_`，与当前账号为同一用户 ID，视为更名而非第二个目标账号 |
| 误写 handle | 部分 react.dev 作者链指向 `@potetotes`，公开查询该 handle 不存在，应以 `@poteto` 为准 |
| 当前工作 | 资料简介写 grok @bot at @SpaceXSI，React Compiler core team；此前 Cursor、Meta、Netflix |
| 资料链接 | [x.ai/bot/plugin/9717366](https://x.ai/bot/plugin/9717366) |
| 博客 | [no.lol](https://www.no.lol/) |
| GitHub | [github.com/poteto](https://github.com/poteto) |
| 幻灯片 | [speakerdeck.com/poteto](https://speakerdeck.com/poteto) |
| 历史 Medium | [medium.com/@sugarpirate](https://medium.com/@sugarpirate)（抓取仍为 403，未读） |

首次读取时该账号约 8203 条帖子、约 31.4 万关注者。这不是“已全部读完 8203 条”的意思，见下方覆盖说明。

## 本目录里有什么

- [资料索引（表格）](https://docs.google.com/spreadsheets/d/1hamZPJXwnUlYRNDs-5K2l33DfZjnkUJDVdgkhhl_5eA/edit)：适合筛选、排序和以后追加行  
- [资料索引（分类阅读版）](https://docs.google.com/document/d/1rJQ3Xfgb21VDtyNy8E6VY3zDbuU6Q4qyLL0OVPn38dE/edit)：按主题浏览  
- [tracking-state.json](https://drive.google.com/file/d/1nUAJhSfK1cKaMz4yZ55dOqSExRaGMutV/view)：给每日增量任务用的账号 ID、已扫范围、去重键和续扫游标  
- [更新日志](https://docs.google.com/document/d/1-C_M8eQ1lFyKT0k-oj3Ix7cUbwrcuweP8u9ZBf7yVIA/edit)

当前收录 **123** 条（首次 97 条，本轮新增 26、修订 18），分类如下：

- 个人博客（no.lol）：36 条  
- 会议演讲与幻灯片：23 条  
- React Compiler 官方文章：5 条  
- 开源项目与代码库：26 条  
- Grok Bot / Agent / Skills：4 条  
- X 技术帖与推荐：29 条

身份字段区分：本人原创、合著、本人原创后移交维护、推荐他人作品、推荐/相关（例如她多次演示但仓库在 cursor/plugins 下的 pstack）。

## 覆盖了什么，没覆盖什么

已相对完整或本轮补齐的部分：

- no.lol 博客 RSS 中的 33 篇文章，链接全部 HTTP 200  
- no.lol/speaking 列出的会议演讲，以及 Speaker Deck 上对应的开发主题幻灯片；本轮为多场补上了独立录像（Reactathon、RubyConf、Code Europe、Elixir Factory、ElixirConf、EmberCamp、EmberConf 2016、两场 Øredev、Netflix UI JS Talks）  
- 开源仓库：hiring-without-whiteboards、terraform、monkers，已移交的 Ember addon，以及本轮补上的 ember-crumbly（当前在 poteto 账号下已归档）、ember-metrics、ember-macaroni、ember-toggle-helper、ember-test-component、ember-deep-set、ember-route-action-helper 等  
- 她作为作者或合著者出现的 React Compiler 官方博文，以及她指向的库作者文档 / Next.js 接入文档  
- 2026 年 Grok Bot 自动化文章、AIE 演讲录像，以及 pstack skills（含本轮补充的上手说明与 verification skill 链接）

X 历史是**按时间窗检索加翻页，不是 8203 条时间线穷尽**。本轮继续使用公开 X 接口，按已保存游标翻页，并核验短链与已知缺口；约使用 29 次公开读取。无 `start_time` 的搜索看起来偏近期，所以历史检索都加了时间窗。只收录 `author_id=2832427459` 的帖。

本轮已结束的检索窗：2014–2016 / 2018–2020 / 2020–2022 / 2022–2024 技术关键词，以及 hiring-without-whiteboards 专题。仍有未翻完的游标，见 `tracking-state.json` 的 `backfill_cursors`。

明确缺口与限制：

- 部分时间窗仍有 `next_token`，应由已启用的每日任务继续翻页，不要无限循环  
- 未宣称收录已删帖、平台未返回或不可访问的内容  
- `github.com/poteto/no.lol` 本次 GET 仍为 404，博客站点仍在  
- Medium 首页及部分历史 Medium / npm 页面 403，未读，不编造摘要  
- EmberFest 录像原 pusher.com 链接仍为 404  
- @16kbps Rust 演讲幻灯片 becca.ooo/rustconf/2020 为 403 未读  
- 推荐的 @edeblois ember-cli 讲座原 X 帖 404  
- 部分 react.dev/learn 深链 403 未读  
- Netflix UI JS Talks 的 YouTube 页 200 但 oembed 403，未读取平台标题  
- 非软件开发闲聊、纯会议社交、以及 Speaker Deck 上的非开发主题未收入

## 以后每天怎么更新

1. 用公开 X 接口读取 `@poteto`（ID `2832427459`）在 `since_id` 之后的新帖，不要登录个人 X、不要改关注或点赞。  
2. 筛软件开发相关内容：博文、演讲、仓库、教程、有实质内容的技术回复和长线程；推荐他人作品单独标注。  
3. 抽出站外链接，用 WebFetch 或 curl 打开：200 记已核验，404 标注失效，403/超时记未读。不要为了 403 去绕过访问控制。  
4. 按 `dedupe_keys`（帖子 ID、conversation\_id、规范化 URL）去重后追加到《资料索引》，并在《更新日志》写一行。  
5. 若仍有历史游标，在当日额度内继续补扫，不要无限循环（公开读取限制约为每分钟 30 次、每天 1000 次）。  
6. 更新 `tracking-state.json` 里的 `newest_post_id`、已扫范围和游标。翻完的窗口从 `backfill_cursors` 删除。

日期：有来源才填写。X 的 `created_at` 是 UTC，写入日志或需要时分时应换算到 Asia/Singapore（UTC+8）。
