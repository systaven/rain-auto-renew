"""
雨云自动积分续期脚本
从环境变量 RAINYUN_INSTANCES 读取配置
格式（多个实例用分号分隔）：API_KEY:产品ID:续费阈值天数:每次续费天数
示例：abc123:12345:7:7;xyz789:67890:10:7
"""

import requests
import time
import os
import sys
import datetime

INSTANCES_ENV = os.environ.get("RAINYUN_INSTANCES", "")

instances = []
for entry in INSTANCES_ENV.split(";"):
    entry = entry.strip()
    if not entry:
        continue
    parts = entry.split(":")
    if len(parts) < 2:
        print(f"⚠️  格式有误，跳过: {entry}")
        continue
    api_key      = parts[0].strip()
    product_id   = parts[1].strip()
    threshold    = int(parts[2].strip()) if len(parts) > 2 else 7   # 剩余天数 ≤ 此值时触发续费
    duration_day = int(parts[3].strip()) if len(parts) > 3 else 7   # 每次续费天数

    instances.append({
        "key":          api_key,
        "pid":          product_id,
        "threshold":    threshold,
        "duration_day": duration_day,
    })

if not instances:
    print("❌ 未找到实例配置，请在 GitHub Secrets 中设置 RAINYUN_INSTANCES")
    sys.exit(1)

URL_INFO  = "https://api.v2.rainyun.com/product/rgs/{id}/"
URL_RENEW = "https://api.v2.rainyun.com/product/point_renew"


def remaining_days(unix_timestamp: int) -> int:
    exp = datetime.datetime.fromtimestamp(unix_timestamp)
    now = datetime.datetime.now()
    return (exp - now).days


print("=" * 50)
print("🔄 雨云自动积分续期")
print(f"🕐 当前时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📋 共 {len(instances)} 个实例")
print("=" * 50)

success_count = 0
skip_count    = 0
fail_count    = 0

for idx, inst in enumerate(instances, 1):
    key          = inst["key"]
    pid          = inst["pid"]
    threshold    = inst["threshold"]
    duration_day = inst["duration_day"]
    masked_key   = key[:6] + "***" + key[-4:]

    print(f"\n[{idx}/{len(instances)}] 账号: {masked_key}  产品ID: {pid}")

    headers = {
        "x-api-key":    key,
        "User-Agent":   "Rainyun-AutoRenew/1.0",
        "Content-Type": "application/json",
    }

    # 获取产品信息
    try:
        resp = requests.get(URL_INFO.replace("{id}", pid), headers=headers, timeout=15)
        resp.raise_for_status()
        result = resp.json()
    except Exception as e:
        print(f"  ❌ 获取产品信息失败: {e}")
        fail_count += 1
        continue

    try:
        exp_timestamp = result["data"]["Data"]["ExpDate"]
    except (KeyError, TypeError):
        print(f"  ❌ 解析到期时间失败，响应: {result}")
        fail_count += 1
        continue

    days_left = remaining_days(exp_timestamp)
    exp_str   = datetime.datetime.fromtimestamp(exp_timestamp).strftime("%Y-%m-%d %H:%M")
    print(f"  📅 到期时间: {exp_str}  剩余: {days_left} 天  (阈值: {threshold} 天)")

    if days_left > threshold:
        print(f"  ✅ 剩余天数充足，无需续费")
        skip_count += 1
        continue

    # 发起续费
    print(f"  💳 剩余天数不足，续费 {duration_day} 天...")
    payload = {
        "duration_day": duration_day,
        "product_id":   int(pid),
        "product_type": "rgs",
    }
    try:
        r = requests.post(URL_RENEW, headers=headers, json=payload, timeout=15)
        r.raise_for_status()
        res = r.json()
        if res.get("code") == 200:
            print(f"  🎉 续费成功！续期 {duration_day} 天")
            success_count += 1
        else:
            print(f"  ⚠️  续费返回异常: {res}")
            fail_count += 1
    except Exception as e:
        print(f"  ❌ 续费请求异常: {e}")
        fail_count += 1

print("\n" + "=" * 50)
print(f"🎉 续费成功: {success_count}  |  ✅ 无需续费: {skip_count}  |  ❌ 失败: {fail_count}")
print("=" * 50)

if fail_count > 0:
    sys.exit(1)
