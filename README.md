# follow-books — 从开始到专注

一个**非官方、未完成的中文连续阅读小样**：五条完整公开 Dan Koe X 短帖、一章五段原创中文编辑整理、覆盖说明。中文由 Engineer (bot) 原创；英文短引文、来源和编辑意见分别标注。无隶属关系或背书，不是完整书籍或人物传记。交付此样章后停止，等待用户审阅，不扩充来源。

此次修正了旧版方向：默认首页不再是人物介绍或 63 条种子来源导航；`site/` 只含首页、样章、覆盖说明及 CSS。旧种子数据、采集器和历史编辑文件仅作为此前工作证据保留，不驱动样章，也不代表读过所有种子条目。其他四人的档案与 `original-info/` 不变。

## 离线构建与检查

Python 3.13+、Node 24+；无第三方依赖，无需安装包。

```bash
npm run build
npm test
npm run check
python3 scripts/validate_content.py
```

新克隆无需私有缓存即可构建、测试和验证。公开规范化记录已提交；导入器测试用公开短引句加明确标识的合成文字构造临时数据，不提交真实的 200+ 字符帖子全文或 API 响应。历史搜索工具保留 8 个独立回归测试，默认站点不发布搜索脚本或索引。

仅在已有三份私有本地文件的本机，可复现导入（不联网）：

```bash
python3 scripts/import_x_sample.py
```

缺少文件即失败，不会回退网络，也不打印响应内容。导入器交叉核对官方响应和选帖记录的作者、UTC 日期、范围、完整性、长度、UTF-8 SHA-256 与引文。公开输出只包含必要元数据和短引文；构建器仅使用公开规范化文件、原创编辑 JSON 和 CSS，不读原始缓存。

## 本次材料覆盖

此前官方 `x.search_posts_all` / namespace `x`（无用户账户）的首次关键词查询成功返回 **0** 条，不是 403/429；一次修正查询 `from:thedankoe -is:retweet -is:reply`，`max_results=10`，取得 **10** 条。本次实现没有追加 X 调用，没有翻页。

样章按主题而非时间排序，选用五条独立的 `complete_short_post`：

| 样章来源 | Post ID | 新加坡发表时间（+08 / Asia/Singapore） | 完整文字字符数 |
| --- | --- | --- | ---: |
| x-sample-01 | 2121636177702727868 | 2026-11-15 00:07:37 | 68 |
| x-sample-02 | 2118387157794496581 | 2026-11-06 00:57:10 | 266 |
| x-sample-03 | 2122717500014022904 | 2026-11-17 23:44:24 | 263 |
| x-sample-04 | 2119463899774767513 | 2026-11-09 00:15:46 | 277 |
| x-sample-05 | 2116156997712195646 | 2026-10-30 21:15:19 | 205 |

作者统一为 DAN KOE / `@thedankoe` / `256523056`；日期来自官方 `created_at` UTC，再换算为新加坡时间。显示范围覆盖全部已取得文字，句末完整，`conversation_id` 等于帖 ID，`note_post` 为空；不作为串文或长文，不声称读取回复。仅 68 字符的一句短帖完整引用，其余各取一个短句（每条不超过 120 字符、25 个英文词）。

其余五条不进入正文：

- `2116921689426583713`、`2114027336421032268`：句中截断预览，绝不猜补。
- `2122374187935523045`：附带链接目标未取得，不推断内容。
- `2117664712532123680`：《The most lucrative AI business to start in 2027》，plain_len 20156；长文不转载、不概括为本样章正文。
- `2112586533610156368`：《The influencer is dead. The Age of Experience is here.》，plain_len 16373；同上。

[来源元数据](data/thedankoe/sample-sources.json)、[覆盖记录](data/thedankoe/sample-coverage.json)、[原创样章](editorial/thedankoe/sample-chapter.json) 是当前内容边界。旧 63 条种子目录、旧人物介绍/索引和未取得或未读条目均不作为样章素材。

## 预览与验收状态

公开预览 URL：**https://follow-books-thedankoe-preview.vercel.app/**，同一隔离 Hobby 静态项目 `follow-books-thedankoe-preview`。**本次推送后待另行重新部署；该 URL 尚不代表此样章版本。** 本轮不部署、不改 Vercel、DNS、域名或 Git 集成，不启动托管或认证流程。

此前元数据修复部署：SHA `c92a182e9d17f46151da02d870e4ba562a596290`，部署 ID `dpl_89LRxD7raHVKrhsgwfHLs35TGDTw`；在 **2026-11-19 18:37:21 +08**，公开 catalog 已逐字节匹配该 SHA。这是用户提供的历史事实，本轮未访问预览或来源站验证。

**当前样章尚未获得用户视觉验收，也未宣称完整验收。** 离线 HTML/CSS 合同检查覆盖 375px 布局、可见来源、跳读链接、前后页、对比度和无脚本阅读；它们不等于浏览器截图或视觉验收。PR #2 保持未合并；本次只提交并常规推送到现有分支。

## 文件与历史边界

```text
scripts/import_x_sample.py             固定五条样本的离线导入与公开模式校验
scripts/build_site.py                  默认中文样章构建器
scripts/validate_content.py            当前样章校验 + 历史采集器校验函数
editorial/thedankoe/sample-chapter.json 原创中文编辑稿
 data/thedankoe/sample-sources.json    公开元数据、哈希与短引文
 data/thedankoe/sample-coverage.json   10 条结果 / 5 条选用 / 5 条排除
 data/thedankoe/raw/                  已忽略的私有响应、HTML/XML、停止状态
site/                                 可独立服务的三页静态小样
```

此前作者站采集在第 17 次请求遇到订阅限制后全局停止，历史汇总和请求账本保留。本轮不运行 live 或 export-only 采集，不恢复、修改或删除停止状态及 HTML/XML 缓存，不访问作者站、Eden、Kortex、YouTube 或其他来源主机。私有 API 响应、长文正文、受保护通讯、秘密和 token 不进入公开树。构建及 CI 全部离线，无部署步骤。

[实现报告](docs/thedankoe-prototype-report.md) 记录本次范围修正、验证和此前证据。完成后在用户审阅关口停止。
