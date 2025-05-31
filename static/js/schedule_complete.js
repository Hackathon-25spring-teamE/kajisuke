document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('.check-icon');

    images.forEach(function(image) {
        image.addEventListener('click', function() {
            const scheduleId = image.getAttribute('data-completed-id');
            const isChecked = !image.src.includes('unchecked.svg');
            const url = `/api/schedules/${scheduleId}/complete/${currentYear}/${currentMonth}/${currentDay}/`;
            // 対応するtaskを取得
            const taskNameElement = document.querySelector(`p[data-task-id='${scheduleId}']`);

            if (isChecked) {
                // チェック済みの場合、DELETEリクエストを送る
                fetch(url, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken  // CSRFトークンをヘッダーに追加
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'not_completed') {
                        image.src = uncheckedImageSrc;  // 画像を未チェックに変更
                        taskNameElement.classList.remove('strikethrough');  // 取り消し線を削除
                    }
                })
                .catch(error => console.error('Error:', error));
            } else {
                // 未チェックの場合、POSTリクエストを送る
                fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken  // CSRFトークンをヘッダーに追加
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'completed') {
                        image.src = checkedImageSrc;  // 画像をチェック済みに変更
                        taskNameElement.classList.add('strikethrough');  // 取り消し線を追加
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        });
    });
});
