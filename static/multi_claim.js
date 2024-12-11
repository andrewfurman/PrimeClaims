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
    
    // Add null checks
    if (!searchInput || !resultsDiv) {
        console.error('Search elements not found');
        return;
    }
    
    const searchTerm = searchInput.value.trim();

    if (searchTerm === '') {
        resultsDiv.style.display = 'none';
        return;
    }

    fetch(`/members/search?q=${encodeURIComponent(searchTerm)}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                resultsDiv.innerHTML = `<p class="text-red-500 p-2">Error: ${data.error}</p>`;
            } else if (data.length === 0) {
                resultsDiv.innerHTML = '<p class="text-gray-500 p-2">No members found</p>';
            } else {
                const resultsHtml = data.map(member => `
                    <div class="p-2 hover:bg-gray-100 cursor-pointer" 
                         onclick="selectMember('${member.database_id}', '${member.first_name} ${member.last_name}')">
                        <p class="font-semibold">${member.first_name} ${member.last_name}</p>
                        <p class="text-sm text-gray-600">ID: ${member.member_id}</p>
                    </div>
                `).join('');
                resultsDiv.innerHTML = resultsHtml;
            }
            resultsDiv.style.display = 'block';
        })
        .catch(error => {
            console.error('Search error:', error);
            if (resultsDiv) {
                resultsDiv.innerHTML = '<p class="text-red-500 p-2">Error searching for members</p>';
                resultsDiv.style.display = 'block';
            }
        });
}

function selectMember(databaseId, memberName) {
    console.log('Selecting member:', databaseId, memberName);
    selectedMemberId = databaseId;
    const searchInput = document.getElementById('memberSearch');
    const resultsDiv = document.getElementById('memberSearchResults');
    searchInput.value = memberName;
    resultsDiv.style.display = 'none';
}

function generateMultiClaims() {
    const button = document.getElementById('generateButton');
    const prompt = document.getElementById('multiClaimPrompt');
    const resultsSection = document.getElementById('resultsSection');
    const claimPrompts = document.getElementById('claimPrompts');

    if (!button || !prompt || !resultsSection || !claimPrompts) {
        console.error('Required elements not found');
        return;
    }

    button.disabled = true;
    button.innerHTML = `
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Generating...
    `;

    const requestData = {
        prompt: prompt.value
    };
    
    if (selectedMemberId) {
        requestData.member_database_id = selectedMemberId;
    }

    fetch('/multi-claims/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        button.disabled = false;
        button.innerHTML = '✨ Generate';
        claimPrompts.innerHTML = '';

        if (data.claim_specification_prompts) {
            resultsSection.style.display = 'block';
            data.claim_specification_prompts.forEach((spec, index) => {
                const specElement = document.createElement('div');
                specElement.className = 'bg-gray-50 p-4 rounded-lg';
                specElement.innerHTML = `
                    <h3 class="font-semibold text-lg mb-2">Scenario ${index + 1}</h3>
                    <p class="mb-2"><strong>Description:</strong> ${spec.scenario_description}</p>
                    <p><strong>Claim Prompt:</strong> ${spec.create_claim_prompt}</p>
                `;
                claimPrompts.appendChild(specElement);
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        button.disabled = false;
        button.innerHTML = '✨ Generate';
        alert('Error generating claims');
    });
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('Setting up member search');
    const memberSearchInput = document.getElementById('memberSearch');
    const resultsDiv = document.getElementById('memberSearchResults');
    const multiClaimPromptInput = document.getElementById('multiClaimPrompt');
    
    // Setup member search input handler
    if (memberSearchInput) {
        memberSearchInput.addEventListener('input', debounce(searchMembers, 300));
    }

    // Setup click handler to close results
    document.addEventListener('click', function(event) {
        if (resultsDiv && !resultsDiv.contains(event.target) && 
            event.target !== memberSearchInput) {
            resultsDiv.style.display = 'none';
        }
    });

    // Add specific handler for multiClaimPrompt to prevent unwanted interactions
    if (multiClaimPromptInput) {
        multiClaimPromptInput.addEventListener('click', function(event) {
            if (resultsDiv) {
                resultsDiv.style.display = 'none';
            }
        });
    }
});