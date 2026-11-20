# 黄金海岸商业维护网站 — V2 设计与 Codex 交接

更新日期：2026-11-20
当前视觉版本：**V2 · 冲浪海报 × 海滩俱乐部 × 热带夏日**

## 1. 当前决定：V2 替代 V1

用户已明确拒绝第一版安静、克制的度假杂志风，要求更强的设计感、更多动画和明显的视觉冲突；随后进一步要求黄金海岸站必须具有独立风格，不能接近墨尔本商业维修站。

**后续开发以 V2 为唯一视觉基线。** 保留墨尔本站的内容分工，使用黄金海岸特有的海岸、泳池、条纹遮阳伞、冲浪海报、沙滩俱乐部与夏日活动语言重新组织视觉。原有基础 CSS 仍有用途，但其中 V1 的视觉值不再是设计依据。

以下方向已被替代，不能在后续“优化”中恢复：浅色左右分栏首屏、安静的度假杂志排版、衬线斜体强调和轻微装饰性动效。也不能套用墨尔本站的电光蓝、荧光绿、建筑分层模型及工程科技背景。

`DESIGN.md` 记录设计决策；`dist/maximal.css` 中的 `--gc-*` 是运行时统一色值，`dist/interiors.css` 继续使用同一套变量。

## 2. 七大主导航保持不变

**首页、服务内容、商业类型、新闻、FAQ、关于我们、联系我们。**

地区信息保留在首页、联系页和具体业务内容中，不增加第八项地区主导航。英语和简体中文一一对应；服务详情、商业类型详情与文章均保留可直接打开和刷新的独立路径。

| 栏目 | V2 内容与页面表现 |
| --- | --- |
| 首页 | 全幅海岸首屏与超大海报字 → 交叉移动色带 → 服务索引与现场场景图 → 商业类型横向推进 → 海盐、日晒、骤雨维护 → 施工安排 → 新闻横向浏览 → FAQ → 询价入口 |
| 服务内容 | 十二类服务与建筑／系统／室外筛选，使用醒目的海报式条目；详情说清范围、进场与交付 |
| 商业类型 | 八类物业，以酒店度假村、公寓共同物业、餐厅咖啡馆为前列；图像采用错位海报墙与场景集合 |
| 新闻 | 六篇海岸维护与物业运营文章；大幅封面、分类筛选与彩色版面，正文保持可读 |
| FAQ | 十条主要问答，醒目的搜索与分类面板、可展开的答案 |
| 关于我们 | 第一人称说明范围、协调和交付，配合大标题、海报式承诺和真实工作步骤 |
| 联系我们 | 物业、地区、需求、联系信息与照片选择；彩色询价桌面式布局，本版生成本地草稿 |

## 3. V2 视觉规范

| 项目 | 当前规范 |
| --- | --- |
| 深棕墨色 | `#241611`，用于主要文字、描边与硬阴影 |
| 日落橙 | `#FF642D`，用于主色块与强调 |
| 珊瑚粉 | `#FF90BF`，与橙、青、黄形成强对比 |
| 泳池青 | `#33E1D3`，强化海水与泳池联想 |
| 日光黄 | `#FFE34D`，用于海报字与明亮段落 |
| 阅读纸色 | `#FFF8E8`，服务于长文和输入区域，不能重新主导成安静杂志风 |
| 英文标题 | **Bowlby One SC**，本地 CSS 别名 **`Surf Display`**；见 `dist/surf-font.css` |
| 正文与中文 | DM Sans 正文；中文使用本地 Noto Sans SC 100–900 变量黑体子集，并独立处理字号、行高和断行 |
| 首屏 | 全幅海岸场景、大面积海报字与可识别的商业维护名称，海浪边界衔接下一段 |
| 图像 | 海岸、泳池、条纹伞、露台和商业场景；成年泳装游客自然融入环境 |
| 形状与层次 | 太阳放射形、遮阳伞扇面、海浪、沙滩条纹、硬边海报、深色描边、错位硬阴影和照片叠放 |
| 页面节奏 | 阳光黄、深棕墨、珊瑚粉、泳池青与日落橙大色块交替；正文和操作区域保留清晰阅读空间 |

图片的作用是建立黄金海岸场景感。生成图和图库图继续标为示意素材，不作为公司已完成项目、真实当地客户或公司施工团队的证明。

## 4. 动效与操作约束

V2 的动效包含首屏图片与标题视差、海报字入场、交叉移动色带、旋转太阳与遮阳伞、浪潮边界、照片焦点变化、桌面横向场景推进、卡片倾斜及磁吸按钮。动效应与海岸主题和页面结构相连，不能重新变成建筑科技演示。

- **桌面宽度 ≥1024px**：商业类型集合可使用 sticky 横向推进，由普通页面纵向滚动映射到原生轨道的 `scrollLeft`。移动端改为原生横向滑动，保留前后按钮。
- 轨道的自身横向滚动不立即被纵向映射覆盖；不要拦截滚轮或通过 `preventDefault` 卡住页面。
- 激活桌面 pin 时，轨道使用 `scroll-snap-type: none` 与 `scroll-behavior: auto`；移动端与暂停状态保留正常浏览方式。
- 倾斜只对桌面精细指针启用，最大 6 度；磁吸最多 5px。正常鼠标指针、焦点边框和按钮文字始终可用。
- 顶部动效开关随时可用。暂停时内容全部可见、持续动画停止、变量回到中性值，长 pin 区域恢复正常文档流。
- 系统 `prefers-reduced-motion` 优先，不能通过页面按钮强制恢复滚动及自动动效。后台页面停止动画帧，持续 CSS 动画可通过 `motion-hidden` 暂停。
- `motion.js` 使用 dirty 标记和单次 `requestAnimationFrame` 调度，不依赖 GSAP；仅保存一个动画暂停偏好，不保存询价个人信息。

### CSS 与脚本接口

| 节点 | 动效变量 |
| --- | --- |
| `.scroll-progress` | `--page-progress`：0–1 |
| `.hero-scroll` | `--hero-progress`：0–1 |
| `[data-tide]` | `--tide-progress`：进入至离开视口的推进值 |
| `[data-parallax]` | `--parallax`：−1 至 1 |
| `[data-track]` 直接子卡片 | `--card-focus`：0–1 |
| `[data-tilt]` | `--tilt-x`、`--tilt-y` |
| `[data-magnetic]` | `--magnet-x`、`--magnet-y` |

CSS 负责具体颜色与变换组合，`motion.js` 提供进度。装饰鼠标圈的位置由脚本直接更新。`app.js` 继续负责原有菜单、筛选、搜索、轮播按钮和询价草稿，不要重复绑定这些功能。

## 5. 参考站最新十二类服务

| slug | 服务 |
| --- | --- |
| building-maintenance | 建筑与日常维护 |
| roofing-waterproofing | 屋顶与防水 |
| electrical-lighting | 电气与照明 |
| plumbing-drainage-gas | 水管、排水与燃气 |
| hvac-building-systems | 空调与楼宇设备 |
| fire-security-access | 消防、安防与门禁 |
| landscaping-irrigation | 园林绿化与灌溉 |
| signage-wayfinding | 广告标识与导视 |
| facade-high-access-cleaning | 外立面与高空清洁 |
| cleaning-waste-hygiene | 清洁、垃圾与环境卫生 |
| car-parks-external-works | 停车场与室外工程 |
| fit-outs-make-good | 装修改造与退租恢复 |

该目录来自本次实际查看的墨尔本站，优先于历史会话中的旧分类。八类物业和六篇文章的具体条目继续以 `src/content.json` 为准。

## 6. 代码位置与构建顺序

| 文件 | 职责 |
| --- | --- |
| `DESIGN.md` | V2 设计方向与约束 |
| `src/content.json` | 双语业务内容 |
| `src/home_v2.py` | V2 首页结构，供 `build.py` 调用 |
| `build.py` | 共享导航、内页、元数据与所有静态路由生成 |
| `dist/style.css` | 保留的基础组件和响应式布局，不能单独代表 V2 |
| `dist/maximal.css` | V2 统一色值、全局样式、首页和共用动效 |
| `dist/interiors.css` | V2 服务、类型、新闻、FAQ、关于和联系等内页表现 |
| `dist/fonts.css` | 基础本地字体 |
| `dist/surf-font.css`、`dist/chinese-font.css` | Bowlby One SC 与 Noto Sans SC 本地字体声明 |
| `dist/app.js` | 基础交互与本地草稿 |
| `dist/motion.js` | V2 动效控制器 |
| `dist/assets/` | 本地图片、字体与图标 |
| `src/assets-sources.json`、`src/font-sources.json` | 素材及字体来源记录 |

CSS 按 `style.css → surf-font.css → chinese-font.css → maximal.css → interiors.css` 加载；脚本按 `app.js → motion.js` 顺序延迟加载。普通内容页保留 `body.maximal`，首页另有 `page-home` 类。不要删掉后加载的覆盖层而让旧版视觉重新出现。

执行 `python3 build.py` 生成全部 HTML；生成器不覆盖 CSS、JavaScript 和素材。修改页面结构应修改对应 Python 源文件，避免只改生成 HTML 而在下一次构建时丢失。

## 7. 内容依据与运营边界

已采用的公开资料：

- [COLORBOND 维护资料](https://colorbond.com/why-colorbond-steel/maintenance)：雨水难以冲洗部位与沿海盐雾环境的维护安排。
- [Gold Coast 恶劣天气资料](https://www.goldcoast.qld.gov.au/Services/Emergencies-disasters-outages/Get-Ready/Get-ready-Severe-weather)：春夏暴风雨与全年天气风险。
- [昆州共同物业维护说明](https://www.qld.gov.au/housing/body-corporate/maintenance/format-plan/building)：维护范围与分层计划、边界及设施有关。
- [Experience Gold Coast 访客经济介绍](https://corporate.experiencegoldcoast.com/what-we-do/visitor-economy)：住宿、场馆、活动与海岸等当地经营场景。

新闻选题和商业类型排序属于内容设计决定，不标成经过验证的搜索量排名。公司文案继续使用第一人称“我们”，直接说明处理范围、进场安排和交付。

黄金海岸联系电话、邮箱、营业安排、正式域名、真实询价接收端、具体覆盖边界以及当地团队和项目资料仍需确认。不要直接复制墨尔本城市联系方式，不编造案例、评价、资质、保险或固定到场时限。

当前表单只在本浏览器生成、复制和下载草稿；照片不上传，下载文本仅包含照片文件名。接通真实接收端并验证实际送达后，才能显示“已发送”。预览 `noindex` 和 `robots.txt` 禁抓状态继续保留，直至正式上线配置完成。

## 8. 验证记录与当前状态

### 已完成的 V2 静态检查

69 个 HTML 文件，即每种语言 34 个路由及一页 404；唯一 H1、预览 noindex、内部链接、图片与样式脚本资源、语言对应链接和页面锚点已检查通过。交互脚本和动效脚本在实施过程中已通过 JavaScript 语法检查。

### 保留的基础交互记录

V2 改版前，已操作验证桌面呈现、英中手机尺寸排版（390px 框架／375px 内容视口）、移动菜单打开与 Escape 关闭、服务分类、FAQ 检索展开、本地需求草稿生成。这些记录证明基础流程曾可用，**不能作为 V2 全部页面及动效已经通过浏览器验收的依据**。

### 已完成的代表性浏览器验证

**V2 已完成代表性桌面、移动与交互验证，实际观察记录见末节。** 这不代表覆盖了所有设备与操作系统；系统减少动态效果分支已实现，本轮浏览器实际操作验证了用户主动暂停。真实询价送达、正式域名和搜索引擎收录尚未配置或验证。

## 9. 直接交给 Codex 的继续开发 Prompt

```text
你是我们 Ellis Services Group 黄金海岸商业维护网站的前端开发、内容与本地 SEO 负责人。

先读取 DESIGN.md、README.md、CODEX_HANDOFF.md、build.py、src/home_v2.py、src/content.json、dist/maximal.css、dist/interiors.css、dist/motion.js、dist/app.js 和素材来源，再拉起当前项目预览。理解现有路由、基础交互和 V2 样式加载顺序后继续工作。

本轮视觉基线是 V2：澳洲冲浪海报 × 海滩俱乐部 × 热带夏日。用户已经拒绝 V1 的安静度假杂志风，并明确要求不能像 Melbourne 商业站。不要恢复浅色左右分栏首屏、衬线斜体杂志排版，也不要使用电光蓝/荧光绿的建筑科技系统。以 DESIGN.md 和 maximal.css 的最新决策为准，不因为 style.css 中留有旧值就恢复旧设计。

1. 保留首页、服务内容、商业类型、新闻、FAQ、关于我们、联系我们七项主导航；保留十二服务、八类物业、文章和双语路径关系。地区信息纳入现有页面，不增加第八个主导航。
2. 使用深棕墨 #241611、日落橙 #FF642D、珊瑚粉 #FF90BF、泳池青 #33E1D3、日光黄 #FFE34D 和阅读纸色 #FFF8E8。英文海报字使用本地 Bowlby One SC（CSS名 Surf Display），正文 DM Sans；中文单独处理尺寸与断行。纸色只服务阅读，不重新主导全站气质。
3. 保持 V2 全幅海岸、泳池、条纹伞与自然成年泳装游客的场景感；大海报字、硬描边、错位阴影、倾斜照片、海浪边界和交叉移动色带共同形成黄金海岸识别。服务、商业类型、新闻、FAQ、关于和联系内页都继续用 V2，不能只有首页更新。
4. 继续完善首屏视差、海浪推进、太阳/遮阳伞旋转、移动色带、照片焦点变化、卡片倾斜和磁吸反馈。宽度>=1024px的商业类型可采用普通纵向滚动驱动横向pin；移动端保留原生滑动和前后按钮。不拦截滚轮，不隐藏正常鼠标，不影响阅读和导航。不要重复绑定app.js已有功能。
5. 保留固定在角落的动效开关；用户暂停或系统减少动态效果时全部内容可见、自动效果停止、pin恢复正常流。验证开关、原生横向浏览和键盘操作。动效需要帮助展示内容；优先修复实际卡顿、遮挡或不可点击，不通过恢复V1弱化整个设计。
6. 内容保持第一人称“我们”，说清处理范围、材料与方法、进场、报价影响和完工交付。英语与中文详情页都可以直接打开和刷新。场景图不能标成我们的完工项目，资质、评价、保险、保证和到场时间只采用公司确认资料。
7. 读取已确认的黄金海岸资料后接入真实电话、邮箱、营业安排与询价接收端。当前表单仅生成本地草稿；接入后检查成功、失败和重复点击状态，实际送达后才显示已发送。不复制Melbourne收件地址或城市电话。
8. 在375/390、768和1440宽度检查英中首屏、导航、服务列表、商业类型、新闻正文、FAQ、联系表单、pin起止及动画暂停。检查H1、按钮和横向集合是否溢出或遮挡。V2代表性桌面、移动端及交互检查已完成，具体范围见末节最终验证记录；在此基础上检查本轮修改及尚未覆盖的视口，不把代表性检查表述为全部设备或所有页面均已验收。
9. 正式域名确定前保留预览noindex。正式上线配置单一canonical、对应hreflang、有效站点地图、真实404、统一斜杠规则和可抓取内链。结构化数据只反映实际页面与真实公司资料。
10. 修改源模板后重新生成HTML，再检查路由、资源、脚本语法和所改交互。最终给出预览地址、V2改动与效果、实际完成的验证、未验证项、仍缺的运营资料及部署状态。延续V2独立风格，避免重新套回V1或Melbourne视觉。
```


## V2 final verification / 最终验证

- 69 deliverable HTML pages; 1,970 internal links and 256 local source references resolved. All normal pages retain seven navigation items and 34 EN/ZH route pairs.
- Desktop browser: new full-bleed hero, poster service index, scroll-linked property collection (observed track advance to 786 px with sticky top at 82 px), Chinese FAQ layout, and no horizontal page overflow.
- Mobile browser: English and Chinese homepages, service and contact layouts at a 380 px content viewport; page width matched the viewport. Chinese hero title stayed within the frame after Noto Sans SC loaded.
- Mobile menu exposed all seven links and closed with Escape. Motion pause set motion-paused and stopped the sun animation. Service Systems filter showed 4 of 12 entries; Chinese FAQ search for 海盐 showed 1 of 10 entries.
- New Chinese font: local Noto Sans SC, 196,904 bytes, variable 100–900, 675 required characters verified. Font source manifest records the official source.
- Python generation, node --check for both JavaScript files, git diff --check, and frontend project strict audit passed (0 findings).
- Persistent corner motion control remains reachable while scrolling. Contact remains a browser-local draft, with no actual delivery.
