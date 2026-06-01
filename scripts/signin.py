"""
雨云自动签到脚本
从环境变量 RAINYUN_API_KEYS 读取密钥（多个用英文逗号分隔）
"""

import requests
import time
import os
import sys

API_KEYS_ENV = os.environ.get("RAINYUN_API_KEYS", "")
api_keys = [k.strip() for k in API_KEYS_ENV.split(",") if k.strip()]

if not api_keys:
    print("❌ 未找到 API 密钥，请在 GitHub Secrets 中设置 RAINYUN_API_KEYS")
    sys.exit(1)

URL = "https://api.v2.rainyun.com/user/reward/tasks"

print("=" * 50)
print("🚀 雨云自动签到")
print(f"🕐 当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📋 共 {len(api_keys)} 个账号")
print("=" * 50)

total_points = 0
success_count = 0
fail_count = 0

for idx, key in enumerate(api_keys, 1):
    masked_key = key[:6] + "***" + key[-4:]
    print(f"\n[{idx}/{len(api_keys)}] 账号: {masked_key}")

    headers = {
        "x-api-key": key,
        "User-Agent": "Rainyun-AutoSignin/2.0",
        "Content-Type": "application/json",
    }

    # 获取任务列表
    try:
        resp = requests.get(URL, headers=headers, timeout=15)
        resp.raise_for_status()
        result = resp.json()
    except Exception as e:
        print(f"  ❌ 获取任务列表失败: {e}")
        fail_count += 1
        continue

    if result.get("code") != 200:
        print(f"  ❌ API 返回异常: {result}")
        fail_count += 1
        continue

    tasks = result.get("data", [])
    claimable = [t for t in tasks if t.get("Status") == 1]
    done      = [t for t in tasks if t.get("Status") == 2]
    pending   = [t for t in tasks if t.get("Status") == 0]

    print(f"  ✅ 已完成: {len(done)} 个  |  ⏳ 可领取: {len(claimable)} 个  |  🔒 未完成: {len(pending)} 个")

    if not claimable:
        print("  ℹ️  没有可领取的任务")
        success_count += 1
        continue

    account_points = 0
    for task in claimable:
        task_name   = task.get("Name", "未知任务")
        task_points = task.get("Points", 0)
        try:
            r = requests.post(URL, headers=headers, json={"task_name": task_name}, timeout=15)
            r.raise_for_status()
            res = r.json()
            if res.get("code") == 200:
                account_points += task_points
                print(f"  🎁 领取「{task_name}」成功 +{task_points} 积分")
            else:
                print(f"  ⚠️  领取「{task_name}」失败: {res}")
        except Exception as e:
            print(f"  ❌ 领取「{task_name}」异常: {e}")

    total_points += account_points
    success_count += 1
    print(f"  💰 本账号本次领取: {account_points} 积分")

print("\n" + "=" * 50)
print(f"✅ 成功: {success_count} 个账号  |  ❌ 失败: {fail_count} 个账号")
print(f"💰 本次总计领取: {total_points} 积分")
print("=" * 50)

if fail_count > 0:
    sys.exit(1)
