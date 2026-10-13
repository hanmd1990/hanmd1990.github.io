# 图片与网站维护

本站是独立静态网站，不再加载“上线了”的脚本、API、图片或字体。布局样式已保存在 static/styles，交互代码为 static/site.js。

## 图片分类
- images/brand：网站标识与分享图
- images/people：成员、韩梦迪老师和课题组活动
- images/research：各研究方向
- images/publications：论文插图和期刊封面
- images/news：按年份归档的新闻图片
- images/lab-tour：实验室与设备
- images/home：首页图
- images/pages：其他页面

同一图片在多个页面使用时只保留一个路径。images/catalog.csv 和 catalog.json 列出图片路径、说明和使用页面；打开 /images/ 可浏览缩略图并搜索。

## 替换图片
1. 在图片目录找到目标图片，打开仓库内相应文件。
2. 上传新图片覆盖同一路径，保留文件名、扩展名，建议维持相同宽高比。GIF 应保留为 GIF，避免丢失动画。
3. 提交到 main。GitHub Actions 会验证并自动发布，完成后刷新网页（必要时强制刷新）。
4. 若增加或重命名图片，更新对应栏目 index.html 中的 src 和相关背景 URL，并同步图片目录记录。

内容直接在各栏目 index.html 中编辑。首页为 index.html，2026 新闻为 news2026/index.html，2026 论文为 publications2026/index.html。外部论文链接仍指向出版商；点击外链与页面自身加载依赖是两回事。

原域名与阿里云 DNS 未变更。历史迁移记录仍可通过 Git 历史恢复；当前发布不再执行抓取。

## 年份导航和 Full List 自动维护

顶部 Publications 和 News 直接打开当年的页面；如果当年页面尚未创建，则打开最近的已有年份。页面第一行自动列出已存在的年份，并高亮当前年份；Full List 与 Covers 为突出显示的入口。

论文内容只编辑 publicationsYYYY/index.html；News 内容只编辑 newsYYYY/index.html。GitHub Actions 发布时运行 tools/build_site.py，从各年份论文页生成 /all/，从各年份新闻页生成 /news-all/，并更新所有年份链接。不要单独维护 Full List，生成结果会覆盖旧版本。

新增年份时创建 publicationsYYYY/index.html 或 newsYYYY/index.html，保留相应类型页面结构即可；导航会自动发现新目录。论文条目延续现有的 (数字) 编号，编号在所有年份中应保持唯一，以避免重复收录。
