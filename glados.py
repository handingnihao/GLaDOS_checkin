import requests
from datetime import datetime

SIGNIN_URL = "https://glados.rocks/api/user/checkin"
STATUS_URL = "https://glados.rocks/api/user/status"

# 替换为你的 Cookie（不要加 cookie:）
COOKIE = os.environ.get("GLADOS_COOKIE", []).split("&")

HEADERS = {
    'cookie': COOKIE,
    'user-agent': 'Mozilla/5.0',
    'referer': 'https://glados.rocks/console/checkin',
    'origin': 'https://glados.rocks',
    'content-type': 'application/json;charset=UTF-8',
}

def check_in():
    payload = {"token": "glados.one"}

    try:
        res = requests.post(SIGNIN_URL, headers=HEADERS, json=payload)
        res_json = res.json()

        # 获取账户状态
        status = requests.get(STATUS_URL, headers=HEADERS).json()
        balance = '?'
        email = '未知'
        left_days = '?'

        if status.get('code') == 0:
            data = status['data']
            email = data.get("email", "未知")
            left_days = data.get("leftDays", "未知")

        # ��� 签到奖励明细处理（包含时间戳）
        reward_time_str = "未知时间"
        if 'list' in res_json and len(res_json['list']) > 0:
            latest_reward = res_json['list'][0]
            asset = latest_reward.get('asset', '未知')
            change = latest_reward.get('change', '?')
            balance = latest_reward.get('balance', '?')

            # 转换时间戳（毫秒转秒）
            timestamp = latest_reward.get('time')
            if timestamp:
                reward_time = datetime.fromtimestamp(timestamp / 1000)
                reward_time_str = reward_time.strftime("%Y-%m-%d %H:%M:%S")

            print(f"��� 签到时间：{reward_time_str}")
            print(f"✅ 签到状态：{'签到成功' if res_json.get('code') == 0 else '今日已签到'}")
            print("��� 今日奖励明细：")
            print(f"  - ��� {asset} 变动：+{change}，余额：{balance}")
        else:
            print("��� 今日已签到（无奖励记录）")

        # ��� 输出账户信息
        print("\n��� 账户信息：")
        print(f"  - 邮箱：{email}")
        print(f"  - 当前总积分：{balance}")
        print(f"  - 剩余服务天数：{int(float(left_days))} 天")

    except Exception as e:
        print("��� 请求出错：", str(e))

if __name__ == "__main__":
    check_in()

