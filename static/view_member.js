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
function exportMemberClaims() {
  const button = document.getElementById('exportButton');
  const memberId = document.querySelector('[data-member-id]')?.getAttribute('data-member-id');
  
  if (!memberId) {
    alert('Member ID not found');
    return;
  }

  // Disable button and show loading state
  button.disabled = true;
  button.innerHTML = `
    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    Exporting...
  `;

  // Make API call
  fetch(`/claims/export?member_database_ids[]=${memberId}`, {
    method: 'GET',
  })
  .then(response => response.blob())
  .then(blob => {
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'member_claims_export.xlsx';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    
    // Reset button
    button.disabled = false;
    button.innerHTML = '📥 Export Claims';
  })
  .catch(error => {
    alert('Error exporting claims');
    button.disabled = false;
    button.innerHTML = '📥 Export Claims';
  });
}
