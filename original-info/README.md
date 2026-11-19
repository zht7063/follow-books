# original-info — 五位关注对象的资料目录快照

这是 Google Drive `follows/` 目录里，五位人物**当前已收集资料**的导出快照，准备放入 `follow-book` 仓库的 `original-info/`。它是索引、摘要、来源链接、核验状态、覆盖缺口与更新日志的快照，**不是**原文或音视频的版权全集，也没有另外抓取整篇转载。

本轮只做归档导出，**没有**再做一轮筛选，没有扩充、翻译重写，也没有把材料改写成“人生指南”。筛掉日常内容、只留干货、做成类似「高性价比人生指南」的加工，按用户说明留到以后再做。

导出时间：2026-11-19 16:12 Asia/Singapore (UTC+8)  
源父目录：[follows/](https://drive.google.com/drive/folders/1ZgCrxGcwnVw1xTW2k4W_KESPvVtKqY2P)（ID `1ZgCrxGcwnVw1xTW2k4W_KESPvVtKqY2P`）  
条目总数（以各人物 `index.csv` 实读数据行为准）：**550**

## 此前已经做过的范围筛选（请如实理解）

这五份目录在写入 Drive 时，就已经按「软件开发 / AI / 技术产品构建」及相关推荐资料来收录，并排除纯闲聊、日常动态，以及（对部分人物）泛人生哲学、投资喊单或励志灌水。因此：

- 这里不是五位人物的全部公开言论，更不是人生主题全集。
- 也不是完整原文库；每条只有标题、短摘要和可核验的来源链接。
- 历史 X 检索与部分站外页面仍有缺口，见各人 `tracking-state.json`、`README.md` 和 `updates.md`。不要把本快照当成已经穷尽的档案。

Dan Koe 与 Naval Ravikant 本来就不是以编程教程为主的作者，条目较少是当时筛选后的结果，不是漏导出。

## 目录结构

每个人物一个子目录，文件夹名使用已核验的 X handle：

```
original-info/
  README.md              ← 本说明
  manifest.json          ← 源 Drive ID/URL、相对路径、sha256、条目数，供核对
  poteto/
  karpathy/
  mattpocockuk/
  thedankoe/
  naval/
```

每个人物目录内的五个标准文件：

| 文件 | 来源（Drive 中的名称） | 说明 |
| ---- | ---- | ---- |
| `README.md` | README | 范围、身份、覆盖与缺口说明（Google 文档导出的 Markdown） |
| `index.csv` | 资料索引 | 可筛选索引表；保留标题、类型、主题、日期、身份、摘要、来源链接、核验状态 |
| `reading.md` | 分类阅读版（poteto 在 Drive 中名为「资料索引阅读版」） | 按主题浏览的阅读版 |
| `tracking-state.json` | tracking-state.json | 账号 ID、增量游标、已扫范围、已知缺口 |
| `updates.md` | 更新日志 | 整理与补扫记录 |

Google 文档导出为 Markdown 时，可能出现自动加链或转义（例如 `created\_at`）。这是 Drive 实读结果，不是另外重写。若源表有多个工作表，会另存 `index-tabN-*.csv` 并在 `manifest.json` 记录；本轮五份表均只有 1 个工作表。

## 人物与 Drive 源

### poteto — Lauren Tan

- X：https://x.com/poteto
- Drive 目录：[https://drive.google.com/drive/folders/16SP3eMRJD-YQU6PrnEIbwTT0S29_q8z5](https://drive.google.com/drive/folders/16SP3eMRJD-YQU6PrnEIbwTT0S29_q8z5)（ID `16SP3eMRJD-YQU6PrnEIbwTT0S29_q8z5`）
- 本轮实读条目：**123**
- 分类计数：个人博客（no.lol） 36；会议演讲与幻灯片 23；React Compiler 官方文章 5；开源项目与代码库 26；Grok Bot / Agent / Skills 4；X 技术帖与推荐 29

- `README.md` ← [README](https://docs.google.com/document/d/11EV1esgPuES-AL0sAecRMplwRz2NALzGmavEG1Uv3ks/edit)（ID `11EV1esgPuES-AL0sAecRMplwRz2NALzGmavEG1Uv3ks`）
- `index.csv` ← [资料索引](https://docs.google.com/spreadsheets/d/1hamZPJXwnUlYRNDs-5K2l33DfZjnkUJDVdgkhhl_5eA/edit)（ID `1hamZPJXwnUlYRNDs-5K2l33DfZjnkUJDVdgkhhl_5eA`）
- `reading.md` ← [资料索引阅读版](https://docs.google.com/document/d/1rJQ3Xfgb21VDtyNy8E6VY3zDbuU6Q4qyLL0OVPn38dE/edit)（ID `1rJQ3Xfgb21VDtyNy8E6VY3zDbuU6Q4qyLL0OVPn38dE`）
- `tracking-state.json` ← [tracking-state.json](https://drive.google.com/file/d/1nUAJhSfK1cKaMz4yZ55dOqSExRaGMutV/view)（ID `1nUAJhSfK1cKaMz4yZ55dOqSExRaGMutV`）
- `updates.md` ← [更新日志](https://docs.google.com/document/d/1-C_M8eQ1lFyKT0k-oj3Ix7cUbwrcuweP8u9ZBf7yVIA/edit)（ID `1-C_M8eQ1lFyKT0k-oj3Ix7cUbwrcuweP8u9ZBf7yVIA`）

### karpathy — Andrej Karpathy

- X：https://x.com/karpathy
- Drive 目录：[https://drive.google.com/drive/folders/1Q7i72wDPng3yxj1aRLJz_EqUyN-EKAJL](https://drive.google.com/drive/folders/1Q7i72wDPng3yxj1aRLJz_EqUyN-EKAJL)（ID `1Q7i72wDPng3yxj1aRLJz_EqUyN-EKAJL`）
- 本轮实读条目：**160**
- 分类计数：官方站点与身份 8；课程与系统教程 16；YouTube 通识讲座 4；外部平台演讲与访谈 22；Bear 博客 11；GitHub Pages 博客 21；开源项目与代码 38；论文与学术项目 6；早期实验与演示 4；X 技术帖与线程 20；推荐的第三方资料 10

- `README.md` ← [README](https://docs.google.com/document/d/1_0KbOPIqb_2VrnoZ7NF-bKbnLFaLLo6Y-9AMlLcrxh0/edit)（ID `1_0KbOPIqb_2VrnoZ7NF-bKbnLFaLLo6Y-9AMlLcrxh0`）
- `index.csv` ← [资料索引](https://docs.google.com/spreadsheets/d/1QX3F036L5xWhYL28bx1AfLWcSk8k3U4FwCypWReknI8/edit)（ID `1QX3F036L5xWhYL28bx1AfLWcSk8k3U4FwCypWReknI8`）
- `reading.md` ← [分类阅读版](https://docs.google.com/document/d/1inBAQrFhcgGuhnnDLFA79eXyO1RZRlEnlGNrKUC328M/edit)（ID `1inBAQrFhcgGuhnnDLFA79eXyO1RZRlEnlGNrKUC328M`）
- `tracking-state.json` ← [tracking-state.json](https://drive.google.com/file/d/12gPFZiMc4pACNWltZAjps-v1Pn069GU7/view)（ID `12gPFZiMc4pACNWltZAjps-v1Pn069GU7`）
- `updates.md` ← [更新日志](https://docs.google.com/document/d/1JsRXXOb5QlpfyIf7YSTxD5N20Ft3scyvWTlIIC3rUPY/edit)（ID `1JsRXXOb5QlpfyIf7YSTxD5N20Ft3scyvWTlIIC3rUPY`）

### mattpocockuk — Matt Pocock

- X：https://x.com/mattpocockuk
- Drive 目录：[https://drive.google.com/drive/folders/1QfRajU_xi82Q1iN4en9eMqUTlSv4tbTj](https://drive.google.com/drive/folders/1QfRajU_xi82Q1iN4en9eMqUTlSv4tbTj)（ID `1QfRajU_xi82Q1iN4en9eMqUTlSv4tbTj`）
- 本轮实读条目：**161**
- 分类计数：官方站点与身份 8；Total TypeScript 免费教程 4；Total TypeScript 付费课程介绍 5；Total TypeScript 系列与工具 5；Total TypeScript 文章 83；AI Hero 教程与文章 19；YouTube 视频与播放列表 9；开源项目与代码 16；X 技术帖与线程 8；推荐的第三方资料 4

- `README.md` ← [README](https://docs.google.com/document/d/1Z-MtRwlg5zBK2aZedFs_A9vfS86tdX4yzG80MFCe2H4/edit)（ID `1Z-MtRwlg5zBK2aZedFs_A9vfS86tdX4yzG80MFCe2H4`）
- `index.csv` ← [资料索引](https://docs.google.com/spreadsheets/d/1_6WNb1YgrW-SWE1STQTBek5bXJRD-ZeK_HvHh8Qhe0s/edit)（ID `1_6WNb1YgrW-SWE1STQTBek5bXJRD-ZeK_HvHh8Qhe0s`）
- `reading.md` ← [分类阅读版](https://docs.google.com/document/d/1am3ByZMJ3z7TV8a0f6XgM6VotWmYtcuepP6gFeaOBDM/edit)（ID `1am3ByZMJ3z7TV8a0f6XgM6VotWmYtcuepP6gFeaOBDM`）
- `tracking-state.json` ← [tracking-state.json](https://drive.google.com/file/d/1GxtF43B5cO4pd_t4JcT0TrJrovEiqzfi/view)（ID `1GxtF43B5cO4pd_t4JcT0TrJrovEiqzfi`）
- `updates.md` ← [更新日志](https://docs.google.com/document/d/1yjRYjvANeTSsow_fCcG5394N8dFhEDaCgwQlS4Z9K4Q/edit)（ID `1yjRYjvANeTSsow_fCcG5394N8dFhEDaCgwQlS4Z9K4Q`）

### thedankoe — Dan Koe

- X：https://x.com/thedankoe
- Drive 目录：[https://drive.google.com/drive/folders/1kdYBXgpnOsl6-Wn7qM9oDlvxHjLmJvUZ](https://drive.google.com/drive/folders/1kdYBXgpnOsl6-Wn7qM9oDlvxHjLmJvUZ)（ID `1kdYBXgpnOsl6-Wn7qM9oDlvxHjLmJvUZ`）
- 本轮实读条目：**63**
- 分类计数：官方站点与身份 8；官方产品与课程介绍 2；通讯：AI、工具与数字产品 12；Kortex 与 Eden 产品文章 21；YouTube 视频与播放列表 7；开源与早期代码 1；X 技术帖与线程 10；推荐的第三方资料 2

- `README.md` ← [README](https://docs.google.com/document/d/1elNq1skHSTlB1TL6kLSJfy7m5SupSzhMHYrTKNCOvFQ/edit)（ID `1elNq1skHSTlB1TL6kLSJfy7m5SupSzhMHYrTKNCOvFQ`）
- `index.csv` ← [资料索引](https://docs.google.com/spreadsheets/d/1g5tfWaPOiIAD1xoXZ1S_wgKaZtisluELycaahamKnrE/edit)（ID `1g5tfWaPOiIAD1xoXZ1S_wgKaZtisluELycaahamKnrE`）
- `reading.md` ← [分类阅读版](https://docs.google.com/document/d/1zGQMULBeZm7Pi4PoZSTfiKQJnRVpP_wd-l6D9vACSGc/edit)（ID `1zGQMULBeZm7Pi4PoZSTfiKQJnRVpP_wd-l6D9vACSGc`）
- `tracking-state.json` ← [tracking-state.json](https://drive.google.com/file/d/1TBz4NqUtrGq-FUYsZ3EER224t1WFu7PX/view)（ID `1TBz4NqUtrGq-FUYsZ3EER224t1WFu7PX`）
- `updates.md` ← [更新日志](https://docs.google.com/document/d/1gY7_lJny4gKF6MYU1VnwSoP3Zks7oiRQo5z8IvuU3gg/edit)（ID `1gY7_lJny4gKF6MYU1VnwSoP3Zks7oiRQo5z8IvuU3gg`）

### naval — Naval Ravikant

- X：https://x.com/naval
- Drive 目录：[https://drive.google.com/drive/folders/13224RaQD_7tjsfXMV3KWn4vI6GB4iZ78](https://drive.google.com/drive/folders/13224RaQD_7tjsfXMV3KWn4vI6GB4iZ78)（ID `13224RaQD_7tjsfXMV3KWn4vI6GB4iZ78`）
- 本轮实读条目：**43**
- 分类计数：官方站点与身份 4；官方产品与公司 2；第三方汇编（非亲笔博客） 1；播客与文字稿：AI、编程与前沿产品 11；数字杠杆与一人产品（How to Get Rich 系列） 9；早期创业与产品文章 3；X 技术帖与线程 11；推荐的第三方资料 2

- `README.md` ← [README](https://docs.google.com/document/d/1AecoRUleOcp12vdjXH7Lo7G2UKC5uArPf6fWssez7ow/edit)（ID `1AecoRUleOcp12vdjXH7Lo7G2UKC5uArPf6fWssez7ow`）
- `index.csv` ← [资料索引](https://docs.google.com/spreadsheets/d/1qMDMfr49SgCfZRIUb1e2hReSOpBRVmkuo7q1tysnQFE/edit)（ID `1qMDMfr49SgCfZRIUb1e2hReSOpBRVmkuo7q1tysnQFE`）
- `reading.md` ← [分类阅读版](https://docs.google.com/document/d/1Z8W5j8M8KEoItFXADsIhXzdZUZlSaMwgPxmZKqHCBHw/edit)（ID `1Z8W5j8M8KEoItFXADsIhXzdZUZlSaMwgPxmZKqHCBHw`）
- `tracking-state.json` ← [tracking-state.json](https://drive.google.com/file/d/1gxnEQV2moou-VtGrr_yYX9v27LITPcks/view)（ID `1gxnEQV2moou-VtGrr_yYX9v27LITPcks`）
- `updates.md` ← [更新日志](https://docs.google.com/document/d/1ajFeZr82Wx2UeMZJopIltZAvz2Rvgy2SwLZRCCdUPDA/edit)（ID `1ajFeZr82Wx2UeMZJopIltZAvz2Rvgy2SwLZRCCdUPDA`）

## 当前已知的覆盖限制（摘要）

共同限制：公开 X 历史检索未穷尽；部分分页游标仍留在各自 `tracking-state.json`；部分短链未展开；403/超时页面只标未读，不编造摘要；音视频若无官方文字稿，只记录已核验标题、说明和原链接，不声称已经听过或看过。未购买、注册或订阅付费内容。

- **poteto**：目录现为补扫后的索引（README / 阅读版写明 123 条）。仍有未翻完的历史检索游标；`github.com/poteto/no.lol` 曾 404（站点本身仍在）；部分 Medium / npm / react.dev 深链 / 幻灯片为 403 或原链失效。
- **karpathy**：历史 X 仍有缺口；部分 Medium / Scholar 为 403 未读；个别旧站点无法访问。视频条目未观看录像。
- **mattpocockuk**：历史 X 仍有缺口；部分网页无法读取，已在原目录标注。
- **thedankoe**：不是编程教程作者，目录聚焦 AI 工具、数字产品与构建；历史缺口见其 state。
- **naval**：不是编程教程作者；未穷尽约 2.7 万条时间线；nav.al sitemap 约 241 篇只选读范围内内容；官方 RSS 不是全站目录；2018 年 How to Get Rich 原推特长线起始帖可能仍未扫到；《纳瓦尔宝典》是第三方汇编（Eric Jorgenson 编辑），不能当成他的亲笔博客。

更完整的游标与缺口列表以各人物 `tracking-state.json` 为准。

## 给后续写入 GitHub 的说明

父会话负责仓库核实和写入。本包只提供 `original-info/` 树，不包含仓库的 git 历史，也不应被当成已经同步过的远程仓库。用户没有要求本轮同步以后的 GitHub 更新，这是一次性快照。
