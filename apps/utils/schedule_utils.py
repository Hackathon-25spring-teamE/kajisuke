from datetime import datetime, date
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY, YEARLY, MO, TU, WE, TH, FR, SA, SU


# 一覧に表示する繰り返し予定を作成
def get_frequency_or_date(schedule_obj, today):
    frequency_or_date = ""

    if schedule_obj.frequency == "NONE":
        # 日付が今日よりも前なら、一覧に表示しない(Noneを返す)
        if schedule_obj.start_date < today:
            return None
        # 繰り返し設定なしのため、start_dateを表示
        else:
            frequency_or_date = f"{schedule_obj.start_date.year}年{schedule_obj.start_date.month}月{schedule_obj.start_date.day}日"
    
    else:
        if schedule_obj.frequency == "DAILY":
            if schedule_obj.interval == 1:
                interval = "毎日"
            else:
                interval = f"{schedule_obj.interval}日毎"
            rule = ""

        elif schedule_obj.frequency == "WEEKLY":
            if schedule_obj.interval == 1:
                interval = "毎週"
            else:
                interval = f"{schedule_obj.interval}週間毎"
            rule = jp_weekday_dict.get(schedule_obj.day_of_week)

        elif schedule_obj.frequency == "MONTHLY":
            if schedule_obj.interval == 1:
                interval = "毎月"
            else:
                interval = f"{schedule_obj.interval}ヶ月毎"
            if schedule_obj.nth_weekday and schedule_obj.day_of_week:
                rule = f"第{schedule_obj.nth_weekday}{jp_weekday_dict.get(schedule_obj.day_of_week)}"
            else:
                rule = f"{schedule_obj.start_date.day}日"

        elif schedule_obj.frequency == "YEARLY":
            if schedule_obj.interval == 1:
                interval = "毎年"
            else:
                interval = f"{schedule_obj.interval}年毎"
            if schedule_obj.nth_weekday and schedule_obj.day_of_week:
                rule = f"{schedule_obj.start_date.month}月第{schedule_obj.nth_weekday}{jp_weekday_dict.get(schedule_obj.day_of_week)}"
            else:
                rule = f"{schedule_obj.start_date.month}月{schedule_obj.start_date.day}日" 
        else:
            interval, rule = ""

        frequency_or_date = f"{interval} {rule}"

    return frequency_or_date


# 曜日を英語文字列から日本語の曜日に変換するための辞書
jp_weekday_dict = { "MO": "月曜日", "TU": "火曜日", "WE": "水曜日", "TH": "木曜日", "FI": "金曜日", "SA": "土曜日", "SU": "日曜日" }



# DBクエリで取得したscheduleから、今日以降で直近の繰り返し日付(date型)を生成
def get_most_recent_reccurenced_date(schedule_obj, today):
    # frequencyがNONEの時→todayを返す
    if schedule_obj.frequency == "NONE":
        return today
    
    # frequencyがNONE以外の時→繰り返し設定から直近の日付を生成
    reccurences = {
        "freq": frequency_dict.get(schedule_obj.frequency), 
        "interval": schedule_obj.interval, 
        "dtstart": schedule_obj.start_date,
        "bymonth": schedule_obj.start_date.month if schedule_obj.frequency == "YEARLY" else None,
        "byweekday": weekday_dict.get(schedule_obj.day_of_week),
        "bysetpos": schedule_obj.nth_weekday,
    }
    # reccurencesからNoneの項目を除外する
    filted_reccurences = { k: v for k, v in reccurences.items() if v is not None }
    # 上記を使って今日以降で直近の繰り返し日付を作成
    recent_date = rrule(**filted_reccurences).after(datetime.combine(today, datetime.min.time()), inc=True)

    return recent_date.date()


# frequency を文字列からdateutil.rruleの定数に変換するための辞書
frequency_dict = { "DAILY": DAILY, "WEEKLY": WEEKLY, "MONTHLY": MONTHLY, "YEARLY": YEARLY }

# 曜日を文字列からdateutil.rruleの曜日オブジェクトに変換するための辞書
weekday_dict = { "MO": MO,"TU": TU,"WE": WE,"TH": TH,"FI": FR,"SA": SA,"SU": SU }
