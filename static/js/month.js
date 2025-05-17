document.addEventListener('DOMContentLoaded', function() {
  const calendarEl = document.getElementById('calendar');
  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    // month.htmlで定義した年月を初期表示に設定
    initialDate: `${current_year}-${current_month.toString().padStart(2, '0')}-01`, 
    // headerToolbar: {
    //     left: 'prev',
    //     center: 'title',
    //     right: 'next'
    //     },
    headerToolbar: false,
    events: '/api/schedules',   // スケジュールリストのリクエスト
    timeZone: "Asia/Tokyo",
    locale: "jp",
    displayEventTime: false,  // 時間表示を消す設定
    dayMaxEventRows: true,
    height: 650, 
    eventBorderColor: 'transparent', // イベントボーダーの色を透明にする
    // 日付から「日」表記を外す
    dayCellContent: function(arg){
        return arg.date.getDate();
    },
    // ポップアップを開かないように明示
    eventLimitClick: false,  // ← この設定は古いが残っていれば追加
    moreLinkClick: function() {
        return 'none';         // ← 「+N件」クリック時も無反応にする
    },
    selectable: false,  // ← 選択機能を無効化
    eventClick: function(info) {
        info.jsEvent.preventDefault(); // デフォルト動作無効
        info.el.blur(); // 明示的に focus を外す
    },
    // 日付クリック時にURL遷移
    dateClick: function(info) {
        const date = new Date(info.dateStr);  // クリックされた日付
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0'); // 月は0-index
        const day = String(date.getDate()).padStart(2, '0');

        const url = `/calendars/${year}/${month}/${day}`;
        window.location.href = url;
    }
  });

  calendar.render();
  });