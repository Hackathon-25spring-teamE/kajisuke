document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("exception-form");
    const modifiedDate = document.getElementById("id_modified_date");
    const modal = document.getElementById("confirmation-modal");
    const modalMessage = document.getElementById("modal-message");
    const modalConfirm = document.getElementById("modal-confirm");
    const modalCancel = document.getElementById("modal-cancel");

    const scheduledDate = window.scheduledDate || "";

    // 今日の日付を yyyy-mm-dd 形式で取得
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    const todayStr = `${yyyy}-${mm}-${dd}`;

    modifiedDate.min = todayStr;

    let currentAction = "";  // 'change' または 'delete'

    document.getElementById("change-only-btn").addEventListener("click", () => {
        if (modifiedDate.value) {
            currentAction = "change";
            modalMessage.textContent = "この予定をこの日のみ変更します。よろしいですか？";
            modal.classList.remove("hidden");
        } else {
            alert("変更するには変更日を入力してください。");
        }
    });

    document.getElementById("delete-only-btn").addEventListener("click", () => {
        if (!modifiedDate.value) {
            currentAction = "delete";
            modalMessage.textContent = "この予定をこの日のみ削除してもよろしいですか？";
            modal.classList.remove("hidden");
        } else {
            alert("削除する場合は変更日を空にしてください。");
        }
    });

    modalConfirm.addEventListener("click", () => {
        modal.classList.add("hidden");
        form.submit();  // フォーム送信
    });

    modalCancel.addEventListener("click", (event) => {
        event.preventDefault();
        modal.classList.add("hidden");
        modifiedDate.focus();
    });

    const isModified = window.isModified || false;
    if (isModified) {
        document.getElementById("modified-modal").classList.remove("hidden");
        document.getElementById("modified-ok-btn").addEventListener("click", () => {
            window.location.href = window.calendarRedirectUrl;
        });
    }
});
