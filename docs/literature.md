# 获取文献与引用次数

[返回首页](../README.md) · [使用手册](usage.md) · [Agent 规则](../AGENTS.md)

`tools/literature.py` 使用 Python 标准库，从 DBLP 搜索和下载 BibTeX，
按 DOI 从 OpenAlex 或 Semantic Scholar 获取引用次数。工具仅依赖 Python 标准库，
可独立于 TeX 环境运行。
默认使用 `python3`；可设置 `make PYTHON=python ...`。

DBLP 的文献搜索用于确定书目信息；引用次数来自所选择的独立提供方，
不同数据库的统计覆盖不同。工具不会混合计数或自动更换来源。
引用次数与检索到的 BibTeX 都不能代替阅读论文来确认研究结论。

用户已提供论文 LaTeX 项目时，agent 优先阅读其中的正文、图注及 `.bib`，
将核实后需要引用的条目写入 `bibliography/main.bib`。
下列在线工具用于用户要求检索，或确认允许补充外部文献之后的场景。

## 搜索 → 选择 → 下载 → 合并

```bash
make literature QUERY="Tensor Fusion Network for Multimodal Sentiment Analysis"
```

输出 JSON，包括 DBLP key、标题、作者、年份、venue、DOI（若搜索记录提供）、
文献页及 BibTeX 地址。默认最多 10 个候选；不会自动选择第一条。
先核对作者、年份和发表版本，区分预印本、会议版、期刊版以及同名论文。
要翻页或查看更多候选，直接使用脚本：

```bash
python3 tools/literature.py search "Tensor Fusion Network" --limit 20 --offset 0
```

以下例子使用该论文的 DBLP key；其他论文应从自己的搜索结果中选择：

```bash
make bibtex DBLP_KEY=conf/emnlp/ZadehCPCM17 CITE_KEY=Zadeh2017TensorFN
```

成功后生成：

- `build/literature/paper.bib`：DBLP 单条标准 BibTeX，以及 `usere` / `userf`。
- `build/literature/paper.json`：DBLP 来源地址、key，以及引用次数、提供方、
  DOI、提供方记录地址和 UTC 查询时间。

`CITE_KEY` 可省略，此时保留 DBLP 原来的 `DBLP:...` key。
获取多篇论文时，用独立的输出路径保留每篇记录：

```bash
make bibtex DBLP_KEY=conf/emnlp/ZadehCPCM17 CITE_KEY=Zadeh2017TensorFN \
  BIB_OUTPUT=build/literature/Zadeh2017TensorFN.bib \
  BIB_REPORT=build/literature/Zadeh2017TensorFN.json
```

核对条目后再合并到本次汇报的文献库，通常为 `bibliography/main.bib`；功能示例使用 `bibliography/refs.bib`。
按 key、DOI、标题检查重复，保留已被幻灯片使用的 key 和已核实的自定义字段。
**不要将现有文献库设为 `BIB_OUTPUT`**：输出是替换单个文件，不是追加数据库。
工具不会自行修改汇报的文献库。
现有演示中的机构、venue、引用数占位符仍需逐项核实。

条目缺少页码、卷期或 DOI 时，应从获准使用的出版方等原始来源补齐，
确实不可获得时明确记录缺失原因，不能凭记忆填入。工具不会推断作者机构或研究结果。

## 查询或更新引用次数

```bash
make citations DOI=10.18653/v1/D17-1115
make citations DOI=10.18653/v1/D17-1115 CITATION_SOURCE=semantic-scholar
```

默认提供方为 OpenAlex。查询只按 DOI 进行；返回的 DOI 必须与输入一致。
JSON 中的 `bibtex_fields` 可以写入已有文献条目，格式如下：

```bibtex
usere = {<实际查询到的非负整数>},
userf = {<OpenAlex 或 Semantic Scholar>, <UTC 查询日期 YYYY-MM-DD>},
```

`paperframe` 会显示这两个字段，引用次数及来源／日期写在同一条引用里。
普通 `\cornercite` 和文末列表不使用它们。
数字会随数据库更新而变化，不把工具运行示例中的数字当作当前值。

可以保存现有文献的查询快照：

```bash
python3 tools/literature.py citations 10.18653/v1/D17-1115 \
  --output build/literature/Zadeh2017TensorFN-count.json
```

只需要书目、不需要联网查询引用次数时：

```bash
make bibtex DBLP_KEY=conf/emnlp/ZadehCPCM17 CITATION_SOURCE=none
```

`none` 不生成引用数快照，报告中的 `citation_snapshot` 为 `null`。
没有 DOI 的 DBLP 条目也使用这个模式；工具不会根据模糊标题猜测引用次数。
接口返回真正的整数 `0` 才表示零引用。缺少数据、找不到记录或请求失败都会报错，
不会把失败写成零次引用，也不会覆盖上一次成功的结果。失败后留下来的文件不能当作这次的查询结果。

## API 密钥与请求错误

按需要在运行环境中配置 `OPENALEX_API_KEY` 或 `SEMANTIC_SCHOLAR_API_KEY`。
工具不会加载 `.env`、要求密钥作为命令参数，或把密钥写进输出报告。
OpenAlex 密钥只发送到 `api.openalex.org`，Semantic Scholar 密钥只发送到
`api.semanticscholar.org`；跨服务重定向会被拒绝。账号、额度及当前认证要求
以各提供方的官方说明为准：

- [DBLP 搜索 API](https://dblp.org/faq/How+to+use+the+dblp+search+API.html)
- [DBLP 单条记录与 BibTeX 地址](https://blog.dblp.org/2020/08/18/new-dblp-url-scheme-and-api-changes/)
- [OpenAlex API](https://help.openalex.org/api/) 与 [DOI 单条查询](https://help.openalex.org/api/get-single-entities/)
- [Semantic Scholar 官方 API 教程](https://www.semanticscholar.org/product/api/tutorial)

默认每次请求超时 20 秒；可在子命令之前设置 `--timeout 30`。
对于限流和部分临时服务错误最多重试两次；较长的等待要求会直接报错，
不持续占用 agent。401/403/404/429、网络故障和验证页面均会明确报告。

DBLP 有时会对脚本请求返回 HTML 验证页面，即使 HTTP 状态是 200。
工具会识别并拒绝将它保存为 BibTeX。可尝试官方 Trier 镜像：

```bash
make literature QUERY="Tensor Fusion Network" DBLP_HOST=dblp.uni-trier.de
make bibtex DBLP_KEY=conf/emnlp/ZadehCPCM17 DBLP_HOST=dblp.uni-trier.de
```

若仍需浏览器验证，从 DBLP 文献页下载**单条标准 BibTeX**（`param=1`，
不要选依赖 `crossref` 的格式），再传入本地文件：

```bash
make bibtex DBLP_KEY=conf/emnlp/ZadehCPCM17 \
  INPUT_BIB=build/literature/download.bib CITE_KEY=Zadeh2017TensorFN
```

此时只跳过 DBLP 的网络下载，仍检查原始条目的 DBLP key，再查询引用次数。
加上 `CITATION_SOURCE=none` 可完全离线处理该下载文件。
本地导入只支持单条、自包含的字面值 BibTeX，不支持 `@string`、字段拼接或多条数据库。
这一路径不会声称重新在线核验了本地文件的来源。

Agent 应先遵循 `AGENTS.md` 的外部资料授权边界；用户已明确要求检索时，无需逐篇再次询问。
生成最终汇报前，核对条目、实际论文内容和备注中的来源说明，再使用正常的 draft／make 流程。
