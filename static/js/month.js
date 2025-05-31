document.addEventListener('DOMContentLoaded', function() {
    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        // month.htmlで定義した年月を初期表示に設定
        initialDate: `${currentYear}-${currentMonth.toString().padStart(2, '0')}-01`, 
        // 指定された月のスケジュールリストを取得
        events: '/api/schedules/',
        headerToolbar: false,
        timeZone: "Asia/Tokyo",
        locale: "jp",
        displayEventTime: false,
        dayMaxEventRows: true,
        height: 650,
        eventBorderColor: 'transparent',
        // month.htmlで定義したholidaysを用いて祝日か判定する
        dayCellDidMount: function(info) {
        const dateStr = info.date.toISOString().split('T')[0];
            if (holidays.includes(dateStr)) {
            info.el.classList.add('holiday');
            }
        },
        // 日付から「日」表記を外す
        dayCellContent: function(arg){
            return arg.date.getDate();
        },
        // 日付スペース内をクリック時に1日のスケジュール一覧へ遷移
        dateClick: function(info) {
            redirectToCalendarDay(info.dateStr);
        },
        // イベントクリック時も1日のスケジュール一覧へ遷移
        eventClick: function(info) {
            info.el.blur(); // 明示的に focus を外す
            redirectToCalendarDay(info.event.start);
        },
        // moreクリック時も1日のスケジュール一覧へ遷移
        moreLinkClick: function(info) {
            redirectToCalendarDay(info.date);
            // ポップアップを無効化
            return 'none';
        },
    });

    // 指定された日付の1日のスケジュール一覧へ遷移
    const redirectToCalendarDay = (currentDate) => {
        const date = new Date(currentDate);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0'); // 月は0-index
        const day = String(date.getDate()).padStart(2, '0');

        const url = `/calendars/${year}/${month}/${day}/`;
        window.location.href = url;
    };

    calendar.render();
});