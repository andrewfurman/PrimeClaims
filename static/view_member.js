function deleteMember(memberId) {
    if (confirm('Are you sure you want to delete this member?')) {
        fetch(`/members/${memberId}/delete`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                window.location.href = '/members';
            }
        })
        .catch(error => {
            alert('Error deleting member');
        });
    }
}