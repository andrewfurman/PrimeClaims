// Add at the top of claim.js
let selectedMemberId = null;

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function searchMembers() {
    const searchInput = document.getElementById('memberSearch');
    const resultsDiv = document.getElementById('memberSearchResults');
    const searchTerm = searchInput.value.trim();

    if (searchTerm === '') {
        resultsDiv.classList.add('hidden');
        return;
    }

    fetch(`/members/search?q=${encodeURIComponent(searchTerm)}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                resultsDiv.innerHTML = `<p class="text-red-500 p-2">Error: ${data.error}</p>`;
                return;
            }

            if (data.length === 0) {
                resultsDiv.innerHTML = '<p class="text-gray-500 p-2">No members found</p>';
            } else {
                const resultsHtml = data.map(member => `
                    <div class="p-2 hover:bg-gray-100 cursor-pointer" onclick="selectMember(${member.database_id}, '${member.first_name} ${member.last_name}')">
                        <p class="font-semibold">${member.first_name} ${member.last_name}</p>
                        <p class="text-sm text-gray-600">ID: ${member.member_id}</p>
                    </div>
                `).join('');
                resultsDiv.innerHTML = resultsHtml;
            }
            resultsDiv.classList.remove('hidden');
        });
}

function selectMember(databaseId, memberName) {
    selectedMemberId = databaseId;
    const searchInput = document.getElementById('memberSearch');
    const resultsDiv = document.getElementById('memberSearchResults');
    searchInput.value = memberName;
    resultsDiv.classList.add('hidden');
}

// Add event listener when the page loads
document.addEventListener('DOMContentLoaded', function() {
    const memberSearchInput = document.getElementById('memberSearch');
    memberSearchInput.addEventListener('input', debounce(searchMembers, 300));
});

function createClaimGPT() {
    const button = document.getElementById('createGPTButton');
    const prompt = document.getElementById('gptPrompt').value;

    // Disable button and show loading state
    button.disabled = true;
    button.innerHTML = `
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Processing...
    `;

    // Construct URL based on whether a member is selected
    const baseUrl = '/claims/create-gpt';
    const params = new URLSearchParams();
    params.append('prompt', prompt);
    if (selectedMemberId) {
        params.append('member_database_id', selectedMemberId);
    }
    
    fetch(`${baseUrl}?${params.toString()}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        }
        window.location.reload();
    })
    .catch(error => {
        alert('Error creating claim');
        button.disabled = false;
        button.innerHTML = '✨ Create';
    });
}

function exportClaims() {
  const button = document.getElementById('exportButton');
  
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
  fetch('/claims/export', {
    method: 'GET',
  })
  .then(response => response.blob())
  .then(blob => {
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'claims_export.xlsx';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    
    // Reset button
    button.disabled = false;
    button.innerHTML = '📥 Export';
  })
  .catch(error => {
    alert('Error exporting claims');
    button.disabled = false;
    button.innerHTML = '📥 Export';
  });
}

function exportNCPDP() {
    const button = document.getElementById('ncpdpButton');
    
    // Disable button and show loading state
    button.disabled = true;
    button.innerHTML = `
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Processing...
    `;

    fetch('/ncpdp/export', {
        method: 'GET',
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'ncpdp_claims.dat';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        
        // Reset button
        button.disabled = false;
        button.innerHTML = '📄 NCPDP';
    })
    .catch(error => {
        alert('Error exporting NCPDP file');
        button.disabled = false;
        button.innerHTML = '📄 NCPDP';
    });
}