from datetime import datetime
import re


def extract_and_calculate_timestamp_diff(s):
    # 使用正则表达式匹配时间戳
    timestamps = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}', s)

    if len(timestamps) != 2:
        raise ValueError("字符串中必须恰好包含两个时间戳！")

        # 将字符串时间戳转换为datetime对象
    start_time = datetime.strptime(timestamps[0], '%Y-%m-%d %H:%M:%S.%f')
    end_time = datetime.strptime(timestamps[1], '%Y-%m-%d %H:%M:%S.%f')

    # 计算时间戳之间的差值
    time_diff = (end_time - start_time).total_seconds()

    return time_diff


# 测试函数
s = "2024-01-12 16:02:30.021 <<<set t:2024-01-12 16:02:29.728,nodeLocation:localhost:4322 = {...}"
print(extract_and_calculate_timestamp_diff(s))