console.log("schedule_edit.js 読み込み成功！");


$(document).ready(function () {
    console.log("Before JS:", $("#id_nth_weekday").val());

    setTimeout(() => {
        console.log("After updateYearlyOptionsFromStartDate:", $("#id_nth_weekday").val());
    }, 1000);
    initScheduleForm();
});

function initScheduleForm() {
    $("#interval-field, #day-of-week-field, #nth-weekday-field").hide();
    updateStartDateWeekday();
    initFrequencyButtonSelection();
    bindFrequencyButtons();
    bindStartDateChange();
    bindMonthlyOptionChange();
    bindYearlyOptionChange();
    triggerInitialFrequency();
    // setInitialFrequencyState();
    updateMonthlyAndYearlyOptionRadios();
}

// --- 初期表示関連 ---
function initFrequencyButtonSelection() {
    const frequency = $("#id_frequency").val();
    if (!frequency) return;
    $(".frequency-buttons").removeClass("active");
    $(`.frequency-buttons[data-value="${frequency}"]`).addClass("active");
}

function triggerInitialFrequency() {
    const initialFreq = $("#id_frequency").val();
    if (!initialFreq) return;

    // クリックイベント発火
    $(`#frequency-buttons button[data-value='${initialFreq}']`).trigger("click");

    // クリックイベントの中で interval は初期値1にリセットされてしまうので、
    // ここでフォームにある interval の値を再セットする
    const initialInterval = $("#id_interval").data("initial-value");
    if (initialInterval) {
        $("#id_interval").val(initialInterval);
    }
}

// --- 曜日表示更新 ---
function updateStartDateWeekday() {
    const dateStr = $("#id_start_date").val();
    if (!dateStr) return $("#start-date-weekday").text("");

    const dateObj = new Date(dateStr);
    if (isNaN(dateObj)) return $("#start-date-weekday").text("");

    const dayNames = ["日", "月", "火", "水", "木", "金", "土"];
    $("#start-date-weekday").text(`(${dayNames[dateObj.getDay()]})`);
}

// --- 曜日関連処理 ---
function showOnlySelectedWeekday(selectedDay) {
    $(".day-label").each(function () {
        const $input = $(this).find("input[type=radio]");
        if ($(this).data("day") === selectedDay) {
            $(this).show();
            $input.prop("checked", true);
        } else {
            $(this).hide();
            $input.prop("checked", false);
        }
    });
}

function setDayOfWeekFromStartDate() {
    const dateStr = $("#id_start_date").val();
    if (!dateStr) return;

    const dateObj = new Date(dateStr);
    if (isNaN(dateObj)) return;

    const jsDayToDjangoCode = ["SU", "MO", "TU", "WE", "TH", "FI", "SA"];
    const djangoDay = jsDayToDjangoCode[dateObj.getDay()];

    if ($("#id_frequency").val() === "WEEKLY") {
        showOnlySelectedWeekday(djangoDay);
    } else {
        $(".day-label").show();
        $("input[name='day_of_week']").prop("checked", false);
    }
}

// --- 毎月繰り返し関連 ---
function updateMonthlyOptionsFromStartDate() {
    const dateStr = $("#id_start_date").val();
    if (!dateStr) return;

    const dateObj = new Date(dateStr);
    if (isNaN(dateObj)) return;

    const d = dateObj.getDate();
    $("#monthly-date-info").text(`${d}日`);

    const info = getOrdinalWeekdayInfo(dateObj);
    $("#monthly-weekday-info").text(info.label);

    if (!$("#id_nth_weekday").val()) {
        $("#id_nth_weekday").val(info.nth + 1);
    }

    if (!$("input[name='day_of_week']:checked").val()) {
        $("input[name='day_of_week']").prop("checked", false);
        $(`input[name='day_of_week'][value='${info.djangoDay}']`).prop("checked", true);
    }
}

// --- 毎年繰り返し関連 ---
function updateYearlyOptionsFromStartDate() {
    const dateStr = $("#id_start_date").val();
    if (!dateStr) return;

    const dateObj = new Date(dateStr);
    if (isNaN(dateObj)) return;

    const m = dateObj.getMonth() + 1;
    const d = dateObj.getDate();
    $("#yearly-date-info").text(`${m}月${d}日`);

    const info = getOrdinalWeekdayInfo(dateObj);
    $("#yearly-weekday-info").text(`${m}月${info.label}`);

    if (!$("#id_nth_weekday").val()) {
        $("#id_nth_weekday").val(info.nth + 1);
    }

    if (!$("input[name='day_of_week']:checked").val()) {
        $("input[name='day_of_week']").prop("checked", false);
        $(`input[name='day_of_week'][value='${info.djangoDay}']`).prop("checked", true);
    }
}

// --- 共通：第何週何曜日を取得 ---
function getOrdinalWeekdayInfo(dateObj) {
    const jsDay = dateObj.getDay();
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

// --- ボタン操作 ---
function bindFrequencyButtons() {
    $("#frequency-buttons button").click(function () {
        const value = $(this).data("value");
        $("#id_frequency").val(value);
        $("#frequency-buttons button").removeClass("selected");
        $(this).addClass("selected");

        $("#interval-field, #day-of-week-field, #nth-weekday-field").hide();
        $(".monthly-options, .yearly-options").hide();
        $(".field-help").text("");
        $(".day-label").show();
        $("input[name='day_of_week']").prop("checked", false);

        // if (value !== "NONE") {
        //     $("#id_interval").val(1);
        // } else {
        //     $("#id_interval").val("");
        // }

        if (value !== "NONE") {
            const currentInterval = $("#id_interval").val();
            // interval が空 or 0 の場合のみ1に設定する
            if (!currentInterval || currentInterval === "0") {
                $("#id_interval").val(1);
            }
        } else {
            $("#id_interval").val("");
        }

        switch (value) {
            case "DAILY":
                $("#interval-field").show();
                $("#interval-help").text("日ごと");
                break;
            case "WEEKLY":
                $("#interval-field, #day-of-week-field").show();
                $("#interval-help").text("週間ごと");
                setDayOfWeekFromStartDate();
                break;
            case "MONTHLY":
                $("#interval-field, #nth-weekday-field").show();
                $(".monthly-options").show();
                $("#interval-help").text("か月ごと");
                updateMonthlyOptionsFromStartDate();
                $("input[name='monthly_option'][value='by_date']").prop("checked", true);
                $("#monthly-nth-weekday-selects").hide();
                break;
            case "YEARLY":
                $("#interval-field, #nth-weekday-field").show();
                $(".yearly-options").show();
                $("#interval-help").text("年ごと");
                updateYearlyOptionsFromStartDate();
                break;
        }
    });
}

// --- イベントバインド ---
function bindStartDateChange() {
    $("#id_start_date").change(function () {
        updateStartDateWeekday();
        const freq = $("#id_frequency").val();
        $(`#frequency-buttons button[data-value='${freq}']`).addClass("selected");

        switch (freq) {
            case "WEEKLY":
                $("#interval-field, #day-of-week-field").show();
                setDayOfWeekFromStartDate();
                break;
            case "MONTHLY":
                $("#interval-field, #nth-weekday-field").show();
                $(".monthly-options").show();
                updateMonthlyOptionsFromStartDate();
                if ($("input[name='monthly_option']:checked").val() === "by_weekday") {
                    $("#monthly-nth-weekday-selects").show();
                }
                break;
            case "YEARLY":
                $("#interval-field, #nth-weekday-field").show();
                $(".yearly-options").show();
                updateYearlyOptionsFromStartDate();
                break;
        }
    });
}

function bindMonthlyOptionChange() {
    $("input[name='monthly_option']").change(function () {
        if ($(this).val() === "by_date") {
            $("#monthly-nth-weekday-selects").hide();
            $("#id_day_of_week").val("");
        } else {
            $("#monthly-nth-weekday-selects").hide();
        }
    });
}

function bindYearlyOptionChange() {
    $("input[name='yearly_option']").change(function () {
        if ($(this).val() === "by_date") {
            $("#yearly-nth-weekday-selects").hide();
            $("#id_day_of_week").val("");
        } else {
            $("#yearly-nth-weekday-selects").hide();
        }
    });
}

function updateMonthlyAndYearlyOptionRadios() {
    const dayOfWeek = $("input[name='day_of_week']:checked").val();
    const nthWeekday = $("#id_nth_weekday").val();  // 選択されている値
    const hasWeekdayRule = dayOfWeek || nthWeekday;

    if (hasWeekdayRule) {
        $("input[name='monthly_option'][value='by_weekday']").prop("checked", true);
        $("input[name='yearly_option'][value='by_weekday']").prop("checked", true);
    } else {
        $("input[name='monthly_option'][value='by_date']").prop("checked", true);
        $("input[name='yearly_option'][value='by_date']").prop("checked", true);
    }
}

function setInitialFrequencyState() {
    const initialFreq = $("#id_frequency").val();
    if (!initialFreq) return;

    // 全ボタンの selected クラスを外す
    $("#frequency-buttons button").removeClass("selected");
    // 初期 frequency に該当するボタンに selected を付ける
    $(`#frequency-buttons button[data-value='${initialFreq}']`).addClass("selected");

    // interval, day_of_week, nth_weekday のフォーム値はそのまま使うので、ここでは変更しない

    // まず、表示を全て隠す
    $("#interval-field, #day-of-week-field, #nth-weekday-field").hide();
    $(".monthly-options, .yearly-options").hide();
    $(".field-help").text("");
    $(".day-label").show();
    $("input[name='day_of_week']").prop("checked", false);

    // frequency によって表示切替
    switch (initialFreq) {
        case "NONE":
            $("#id_interval").val("");
            break;
        case "DAILY":
            $("#interval-field").show();
            $("#interval-help").text("日ごと");
            break;
        case "WEEKLY":
            $("#interval-field, #day-of-week-field").show();
            $("#interval-help").text("週間ごと");
            // day_of_week はフォームの値を反映しているはずなのでチェックは不要
            break;
        case "MONTHLY":
            $("#interval-field, #nth-weekday-field").show();
            $(".monthly-options").show();
            $("#interval-help").text("か月ごと");

            // 月毎のオプション選択はフォーム値に合わせて
            const monthlyOption = $("input[name='monthly_option']:checked").val() || "by_date";
            $("input[name='monthly_option'][value='" + monthlyOption + "']").prop("checked", true);

            // by_dateならnth_weekdayは隠す(by_weekdayなら表示)
            if (monthlyOption === "by_date") {
                $("#monthly-nth-weekday-selects").hide();
            } else {
                $("#monthly-nth-weekday-selects").show();
            }
            break;
        case "YEARLY":
            $("#interval-field, #nth-weekday-field").show();
            $(".yearly-options").show();
            $("#interval-help").text("年ごと");

            // yearly_option はフォームの値に合わせて選択
            const yearlyOption = $("input[name='yearly_option']:checked").val() || "by_date";
            $("input[name='yearly_option'][value='" + yearlyOption + "']").prop("checked", true);

            if (yearlyOption === "by_date") {
                $("#yearly-nth-weekday-selects").hide();
            } else {
                $("#yearly-nth-weekday-selects").show();
                // 必要ならここで nth_weekday の値セットも
            }
            break;
    }
}





document.addEventListener("DOMContentLoaded", function () {
    const deleteModal = document.getElementById("delete-modal");
    const openDeleteModalBtn = document.getElementById("open-delete-modal");
    const cancelDeleteBtn = document.getElementById("cancel-delete");
    // 削除ボタンを押した時のモーダル
    if (openDeleteModalBtn) {
        openDeleteModalBtn.addEventListener("click", function () {
            deleteModal.classList.remove("hidden");
        });
    }

    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener("click", function () {
            deleteModal.classList.add("hidden");
        });
    }
    // スケジュールIDから開始日を取得して表示、選択肢は当日以降に制限
    const startDateInput = document.getElementById("id_start_date");
    if (startDateInput) {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, "0");
        const dd = String(today.getDate()).padStart(2, "0");
        const todayStr = `${yyyy}-${mm}-${dd}`;

        startDateInput.min = todayStr;
    }
    // 変更ボタンを押した時のモーダル
    const openEditModalBtn = document.getElementById("open-edit-modal");
    const editModal = document.getElementById("edit-confirmation-modal");
    const confirmEditBtn = document.getElementById("edit-modal-confirm");
    const cancelEditBtn = document.getElementById("edit-modal-cancel");

    if (openEditModalBtn) {
        openEditModalBtn.addEventListener("click", function () {
            editModal.classList.remove("hidden");
        });
    }

    if (cancelEditBtn) {
        cancelEditBtn.addEventListener("click", function () {
            editModal.classList.add("hidden");
        });
    }

    if (confirmEditBtn) {
        confirmEditBtn.addEventListener("click", function () {
            editModal.classList.add("hidden");
        });
    }
});