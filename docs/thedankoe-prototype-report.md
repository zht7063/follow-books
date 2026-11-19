# Dan Koe 中文连续阅读小样 — 实现报告

记录日期：2026-11-19。当前交付是一个非官方、未完成的小样：五条完整公开短帖、一章原创中文编辑整理。无隶属关系或背书；不是完整书籍、人物传记或 63 条内容语料库。样章已部署到公开预览 URL；针对本样章的真实浏览器验证仍在进行，尚未通过验收，完整验收未完成。等待用户审阅，不扩充来源。

## 范围修正与交付

默认发布方向从此前的人物介绍 / 来源目录改为按序阅读的中文样章：

- 首页先说明范围、如何阅读、5/10 覆盖和全部排除项。
- 一章五段：从开始获得经验，到接受初稿、给修改一个对象、投入时间并复查，最后回到注意力。段落相互承接，每段明确标注“编辑整理”“短引文”“来源”。
- 覆盖说明与编后记交代来源边界和用户审阅关口。前后页、目录、skip link、375px 响应式及无脚本阅读保留。
- 旧 `site/catalog.html`、七个旧章节、旧搜索索引与发布搜索脚本删除。旧采集器、种子元数据、旧编辑文件及历史搜索源代码/测试留作历史材料，不驱动样章。

仓库：[zht7063/follow-books](https://github.com/zht7063/follow-books)。分支：`feat/thedankoe-ebook-prototype`；样章实现起点 SHA：`c92a182e9d17f46151da02d870e4ba562a596290`。继续使用未合并 [PR #2](https://github.com/zht7063/follow-books/pull/2)，不合并、不 rebase、不 amend 已推送提交、不 force push。Git 作者保持 `Engineer (bot) <zht7063@users.noreply.github.com>`。样章实现提交为 `9ab5c94bb92c9c1d0e2d4be2377f15dfd3ada36b`。此次文档更正不改变 `site/` 或语料，不扩大样章。

## 当前五条素材与依据

整个工作流此前通过平台官方公开工具 namespace `x`（非 user-X，不使用用户账户）进行了两次 `search_posts_all`，每次 `max_results=10`。第一次关键词查询返回 `result_count: 0`，是成功空集，不是 403/429；唯一一次修正查询 `from:thedankoe -is:retweet -is:reply` 返回 10 条，均为 DAN KOE / `@thedankoe` / 用户 ID `256523056`。没有翻页、批量 lookup 或后续 X 调用。

工作流根据这些官方响应在本地生成了三份 gitignored JSON：`data/thedankoe/raw/x-api/search-posts-all-01.json`、`data/thedankoe/raw/x-api/search-posts-all-02.json`、`data/thedankoe/raw/x-api/selected-sample-posts.json`。它们不是用户上传的文件。

后续 Codex 实现阶段，我只使用这些已采集的本地文件，没有追加 X / 来源 API 调用，没有抓取作者站，也没有执行部署。这一离线实现阶段不代表整个工作流没有联网；此前的官方公开读取和实现提交推送后的手动部署分别记录于此。导入器、构建器在 CI 和新克隆中仍保持离线。

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

样章 SHA `9ab5c94bb92c9c1d0e2d4be2377f15dfd3ada36b` 已记录的离线套件结果：**48 个 Python 测试 + 8 个 Node 测试，共 56 个**。其中包括原采集器回归、历史种子元数据 / 导出保护、合成临时夹具导入、哈希和日期、失败时不写输出、截断及长文排除、短引文上限、五段来源属性、链接 / 锚点、确定性构建、375px CSS 合同、HTML 转义。历史搜索的 8 个测试用合成数据验证保留工具；站点不再发布该工具。新克隆不依赖私有缓存。实现机器另对可用私有缓存检查未泄露完整 200+ 字符帖子和长文正文。

另一次隐藏实际私有缓存、禁用 socket 的新克隆模拟中，48 个 Python 测试全部通过；没有移动或修改私有缓存。将导入器哈希相等条件临时反向后，夹具测试按预期失败，随后已恢复原代码。独立只读代码审查未发现需要修正的问题，并在内存中确认两份规范化输出与本地原始记录一致。21 个私有文件的前后字节哈希相同，包括停止状态与 HTML/XML 缓存。

自动 CSS/HTML 检查不是视觉验收或完整无障碍审计。**当前样章的真实浏览器验证仍在进行，尚未通过用户视觉验收，完整验收未完成。** 不继承旧版的验收结论。此次文档更正不重新运行构建或测试，上述结果属于样章实现记录。

## 样章预览、部署记录与待完成验收

公开免认证预览 URL：**https://follow-books-thedankoe-preview.vercel.app/**，现已提供此样章。样章提交推送后，工作流手动部署至同一个隔离、无成本的 Hobby 项目：

- 项目：`follow-books-thedankoe-preview` / `prj_mPKRT20m578FfIZz7JoiyD9rTwrK`；团队：`tiansang0824s-projects`。
- 样章 SHA：`9ab5c94bb92c9c1d0e2d4be2377f15dfd3ada36b`。
- 部署 ID：`dpl_Cgyu4kGENUUkP3xR7SUtAExHiHhd`。
- READY 时间：**2026-11-19 18:54:53 +08（Asia/Singapore）**。
- 免认证 HTTP 检查：四份已提交的 `site/` 文件均返回 200，响应字节与该 SHA 一致；旧 `/catalog.html` 和 `/chapters/orientation.html` 返回 404。

团队范围别名仍需 Vercel Authentication；公开阅读使用上面的无团队前缀 `*.vercel.app` 别名。此次手动部署没有建立 Git 集成，没有更改自定义域名、DNS、套餐或其他站点。GitHub Actions 仍只运行离线检查，没有部署步骤；Codex 离线实现阶段本身没有部署。

以上部署和 HTTP 核验属于工作流记录；此次文档更正没有联网复核。HTTP 字节一致性不能替代真实浏览器验收，当前样章的浏览器验证仍在进行。

此前工作流的元数据修复部署记录：

- SHA：`c92a182e9d17f46151da02d870e4ba562a596290`。
- 部署 ID：`dpl_89LRxD7raHVKrhsgwfHLs35TGDTw`。
- **2026-11-19 18:37:21 +08**：公开 catalog 逐字节匹配该 SHA。

更早首部署为 `85a23d6489432ed5858efe4aec343fd6adaeae8c` / `dpl_2F6qqueYBBhUZ1opi2jeY87Kk9Zp`。此前人物介绍 / 来源索引站的首页覆盖说明、章节导航、搜索“AI”=25、无意义查询=0、375×985 视口检查，以及后续 letter-06 元数据修复与 catalog 字节匹配，均属于旧版工作流记录。**这些检查及此前部署不构成本样章的视觉验收或完整验收。** PR #2 保持未合并；用户批准此样章前，不扩大采集、不制作全书。

## 单独保留的历史采集证据

此前作者站采集器在一次有限计划中使用单请求并发、10 秒间隔与 90 次预算，实际第 17 次请求遇到订阅标记后全局停止：16 次成功响应，1 次限制事件；11 条目录来源取得成功，3 条曾被审阅（一个首页、两篇仅开篇片段）。这些是旧采集器事实，不是本样章的内容覆盖数字。历史证据保存在 [collection-summary.json](../data/thedankoe/collection-summary.json)、[request-ledger.json](../data/thedankoe/request-ledger.json) 和旧 review registry。

Codex 离线实现阶段和此次文档更正均没有执行 live 或 export-only，没有重启、删除或改变 `data/thedankoe/raw/state.json` 及其 HTML/XML 缓存。旧限制状态保持原样。这两个阶段均未访问 thedankoe.com、letters.thedankoe.com、Eden、Kortex、YouTube 或其他来源主机，没有追加 API 调用、翻页、视频字幕或保护内容读取。旧种子资料和其他四人的档案不变。

原始 API 响应、HTML/XML、状态、秘密与 token 留在已 gitignored 的私有区域；公开只含原创编辑、短引文、URL 和必要元数据。维持用户审阅关口，等待用户决定样章是否可接受；在批准前不扩大采集或制作全书。此次仅更正文档，不改变 `site/` 或语料，不扩大样章。
