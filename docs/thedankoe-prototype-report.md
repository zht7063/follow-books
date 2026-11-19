# Dan Koe 中文连续阅读小样 — 实现报告

记录日期：2026-11-19。当前交付是一个非官方、未完成的小样：五条完整公开短帖、一章原创中文编辑整理。无隶属关系或背书；不是完整书籍、人物传记或 63 条内容语料库。样章尚未获得用户视觉验收，完整验收未完成。交付后停止，等待用户审阅，不扩充来源。

## 范围修正与交付

默认发布方向从此前的人物介绍 / 来源目录改为按序阅读的中文样章：

- 首页先说明范围、如何阅读、5/10 覆盖和全部排除项。
- 一章五段：从开始获得经验，到接受初稿、给修改一个对象、投入时间并复查，最后回到注意力。段落相互承接，每段明确标注“编辑整理”“短引文”“来源”。
- 覆盖说明与编后记交代来源边界和用户审阅关口。前后页、目录、skip link、375px 响应式及无脚本阅读保留。
- 旧 `site/catalog.html`、七个旧章节、旧搜索索引与发布搜索脚本删除。旧采集器、种子元数据、旧编辑文件及历史搜索源代码/测试留作历史材料，不驱动样章。

仓库：[zht7063/follow-books](https://github.com/zht7063/follow-books)。分支：`feat/thedankoe-ebook-prototype`；本次起点 SHA：`c92a182e9d17f46151da02d870e4ba562a596290`。继续使用未合并 [PR #2](https://github.com/zht7063/follow-books/pull/2)，不合并、不 rebase、不 amend 已推送提交、不 force push。Git 作者保持 `Engineer (bot) <zht7063@users.noreply.github.com>`。最终提交 SHA 写入仓库外结果说明，避免在同一个提交中自引用。

## 当前五条素材与依据

仅使用用户已提供的三份 gitignored 本地 JSON：`search-posts-all-01.json`、`search-posts-all-02.json`、`selected-sample-posts.json`。本轮没有 X / 网络 API 调用，没有作者站或其他来源主机请求。

此前官方 `x.search_posts_all`，namespace `x`，无用户账户：第一次关键词查询返回 `result_count: 0`，结果为成功空集，不是 403/429。一条修正查询 `from:thedankoe -is:retweet -is:reply`，`max_results=10`，取得 10 条，均为 DAN KOE / `@thedankoe` / 用户 ID `256523056`。不翻页，不扩展来源。

| 样章顺序 | Post ID | 官方 created_at（UTC） | 新加坡显示时间（+08 / Asia/Singapore） | 文字字符数 |
| --- | --- | --- | --- | ---: |
| x-sample-01 | 2121636177702727868 | 2026-11-14T16:07:37.000Z | 2026-11-15 00:07:37 | 68 |
| x-sample-02 | 2118387157794496581 | 2026-11-05T16:57:10.000Z | 2026-11-06 00:57:10 | 266 |
| x-sample-03 | 2122717500014022904 | 2026-11-17T15:44:24.000Z | 2026-11-17 23:44:24 | 263 |
| x-sample-04 | 2119463899774767513 | 2026-11-08T16:15:46.000Z | 2026-11-09 00:15:46 | 277 |
| x-sample-05 | 2116156997712195646 | 2026-10-30T13:15:19.000Z | 2026-10-30 21:15:19 | 205 |

这是主题顺序，不是时间顺序。五条均为 `complete_short_post`：完整 display_text_range、完整句末、conversation_id 等于帖 ID、note_post 为空，未作为串文或长文，也不声称读取了回复。

公开记录带作者、原 URL、UTC 与新加坡日期、长度、完整性、对话范围说明、完整已取得文字的 UTF-8 SHA-256、官方 API 和本地文件来源依据。只保留短引文：68 字符的一句话可全文引用，其余每条一个短句，不超过 120 字符和 25 个英文词。哈希的对象是私有已取得文字，不是短引文；哈希并不意味着公开了全文。

## 未使用的五条结果

- `2116921689426583713`、`2114027336421032268`：句中截断预览，不补写、不纳入正文。display_text_range 匹配所见预览本身不足以证明完整。
- `2122374187935523045`：附带链接目标未取得，不推断链接内容。
- `2117664712532123680`：《The most lucrative AI business to start in 2027》，plain_len 20156。长 X 文章不转载，不作为样章正文。
- `2112586533610156368`：《The influencer is dead. The Age of Experience is here.》，plain_len 16373。同上。

旧 63 条种子目录、旧人物介绍 / 来源索引、未取得或未读的种子条目不作为这章素材。不借未读条目填补第六篇，不概括为已读内容。

## 实现与验证

`import_x_sample.py` 没有网络代码，只读三个指定本地文件；缺失即失败。选帖记录与官方结果逐项交叉验证，重算 UTF-8 SHA-256、字符长度及时区，验证短引文确实在所取文字中，再用白名单写两个公开文件。验证全部通过前不写输出。长文只保留标题、长度和排除原因。

`build_site.py` 仅读 `sample-sources.json`、`sample-coverage.json`、原创 `sample-chapter.json` 和 CSS，不读私有原始 API 或旧目录。固定五条来源顺序和公开字段模式，输出 HTML 转义，使用严格 CSP，无远程资源、JavaScript 或表单。重建会删除明确列举的旧生成文件，不递归清理任意输出目录。

无第三方依赖。完整离线命令：

```bash
npm run build
npm test
npm run check
python3 scripts/validate_content.py
```

本次离线套件：**48 个 Python 测试 + 8 个 Node 测试，共 56 个**。其中包括原采集器回归、历史种子元数据 / 导出保护、合成临时夹具导入、哈希和日期、失败时不写输出、截断及长文排除、短引文上限、五段来源属性、链接 / 锚点、确定性构建、375px CSS 合同、HTML 转义。历史搜索的 8 个测试用合成数据验证保留工具；站点不再发布该工具。新克隆不依赖私有缓存。实现机器另对可用私有缓存检查未泄露完整 200+ 字符帖子和长文正文。

另一次隐藏实际私有缓存、禁用 socket 的新克隆模拟中，48 个 Python 测试全部通过；没有移动或修改私有缓存。将导入器哈希相等条件临时反向后，夹具测试按预期失败，随后已恢复原代码。独立只读代码审查未发现需要修正的问题，并在内存中确认两份规范化输出与本地原始记录一致。21 个私有文件的前后字节哈希相同，包括停止状态与 HTML/XML 缓存。

自动 CSS/HTML 检查不是视觉验收或完整无障碍审计。当前小样未在公开 URL 重新部署，未进行样章浏览器视觉验收，不继承旧版的验收结论。

## 预览、此前部署与本次不部署

公开预览 URL：**https://follow-books-thedankoe-preview.vercel.app/**。同一隔离的 Hobby 静态项目：`follow-books-thedankoe-preview`（`prj_mPKRT20m578FfIZz7JoiyD9rTwrK`）。本次推送后待另行重新部署，当前公开 URL 不代表样章已发布。

用户提供的上一轮元数据修复部署事实：

- SHA：`c92a182e9d17f46151da02d870e4ba562a596290`。
- 部署 ID：`dpl_89LRxD7raHVKrhsgwfHLs35TGDTw`。
- **2026-11-19 18:37:21 +08**：公开 catalog 逐字节匹配该 SHA。

这些是历史记录，本轮没有网络复核。更早首部署为 `85a23d6489432ed5858efe4aec343fd6adaeae8c` / `dpl_2F6qqueYBBhUZ1opi2jeY87Kk9Zp`，旧目录首页、导航、搜索和 375×985 视口曾有浏览器检查；这些仅适用于旧版，不是本样章视觉验收。

本轮不部署，不改变 Vercel、域名、DNS、Git 集成、认证、套餐或其他站点；不启动托管 / 认证流程。现有 GitHub Actions 只运行离线检查，无部署步骤。

## 单独保留的历史采集证据

此前作者站采集器在一次有限计划中使用单请求并发、10 秒间隔与 90 次预算，实际第 17 次请求遇到订阅标记后全局停止：16 次成功响应，1 次限制事件；11 条目录来源取得成功，3 条曾被审阅（一个首页、两篇仅开篇片段）。这些是旧采集器事实，不是本样章的内容覆盖数字。历史证据保存在 [collection-summary.json](../data/thedankoe/collection-summary.json)、[request-ledger.json](../data/thedankoe/request-ledger.json) 和旧 review registry。

本轮没有执行 live 或 export-only，没有重启、删除或改变 `data/thedankoe/raw/state.json` 及其 HTML/XML 缓存。旧限制状态保持原样。未访问 thedankoe.com、letters.thedankoe.com、Eden、Kortex、YouTube 或其他来源主机。没有新 API、翻页、视频字幕或保护内容读取。旧种子资料和其他四人的档案不变。

原始 API 响应、HTML/XML、状态、秘密与 token 留在已 gitignored 的私有区域；公开只含原创编辑、短引文、URL 和必要元数据。交付在此次提交及常规推送、仓库外结果记录后停止，等待用户决定样章是否可接受。
