console.log("schedule_form.js 読み込み成功！");
// Ajaxでカテゴリーに応じたタスクを表示処理 
$("#id_task_category").change(function () {
    const url = "/ajax/load-tasks/";
    const categoryId = $(this).val();

    $.ajax({
        url: url,
        data: {
            'task_category': categoryId
        },
        success: function (data) {
            const $taskSelect = $("#id_task");
            $taskSelect.empty();
            $.each(data, function (index, task) {
                $taskSelect.append(`<option value="${task.id}">${task.task_name}</option>`);
            });
        }
    });
});


$(document).ready(function () {
    // 初期は全フィールド非表示
    $("#interval-field, #day-of-week-field, #nth-weekday-field").hide();

    // 曜日コードマップ（日曜=0〜土曜=6 → Djangoの曜日コード）
    const jsDayToDjangoCode = ["SU", "MO", "TU", "WE", "TH", "FI", "SA"];

    // 指定曜日だけ表示しチェック。その他非表示
    function showOnlySelectedWeekday(selectedDay) {
        $(".day-label").each(function () {
            if ($(this).data("day") === selectedDay) {
                $(this).show();
                $(this).find("input[type=radio]").prop("checked", true);
            } else {
                $(this).hide();
                $(this).find("input[type=radio]").prop("checked", false);
            }
        });
    }

    // 開始日から曜日セット(毎週選択時使用)
    function setDayOfWeekFromStartDate() {
        const startDateStr = $("#id_start_date").val();
        if (!startDateStr) return;

        const dateObj = new Date(startDateStr);
        if (isNaN(dateObj)) return;

        const jsDay = dateObj.getDay();
        const djangoDay = jsDayToDjangoCode[jsDay];

        if ($("#id_frequency").val() === "WEEKLY") {
            showOnlySelectedWeekday(djangoDay);
        } else {
            // 週以外は全部表示してチェックなし
            $(".day-label").show();
            $("input[name='day_of_week']").prop("checked", false);
        }
    }

    // 第何週何曜日取得の関数(毎月選択時に使用)
    function getOrdinalWeekdayInfo(dateObj) {
        const jsDay = dateObj.getDay(); // 0〜6
        const jsDayToDjangoCode = ["SU", "MO", "TU", "WE", "TH", "FI", "SA"];
        const djangoDay = jsDayToDjangoCode[jsDay];

        const nth = Math.floor((dateObj.getDate() - 1) / 7);
        const weekNames = ["第1", "第2", "第3", "第4", "第5"];
        const dayNames = ["日", "月", "火", "水", "木", "金", "土"];

        return {
            nth,
            djangoDay,
            label: `${weekNames[nth]}${dayNames[jsDay]}曜日`
        };
    }
    // MonthlyOptions選択時（毎月選択時に使用）
    function updateMonthlyOptionsFromStartDate() {
        const dateStr = $("#id_start_date").val();
        if (!dateStr) return;

        const dateObj = new Date(dateStr);
        if (isNaN(dateObj)) return;

        const y = dateObj.getFullYear(), m = dateObj.getMonth() + 1, d = dateObj.getDate();
        $("#monthly-date-info").text(`${d}日`);

        const info = getOrdinalWeekdayInfo(dateObj);
        $("#monthly-weekday-info").text(`${info.label}`);

        // デフォルトでフォームに値をセット（初期表示）
        $("#id_nth_weekday").val(info.nth + 1);
        $("input[name='day_of_week']").prop("checked", false);
        $(`input[name='day_of_week'][value='${info.djangoDay}']`).prop("checked", true);
    }
    // YearlyOptions選択時（毎年選択時に使用）
    function updateYearlyOptionsFromStartDate() {
        const dateStr = $("#id_start_date").val();
        if (!dateStr) return;

        const dateObj = new Date(dateStr);
        if (isNaN(dateObj)) return;

        const y = dateObj.getFullYear(), m = dateObj.getMonth() + 1, d = dateObj.getDate();
        $("#yearly-date-info").text(`${m}月${d}日`);

        const jsDay = dateObj.getDay(); // 0〜6
        const jsDayToDjangoCode = ["SU", "MO", "TU", "WE", "TH", "FI", "SA"];
        const djangoDay = jsDayToDjangoCode[jsDay];
        const nth = Math.floor((dateObj.getDate() - 1) / 7);
        const weekNames = ["第1", "第2", "第3", "第4", "第5"];
        const dayNames = ["日", "月", "火", "水", "木", "金", "土"];

        $("#yearly-weekday-info").text(`${m}月${weekNames[nth]}${dayNames[jsDay]}曜日`);

        $("#id_nth_weekday").val(nth + 1);
        $("input[name='day_of_week']").prop("checked", false);
        $(`input[name='day_of_week'][value='${djangoDay}']`).prop("checked", true);
    }

    // MONTHLYオプション切替
    $("input[name='monthly_option']").change(function () {
        const option = $(this).val();

        if (option === "by_weekday") {
            $("#monthly-nth-weekday-selects").hide();
            // 選択された曜日を保持（すでに updatemonthlyOptionsFromStartDate() でセット済み）
        } else if (option === "by_date") {
            $("#monthly-nth-weekday-selects").hide();
            //  by_date 選択時は day_of_week を空にする
            $("#id_day_of_week").val("");
        }
    });

    // YEARLYオプション切替
    $("input[name='yearly_option']").change(function () {
        const option = $(this).val();

        if (option === "by_weekday") {
            $("#yearly-nth-weekday-selects").hide();
            // 選択された曜日を保持（すでに updateYearlyOptionsFromStartDate() でセット済み）
        } else if (option === "by_date") {
            $("#yearly-nth-weekday-selects").hide();
            //  by_date 選択時は day_of_week を空にする
            $("#id_day_of_week").val("");
        }
    });


    // frequencyボタンクリック
    $("#frequency-buttons button").click(function () {
        const value = $(this).data("value");
        $("#id_frequency").val(value);

        $("#frequency-buttons button").removeClass("selected");
        $(this).addClass("selected");

        //  interval の初期値を1にセット（NONE以外の時）
        if (value !== "NONE") {
            $("#id_interval").val(1);
        } else {
            $("#id_interval").val("");  // NONE の時は空にする
        }

        $("#interval-field, #day-of-week-field, #nth-weekday-field").hide();
        $(".monthly-options, .yearly-options").hide();
        $(".field-help").text("");
        $(".day-label").show();
        $("input[name='day_of_week']").prop("checked", false);

        if (value === "DAILY") {
            $("#interval-field").show();
            $("#interval-help").text("日ごと");
        } else if (value === "WEEKLY") {
            $("#interval-field, #day-of-week-field").show();
            $("#interval-help").text("週間ごと");
            $("#day-of-week-help").text("");
            setDayOfWeekFromStartDate();
        } else if (value === "MONTHLY") {
            $("#interval-field, #nth-weekday-field").show();
            $(".monthly-options").show();
            $("#interval-help").text("か月ごと");
            $("input[name='monthly_day_of_week']").prop("checked", true).hide();
            updateMonthlyOptionsFromStartDate();
            $("input[name='monthly_option'][value='by_date']").prop("checked", true);
            $("#monthly-nth-weekday-selects").hide();
        } else if (value === "YEARLY") {
            $("#interval-field, #nth-weekday-field").show();
            $("#interval-help").text("年ごと");
            $(".yearly-options").show();
            $("input[name='yearly_day_of_week']").prop("checked", true);
            updateYearlyOptionsFromStartDate();
        } else if (value === "NONE") {
            $("#interval-field, #day-of-week-field, #nth-weekday-field").hide();
        }
    });

    // 開始日変更時
    $("#id_start_date").change(function () {
        const freq = $("#id_frequency").val();
        if (freq === "WEEKLY") {
            $("#frequency-buttons button[data-value='WEEKLY']").addClass("selected");
            $("#interval-field, #day-of-week-field").show();
            setDayOfWeekFromStartDate();
        } else if (freq === "MONTHLY") {
            $("#frequency-buttons button[data-value='MONTHLY']").addClass("selected");
            $("#interval-field, #nth-weekday-field").show();
            $(".monthly-options").show();
            updateMonthlyOptionsFromStartDate();
            if ($("input[name='monthly_option']:checked").val() === "by_weekday") {
                $("#monthly-nth-weekday-selects").show();
            }
        } else if (freq === "YEARLY") {
            $("#frequency-buttons button[data-value='YEARLY']").addClass("selected");
            $("#interval-field, #nth-weekday-field").show();
            $(".yearly-options").show();
            updateYearlyOptionsFromStartDate();
        }
    });

    // 初期表示時に frequency による設定を反映
    const initialFreq = $("#id_frequency").val();
    if (initialFreq) {
        $(`#frequency-buttons button[data-value='${initialFreq}']`).trigger('click');
    }
});