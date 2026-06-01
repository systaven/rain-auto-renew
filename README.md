# 雨云自动签到 & 积分续期

通过 GitHub Actions 每天自动完成雨云签到与积分续期，无需任何服务器。

---

## 功能

- ✅ 每天自动签到，领取全部可用任务积分
- 🔄 自动检测到期时间，积分不足时自动续费
- 🔐 密钥存放在 GitHub Secrets，不会泄露
- 📋 支持多账号、多实例

---

## 快速开始

### 第一步：Fork 或克隆仓库

点击右上角 **Fork**，或：

```bash
git clone https://github.com/你的用户名/rainyun-auto.git
```

### 第二步：获取 API 密钥

1. 打开 [雨云账户设置](https://app.rainyun.com/account/settings)
2. 点击左侧【API 秘钥】→【重新生成】
3. 复制密钥字符串

### 第三步：配置 GitHub Secrets

在仓库页面进入 **Settings → Secrets and variables → Actions → New repository secret**，添加以下两个 Secret：

#### `RAINYUN_API_KEYS`（签到用）

单账号：
```
你的API密钥
```

多账号（英文逗号分隔）：
```
密钥1,密钥2,密钥3
```

#### `RAINYUN_INSTANCES`（续期用，可选）

格式：`API密钥:产品ID:触发阈值天数:每次续费天数`

单实例：
```
你的API密钥:产品ID:7:7
```

多实例（英文分号分隔）：
```
密钥1:产品ID1:7:7;密钥2:产品ID2:10:7
```

> **产品 ID 在哪里找？**  
> 登录雨云控制台，打开你的游戏云实例，URL 中的那串数字即为产品 ID。  
> 例如：`https://app.rainyun.com/apps/rgs/12345/...` → 产品 ID 为 `12345`

### 第四步：启用 Actions

进入仓库的 **Actions** 页面，点击 **Enable GitHub Actions**。

之后会在每天北京时间 **09:00 签到**、**10:00 续期**，自动执行。

---

## 手动触发

在 Actions 页面 → 左侧选择 **雨云自动签到 & 续期** → 右侧点击 **Run workflow**，可选择执行：
- `both`：签到 + 续期（默认）
- `signin`：仅签到
- `renew`：仅续期

---

## 积分收益参考

| 项目 | 数值 |
|------|------|
| 每日签到积分 | ~300 积分 |
| 每月累计积分 | ~9,000 积分 |
| 积分兑换比例 | 400 积分 = 1 元 |
| 每月等值金额 | **22.5 元** |

---

## 注意事项

- **不要**把 API 密钥直接写进代码后上传，始终用 Secrets 存储
- 如果长时间没有 Actions 活动，GitHub 可能暂停定时任务，手动触发一次即可恢复
- 积分余额不足时续费会失败，注意查看 Actions 运行日志

---

## 文件结构

```
.
├── .github/
│   └── workflows/
│       └── auto_tasks.yml   # GitHub Actions 定时任务
├── scripts/
│   ├── signin.py            # 自动签到脚本
│   └── renew.py             # 自动积分续期脚本
├── .gitignore
└── README.md
```

---

## License

MIT
