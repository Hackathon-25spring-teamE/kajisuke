document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('.check-icon');

    images.forEach(function(image) {
        image.addEventListener('click', function() {
            const scheduleId = image.getAttribute('data-schedule-id');
            const isChecked = !image.src.includes('unchecked.svg');
            const url = `/api/schedules/${scheduleId}/complete/${currentYear}/${currentMonth}/${currentMonth}/`;
            
            if (isChecked) {
                // チェック済みの場合、DELETEリクエストを送る
                fetch(url, {
                    method: 'DELETE',
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'not_completed') {
                        image.src = uncheckedImageSrc;  // 画像を未チェックに変更
                    }
                })
                .catch(error => console.error('Error:', error));
            } else {
                // 未チェックの場合、POSTリクエストを送る
                fetch(url, {
                    method: 'POST',
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'completed') {
                        image.src = checkedImageSrc;  // 画像をチェック済みに変更
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        });
    });
});
