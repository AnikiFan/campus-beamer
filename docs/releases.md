# 版本维护与发布 / Version maintenance and releases

[首页](../README.md) · [English](../README.en.md) · [变更记录](../CHANGELOG.md)

## Release Please 发布流程

项目使用 [Release Please Action](https://github.com/googleapis/release-please-action)
维护发行 PR。工作流只在仓库默认分支收到 push 时运行版本管理，不固定分支名称。

1. 普通提交或 squash 合并标题使用 Conventional Commits，例如 `fix: preserve video links`
   或 `feat: add a layout option`。`feat` 增加次版本，`fix` 增加补丁版本；
   `feat!` 或正文中的 `BREAKING CHANGE:` 标记不兼容变化。
   `0.x` 阶段的不兼容变化增加次版本，并在变更记录中写明如何改用新接口。
2. Release Please 创建或更新发行 PR，同时修改 `pyproject.toml`、`uv.lock` 中本项目的版本、
   `.release-please-manifest.json` 和 `CHANGELOG.md`。
   锁文件的其他依赖版本、下载地址和哈希不因项目版本变化而更新。
3. 维护者检查发行 PR 的版本、变更记录、CI 和全部演示页面，再合并。
4. 合并后的默认分支 push 创建 `vX.Y.Z` tag 和 GitHub Release。
   **同一次工作流**随后检出该 tag，运行 Docker 中的 `make release`，上传发行 ZIP，
   并以包内 `RELEASE_NOTES.md` 更新 Release 正文，保留素材许可边界与 PPTX 限制说明。

`pyproject.toml` 的 `[project].version` 是构建版本入口，使用 `MAJOR.MINOR.PATCH`；
`make version` 查看版本。清单中的版本是下一次发行的起点，下一版由新增的 Conventional Commits 决定。
`CHANGELOG.md` 里标为“待发布”的章节表示该版本尚未发布；实际发布时由 Release Please 写入日期。
Release Please 自动生成的新章节自带日期和提交链接，无需手工维护版本号或 tag。
后续发行 PR 应保留根级的“许可与使用范围”章节；打包工具会将其附加到每版发行说明。

配置文件为 [`release-please-config.json`](../release-please-config.json) 和
[`.release-please-manifest.json`](../.release-please-manifest.json)。
Python 策略更新项目版本，额外 TOML 规则按包名精确更新 `uv.lock` 的本项目版本。
Action 固定为 `v4.4.1`；其 TOML 更新器将名称包装在 `value` 节点中，因此筛选规则使用
`@.name.value`。升级 Action 时须重新验证锁文件匹配规则，避免只更新项目文件而遗漏锁文件。
正常发布不手动修改 manifest；需要指定特殊版本时，按
[官方版本覆盖说明](https://github.com/googleapis/release-please#how-do-i-change-the-version-number)
使用提交正文中的 `Release-As: X.Y.Z`，并审核生成的 PR。

## GitHub 仓库配置

项目必须放在**独立仓库根目录**，GitHub 才会读取这里的 workflows。
本目录如果不是 Git 仓库的根目录，这些工作流不会运行。

公开仓库为 [AnikiFan/campus-beamer](https://github.com/AnikiFan/campus-beamer)，
发行包在 [GitHub Releases](https://github.com/AnikiFan/campus-beamer/releases) 下载。
首版 `v0.1.0` 作为 Release Please 的已发布起点；后续版本通过上述发行 PR 流程维护。

- 在 **Settings → Actions → General → Workflow permissions** 中允许 GitHub Actions
  创建和批准 pull requests；发行 PR 由维护者审核后合并。
- 工作流为版本管理 job 声明 `contents`、`issues` 和 `pull-requests` 写权限。
  组织策略也必须允许这些权限。
- 默认可用内置 `GITHUB_TOKEN`。若需要发行 PR 自动触发普通 CI，设置仓库 Actions secret
  **`RELEASE_PLEASE_TOKEN`**，使用能访问该仓库的 fine-grained PAT，
  授予 Contents、Issues、Pull requests 的读写权限。此配置对强制 CI 检查的分支尤其必要。
  不要把令牌写进文件、配置 JSON 或日志。

内置 `GITHUB_TOKEN` 创建的 PR/tag 通常不会触发新的工作流，见
[官方令牌说明](https://github.com/googleapis/release-please-action#other-actions-on-release-please-prs)。
因此附件构建直接接在 Release Please job 后面，不依赖 `release: published` 或 tag push 事件。
若只使用内置令牌，必须另行触发并确认发行 PR 的 CI 检查，不能把缺少检查视为通过。

Release 会先创建，再构建附件。构建失败时 Release 可能暂时没有发行 ZIP；
查看诊断并修复后，使用下方按 tag 手动重试的入口，勿将旧附件当作本次成功构建的结果。

## 本地准备发行包

```bash
make release
# 检查期间需要更小的 PPTX 时：
make release DPI=200
```

`make release` 先检查锁文件同步，再顺序运行 Python 测试、完整演示 draft、演示 PDF/PPTX 导出、
源码打包及版本化发行包生成。默认 600 DPI，始终选择 `example.tex`，
即使本地存在自己的 `main.tex` 也只导出公开演示。
当前版本在 `CHANGELOG.md` 中缺少非空章节，或演示产物缺失时，打包失败。
支持 Release Please 的普通、链接式版本标题及手动的 `[X.Y.Z]` 标题。

`build/releases/campus-beamer-vX.Y.Z-release.zip` 包含：

- `campus-beamer-X.Y.Z-source.zip`：可作为独立仓库根目录的源码包。
- `campus-beamer-X.Y.Z-example.pdf` 与 `campus-beamer-X.Y.Z-example.pptx`：公开功能演示。
- `RELEASE_NOTES.md`：本版变更与素材许可范围。
- `SHA256SUMS`：上述文件的 SHA-256 校验和，解压后运行 `sha256sum -c SHA256SUMS` 校验。

查看 `build/draft/example/` 的全部页面预览与报告；编译成功不替代视觉检查。
源码 ZIP 只包含 `tools/package_source.py` 的逐文件 `FILES` 白名单，包括两份 Release Please 配置。
新增公开文件必须审核后登记；清单外文件默认不打包，清单文件及父目录不得为符号链接。
发布前保留通用 `prompt.md`，并审核已登记文件的内容；白名单不能识别文件中的私人信息。
发行包与演示产物均保存在忽略的 `build/`，不提交源码仓库。

## 手动构建与附件重试

在 Actions 中打开 **Release Please**，点击 **Run workflow**：

- `tag` 留空：构建所选 ref 的发行包，仅上传 Actions artifact，不创建 Release 或上传 Release 附件。
- `tag` 填写已有的 `vX.Y.Z`：检出该 tag，确认它与项目版本一致且 GitHub Release 已存在，
  重建并上传该版发行 ZIP。相同名称的附件被替换，Release 正文更新为包内发行说明。

Actions artifact 保留 14 天；GitHub Release 附件不受此期限影响。
构建失败会上传可用的 LaTeX 日志与 draft 报告。

依赖发生变化时，仍从官方 PyPI 重新生成锁文件：

```bash
env -u UV_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL -u UV_DEFAULT_INDEX \
  uv lock --no-config --default-index https://pypi.org/simple
```

检查版本、下载地址和哈希变化后提交。CI 与 Docker 固定使用 uv `0.12.3`，升级时同步修改并验证。

## English quick guide

Use Conventional Commits for commit messages and squash titles. Release Please
opens a release PR that updates `pyproject.toml`, the local package version in
`uv.lock`, the manifest and `CHANGELOG.md`. The manifest version is the starting
point for the next release. A changelog heading marked pending has not been
published; Release Please writes the date when the release is created. Features bump
minor versions and fixes bump patch versions; breaking changes below 1.0 bump
minor versions and should say how to adopt the new interface. Review CI and all
demo pages before merging.

On merging, the **Release Please** workflow creates `vX.Y.Z` and a GitHub Release,
then checks out that tag and runs Docker `make release` in the same workflow.
It attaches the checksummed source/demo bundle and updates the release body with
bundled notes, including the shared license scope and image-based PPTX limitation.
Keep the top-level license section in the changelog. Releases are created before
the artifact build; retry a failed build manually with the existing tag.

Install this project at a standalone repository root. Allow Actions to create PRs.
Set the optional `RELEASE_PLEASE_TOKEN` Actions secret to a suitable fine-grained
PAT with Contents, Issues and Pull requests write access if release
PRs must automatically trigger CI. The built-in token works for release management
and artifact uploads, but its PR/tag events do not trigger ordinary CI. Required
checks must still be run and reviewed.

Manual **Run workflow** with an empty `tag` builds only an Actions artifact,
retained for 14 days. Supplying an existing `vX.Y.Z` rebuilds and replaces its
release bundle and notes, after checking the tag against the project version.
Run `make release` locally for the same 600-DPI public-demo build; `DPI=200`
is available for previews. Keep dependency locks on official PyPI and review
every public source file before packaging.
