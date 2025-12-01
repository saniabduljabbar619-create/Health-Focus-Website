document.addEventListener("DOMContentLoaded", () => {

    // DELETE PROFILE
    document.querySelectorAll(".admin-delete").forEach(btn => {
        btn.addEventListener("click", () => {

            const id = btn.dataset.id;

            if (!confirm("Are you sure you want to delete this profile?")) {
                return;
            }

            fetch(`/admin/hod/delete/${id}`, {
                method: "POST"
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert("Profile deleted successfully");
                    location.reload();
                }
            });
        });
    });

});
