from datetime import datetime, date
import jpholiday
from dateutil.rrule import rruleset, rrule, DAILY, WEEKLY, MONTHLY, YEARLY, MO, TU, WE, TH, FR, SA, SU


# 日付から和暦を算出する
def wareki(date_obj):
    if date_obj.year >= 2019:
        era = "令和"
        year = date_obj.year - 2018
    elif date_obj.year >= 1989:
        era = "平成"
        year = date_obj.year - 1988
    elif date_obj.year >= 1926:
        era = "昭和"
        year = date_obj.year - 1925
    elif date_obj.year >= 1912:
        era = "大正"
        year = date_obj.year - 1911
    elif date_obj.year >= 1868:
        era = "明治"
        year = date_obj.year - 1867
    else:
        return f"{date_obj.year}年"  # 和暦対象外

    year_str = "元" if year == 1 else str(year)
    return f"{era}{year_str}年"


# 祝日リスト作成
def get_japanese_holidays(year, month):
    holidays = []
    for day in range(1, 32):
        try:
            d = date(year, month, day)
            if jpholiday.is_holiday(d):
                holidays.append(d.strftime('%Y-%m-%d'))
        except ValueError:
            continue
    return holidays



# DBクエリで取得したscheduleとexceptional_schedulesから、対象期間（datetime型）の日付リスト（date型）を生成
def get_reccureced_dates(schedule_obj, except_obj, start_date, end_date):
    date_list = []
    # frequencyがNONEの時→schedule_obj.start_dateがstart_dateとend_dateの間であれば日付リストに追加
    if schedule_obj.frequency == "NONE":
        if start_date.date() <= schedule_obj.start_date <= end_date.date():
            date_list.append(schedule_obj.start_date)
    # frequencyがNONE以外の時→繰り返し設定から日付リストを作成する
    else:
        date_set = rruleset()
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
        # 上記を使って対象期間の日付リストを作成
        date_set.rrule(
            rrule(**filted_reccurences)
            .between(start_date, end_date, inc=True)
            )

        # 2-3. 日付リストに対し、original_dateを除外し、modified_dateを追加する
        for except_item in except_obj:
            if except_item.schedule.id == schedule_obj.id:
                # 繰り返しからoriginal_dateを除外
                original_date = datetime.combine(except_item.original_date, datetime.min.time())
                date_set.exdate(original_date)
                # modified_dateがNoneではなく、対象期間内なら追加
                if except_item.modified_date is not None:
                    if start_date.date() <= except_item.modified_date <= end_date.date():
                        modified_date = datetime.combine(except_item.modified_date, datetime.min.time())
                        date_set.rdate(modified_date)

        # datetimeをdateに変換
        date_list = [dt.date() for dt in date_set]

    return date_list


# frequency を文字列からdateutil.rruleの定数に変換するための辞書
frequency_dict = { "DAILY": DAILY, "WEEKLY": WEEKLY, "MONTHLY": MONTHLY, "YEARLY": YEARLY }

# 曜日を文字列からdateutil.rruleの曜日オブジェクトに変換するための辞書
weekday_dict = { "MO": MO,"TU": TU,"WE": WE,"TH": TH,"FI": FR,"SA": SA,"SU": SU }