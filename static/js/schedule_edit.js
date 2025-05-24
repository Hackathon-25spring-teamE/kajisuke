console.log("schedule_edit.js 読み込み成功！");
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
            window.location.href = editUrl;
        });
    }
});