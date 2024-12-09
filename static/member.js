// Remove the duplicate event listeners and consolidate into one at the bottom of the file
document.addEventListener('DOMContentLoaded', function() {
  // Initialize search functionality
  const searchInput = document.getElementById('searchInput');
  if (searchInput) {  // Add null check
    searchInput.addEventListener('input', debounce(performSearch, 300));
  }
});

function createMemberGPT() {
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
  // Make API call
  fetch('/members/create-gpt', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ prompt: prompt })
  })
  .then(response => response.json())
  .then(data => {
    if (data.error) {
      alert(data.error);
    }
    // Refresh the page
    window.location.reload();
  })
  .catch(error => {
    alert('Error creating member');
    button.disabled = false;
    button.innerHTML = 'Create Member GPT';
  });
}

function exportMembers() {
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
  fetch('/members/export', {
    method: 'GET',
  })
  .then(response => response.blob())
  .then(blob => {
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'members_export.xlsx';
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    
    // Reset button - Fixed text to match HTML
    button.disabled = false;
    button.innerHTML = '📥 Export';
  })
  .catch(error => {
    alert('Error exporting members');
    button.disabled = false;
    button.innerHTML = '📥 Export'; // Fixed text to match HTML
  });
}

function deleteMember(memberId) {
  if (!confirm('Are you sure you want to delete this member?')) {
    return;
  }

  const button = event.target;
  button.disabled = true;
  button.innerHTML = `
    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
    Deleting...
  `;

  fetch(`/members/${memberId}/delete`, {
    method: 'DELETE',
  })
  .then(response => {
    if (response.ok) {
      window.location.href = '/members';
    } else {
      throw new Error('Failed to delete member');
    }
  })
  .catch(error => {
    alert('Error deleting member');
    button.disabled = false;
    button.innerHTML = '🗑️ Delete Member';
  });
}

function toggleSearch() {
  const overlay = document.getElementById('searchOverlay');
  overlay.classList.toggle('hidden');
  if (!overlay.classList.contains('hidden')) {
    document.getElementById('searchInput').focus();
  }
}

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

function performSearch() {
  const searchInput = document.getElementById('searchInput');
  const searchResults = document.getElementById('searchResults');
  const searchTerm = searchInput.value.trim();

  if (searchTerm === '') {
    searchResults.innerHTML = '';
    return;
  }

  fetch(`/members/search?q=${encodeURIComponent(searchTerm)}`)
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        searchResults.innerHTML = `<p class="text-red-500">Error: ${data.error}</p>`;
        return;
      }

      if (data.length === 0) {
        searchResults.innerHTML = '<p class="text-gray-500">No results found</p>';
        return;
      }

      const resultsHtml = data.map(member => `
        <div class="p-4 border rounded-lg hover:bg-gray-50">
          <a href="/members/${member.member_id}" class="block">
            <p class="font-bold">${member.first_name} ${member.last_name}</p>
            <p class="text-sm text-gray-600">
              ID: ${member.member_id} | DOB: ${member.date_of_birth || 'N/A'}<br>
              ${member.city}, ${member.state} | Group: ${member.group_number}
            </p>
          </a>
        </div>
      `).join('');

      searchResults.innerHTML = resultsHtml;
    })
    .catch(error => {
      searchResults.innerHTML = '<p class="text-red-500">Error performing search</p>';
    });
}

// Add event listener when the page loads
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('searchInput');
  searchInput.addEventListener('input', debounce(performSearch, 300));
});