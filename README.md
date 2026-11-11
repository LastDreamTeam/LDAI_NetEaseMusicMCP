# 网易云音乐 MCP

> **自用项目** · 本仓库主要供维护者自用。

使用网易云音乐官方 CLI 查询曲库、音乐库并管理歌单。 本仓库是独立维护的第三方 stdio MCP 连接器。

## 安装运行环境

使用 Python 3.11 或更高版本。在仓库根目录执行 `python -m venv .venv`。Windows 用 `.venv\Scripts\python.exe -m pip install -r requirements.txt` 安装依赖，macOS/Linux 用 `.venv/bin/python -m pip install -r requirements.txt`。

## 连接自己的账户

1. 安装 Node.js 与 npm，运行 `npm install -g @music163/ncm-cli` 安装官方 CLI。
2. 按官方说明配置自己的开放平台 App ID 和私钥，再执行 `ncm-cli login --background`，用 `ncm-cli login --check` 验证。已有可用 CLI 配置的用户可直接复用。CLI 和 MCP 要在同一操作系统账户下运行。[官方认证说明](https://github.com/NetEase/skills/tree/main/ncm-cli-setup)
3. 工具支持分类搜索、个人收藏、每日推荐、歌词、音乐云盘、播客分类、AI 写歌积分，以及收藏歌曲、创建或重命名歌单、增删曲目。后续操作使用搜索结果中的资源 ID。若客户端看不到全局 npm 的 PATH，可设置 `NCM_CLI_JS` 为包声明的 bin 入口，`NCM_NODE` 为 Node 的绝对路径。

## 接入 Cursor、DSH 或 Codex

在仓库目录执行对应命令。生成器使用 Python 3，按当前机器的路径输出可合并的客户端配置。

```sh
python client_config.py cursor
python client_config.py dsh
python client_config.py codex
```

| 客户端 | 配置位置 |
| --- | --- |
| Cursor | 项目 `.cursor/mcp.json` 或用户级 `~/.cursor/mcp.json` 的 `mcpServers` |
| DSH | 当前 profile 的插件列表，启用一条 `@deepseek-ai/dsh-mcp-client` 记录 |
| Codex | `~/.codex/config.toml` 的 `mcp_servers` 条目 |

可重复使用 `--env NAME=VALUE` 传递这些设置：`NCM_CLI_JS`、`NCM_NODE`。涉及密钥的设置只填写私有文件的路径。在客户端刷新工具后先调用 `music_status`。各端使用同一个服务入口，克隆到另一台机器时重新生成路径。仓库另附 Codex 插件清单、图标和技能，可用于打包本地插件。若插件被复制到客户端缓存，可通过进程环境 `LDAI_MCP_PYTHON` 指定已安装依赖的 Python 绝对路径。 [Cursor MCP 文档](https://cursor.com/docs/mcp) · [DSH MCP 客户端](https://github.com/deepseek-ai/deepseek-harness/blob/main/packages/mcp/mcp-client/README.zh.md)

## 实现参考

GitHub 数据核对日期为 2026-11-11。

参照网易官方 CLI 的认证和命令，同时借鉴社区 MCP 的搜索、歌单与推荐工具划分。

- [NetEase/skills](https://github.com/NetEase/skills) · 266 stars，默认分支 7 次提交
- [Vael-KY/netease-music-mcp](https://github.com/Vael-KY/netease-music-mcp) · 221 stars，默认分支 68 次提交

## 许可

本项目以 **GNU Affero General Public License v3.0 only（AGPL-3.0-only）** 发布。分发受许可覆盖的修改版或通过网络向用户提供修改版时，应按许可条款向相应用户提供对应源码。仅在本机自行使用无需公开发布。第三方服务及依赖遵循各自条款。[许可全文](LICENSE)

## 账号管理窗口

在 Codex 对本插件说「管理账号」，或直接运行 python account_manager.py。在窗口中新增连接、编辑显示名和标识、重新连接或断开，修改后刷新客户端工具列表。站点和凭据文件路径仅存当前操作系统用户的配置。已有自定义适配器保留其授权方式；可并行添加原生账号。图形窗口需要 Python 的 Tk 组件，远程无桌面执行器可使用账号 JSON。

重新连接会启动官方 CLI 登录。可查/搜歌单与播客、读我的最爱和订阅电台、按播单 ID 获取节目、红心歌曲、向自建歌单添加歌曲。获取内容需要该账号在网易云开放平台具有相应权限。

## 多账号和终端更新

MCP 入口为 `router.py`，需要 Python 3.11+。主机在本地保存账号配置，默认位置为 `~/.config/ldai-mcp/netease-music/accounts.json`，也可用 `LDAI_ACCOUNTS_FILE` 指定。复制 [两账号示例](examples/accounts.example.json)，将地址与路径换成自己的值。每个 accountHome 对应独立的 HOME、USERPROFILE、APPDATA、LOCALAPPDATA 和 XDG 目录。先用下述 profile_exec.py 在对应环境运行官方 CLI 完成配置和登录。

`ldai_accounts` 仅列出别名和连接状态。配置两个账号后，工具以 `work__` 和 `personal__` 前缀区分，所选工具始终进入该账号的独立子进程。已有单账号配置继续使用原工具名。运行 `python profile_exec.py work -- <程序> <参数…>` 可在同一账号环境完成登录或初始化。完成配置后重新连接 MCP。需要自有适配器时，管理员可为某个账号填写可信 stdio 程序的 `command`、`args` 和 `env`；连接器仅发布当前产品前缀下的业务工具。

安装本仓库后，其他终端可运行 `git pull --ff-only`；Python 服务在其虚拟环境执行 `python -m pip install -r requirements.txt`，随后重新加载客户端。需要固定版本时可检出发布标签。

维护者在 main 提交改进、运行测试，并同步更新 connector.json、两个插件清单的版本，再执行 `python build_plugin.py --push`。此命令将 main 与版本标签一起推送到本仓库，再从已提交文件生成 ZIP。更新既有账号插件时传 `--account-name <既有包名>`，把生成的 ZIP 发布到同一插件。包内 release-source.json 记录精确提交，可与各终端核对。Git 推送与账号插件发布是两个独立步骤。

许可为 **AGPL-3.0-only**。[许可全文](LICENSE)
