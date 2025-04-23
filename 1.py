import requests, json, os, pytz, smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SIGNIN_URL = "https://glados.rocks/api/user/checkin"
STATUS_URL = "https://glados.rocks/api/user/status"

# 读取 cookie
cookies = os.environ.get("GLADOS_COOKIE", "").split("&")
if cookies[0] == "":
    print('未获取到COOKIE变量') 
    cookies = []
    exit(0)
else:
    cookies = cookies[0]

HEADERS = {
    'cookie': cookies,
    'user-agent': 'Mozilla/5.0',
    'referer': 'https://glados.rocks/console/checkin',
    'origin': 'https://glados.rocks',
    'content-type': 'application/json;charset=UTF-8',
}

# 发送邮件函数
def send_email(subject, content, to_email):
    from_email = os.environ.get("EMAIL_USER")
    email_pass = os.environ.get("EMAIL_PASS")

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(content, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)  # Gmail SMTP
        server.login(from_email, email_pass)
        server.send_message(msg)
        server.quit()
        print("邮件发送成功")
    except Exception as e:
        print("邮件发送失败：", str(e))


def check_in():
    result_log = []
    payload = {"token": "glados.one"}

    try:
        res = requests.post(SIGNIN_URL, headers=HEADERS, json=payload)
        res_json = res.json()

        status = requests.get(STATUS_URL, headers=HEADERS).json()
        balance = '?'
        email = '未知'
        left_days = '?'

        if status.get('code') == 0:
            data = status['data']
            email = data.get("email", "未知")
            left_days = data.get("leftDays", "未知")

        reward_time_str = "未知时间"
        if 'list' in res_json and len(res_json['list']) > 0:
            latest_reward = res_json['list'][0]
            asset = latest_reward.get('asset', '未知')
            change = latest_reward.get('change', '?')
            balance = latest_reward.get('balance', '?')

            timestamp = latest_reward.get('time')
            tz = pytz.timezone("Asia/Shanghai")
            if timestamp:
                reward_time = datetime.fromtimestamp(timestamp / 1000, tz)
                reward_time_str = reward_time.strftime("%Y-%m-%d %H:%M:%S")

            result_log.append(f"签到时间：{reward_time_str}")
            result_log.append(f"签到状态：{'签到成功' if res_json.get('code') == 0 else '今日已签到'}")
            result_log.append(f"今日奖励明细：{asset} +{change}，余额：{balance}")
        else:
            result_log.append("今日已签到（无奖励记录）")

        result_log.append("\n账户信息：")
        result_log.append(f"邮箱：{email}")
        result_log.append(f"当前总积分：{balance}")
        result_log.append(f"剩余服务天数：{int(float(left_days))} 天")

        # 拼接日志内容并发送邮件
        result_str = '\n'.join(result_log)
        send_email(subject="GLaDOS 签到报告", content=result_str, to_email=email)

    except Exception as e:
        print("请求出错：", str(e))


if __name__ == "__main__":
    check_in()
