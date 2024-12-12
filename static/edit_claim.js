
document.addEventListener('DOMContentLoaded', () => {
    const editClaimForm = document.getElementById('editClaimForm');
    if (editClaimForm) {
        editClaimForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const button = e.target.querySelector('button[type="submit"]');
            button.disabled = true;
            button.innerHTML = 'Saving...';
            
            try {
                const response = await fetch(window.location.href, {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    window.location.reload();
                } else {
                    alert('Error updating claim: ' + result.error);
                }
            } catch (error) {
                alert('Error updating claim: ' + error);
            } finally {
                button.disabled = false;
                button.innerHTML = 'Save Changes';
            }
        });
    }
});
