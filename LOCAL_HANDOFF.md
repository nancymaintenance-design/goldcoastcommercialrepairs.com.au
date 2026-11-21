# Gold Coast 本地交付

2026-11-21 已在现有仓库接入 V3 询价区和共享页脚。当前预览用 `python -m http.server 8000 --bind 127.0.0.1 --directory dist`，打开 <http://127.0.0.1:8000/> 或 <http://127.0.0.1:8000/zh/>。下面的 8765 端口说明和上传记录对应此前 V2 交付。`PACKAGE_INFO.json` 和 `PACKAGE_MANIFEST.json` 记录原始 V3 导出包，文件哈希以导出时为准。

本项目接续用户提供的 `E:/Download/gold-coast-v2.zip`，保留 Python 静态生成器、V2 视觉、本地字体、素材和原有交互。正式维护位置为 `E:/Ellis-Services/Gold Coast Commercial Maintenance/source`。

## 运行

使用 Python 3.10 或更新版本，无运行时第三方依赖：

```powershell
python build.py
python preview.py --port 8765
```

打开 <http://127.0.0.1:8765/>；中文 <http://127.0.0.1:8765/zh/>。预览仅绑定本机。退出启动终端或按 Ctrl+C 可停止服务。当前交付时有独立后台预览进程；不要重复占用同一端口。

`preview.py` 只托管 dist，不自动重新构建。修改 Python 模板或 JSON 后再次运行 `python build.py`，刷新页面。CSS/JS 仍由 dist 中现有文件维护，构建不会删除或覆盖它们。

## 本轮改动

| 修改前 | 修改后 |
| --- | --- |
| Windows 默认 GBK 读取 UTF-8 内容失败，无法直接构建 | build.py 六处文本读写明确 UTF-8，输出固定 LF；非 UTF-8 环境回归测试通过 |
| FAQ 搜索无结果仅显示 0 个问题 | 模板生成双语无结果提示，复用 app.js 现有逻辑 |
| 标准 Python 服务的未知地址显示通用错误页 | preview.py 返回 HTTP 404 与原包 dist/404.html；正常目录和斜杠重定向仍由标准处理器负责 |
| 只有包内历史验证说明 | 新增静态检查、浏览器视口检查、交互检查和实际截图 |

V2 配色、CSS、字体、图像、首页组成、12 类服务、8 类物业、6 篇文章、10 条 FAQ、七项导航及双语路线保持原包设计。未增加联系方式、公司证明或已发送状态。

## 验证与复跑

```powershell
python -m unittest discover -s tests
python tests/validate_static.py
node --check dist/app.js
node --check dist/motion.js
```

浏览器检查需本地预览运行，并额外安装开发工具 `python -m pip install playwright`。`tests/browser_audit.py` 中的 CHROME 是本机现有浏览器位置，换电脑需调整为当地 Chromium 可执行文件，或使用 `python -m playwright install chromium` 后在测试中省略 executable_path。

```powershell
python tests/browser_audit.py
python tests/interactions.py
```

浏览器依赖只用于 QA，不影响网站构建或运行。`test_gallery_keyboard.py` 同样使用该浏览器。

报告和截图在同级 `../reports`，总报告为 `交付与验收-2026-11-20.md`。包内 README / CODEX_HANDOFF 原验证记录属于设计交接历史，本轮结果以该报告及 JSON 为准。

## 正式上线准备

原 ZIP 没有 `.git`、origin 或可核验远端主分支。用户随后于本轮授权上传至 https://github.com/nancymaintenance-design/goldcoastcommercialrepairs.com.au ，已核实目标为默认分支 main 的空仓库。本次上传包括最新粉带文案“商业。地产。专业维护。”；Vercel 项目和正式域名仍未配置。`.openai/hosting.json` 是原设计预览的托管标识，仅本地保留且被 Git 忽略，不代表 Vercel 发布目标。

待确认既有 GitHub 仓库、Vercel 项目、实际生产分支后，先核对远端默认分支和未同步改动，再整合；不另建同名项目。预期静态部署参数为项目根目录、构建命令 `python3 build.py`、产物目录 `dist`、不启用单页应用全路径重写。正式运行时需提供 Python 3.10+。

在原目标的预览部署验证：目录式路径、无斜杠至有斜杠规范化、嵌套页面直接打开和刷新、不存在路径返回自定义 404 且 HTTP 状态为 404。正式域名确定前保持 noindex 和 robots 禁抓；本轮保留原预览 canonical/hreflang。

正式发布前，在生成器统一 ORIGIN、canonical、对应 hreflang（含适用的 x-default）、社交图片绝对 URL，生成仅含可索引规范路径的 sitemap.xml，更新 robots 并移除预览 noindex，核对 HTTPS 和单一域名重定向。结构化数据仅使用已确认公司资料；当前未添加未经确认的 LocalBusiness、电话、营业时间、评价或地址。

真实表单需要经确认的服务器接收端和接收邮箱。实现并实测正常、输入错误、服务端失败、重复点击、照片上传以及实际到达邮箱；只有服务器确认成功且链路经过送达验证后启用“已发送”文案。域名、邮箱和后端尚未提供，不能在当前纯静态草稿中完成真实发送验证。

尚缺资料一次列清：

- 黄金海岸电话、邮箱、营业时间与节假日安排。
- 真实询价接收端、测试收件箱、照片接收限制与保存规则。
- 正式域名及控制权、既有 GitHub/Vercel 目标与生产分支。
- 实际服务覆盖边界、当地团队、可公开资质与项目证明。

本轮未推送、未发布，也未发送真实询价。
