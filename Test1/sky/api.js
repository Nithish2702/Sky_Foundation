/**
 * API Integration for Qatar Foundation Admin Portal
 * Connects frontend to Flask backend
 */

// Automatically detect environment and use appropriate API URL
const API_BASE_URL = (() => {
    const hostname = window.location.hostname;
    
    // Local development
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://localhost:5000/api';
    }
    
    // Production - Your Render backend URL
    return 'https://sky-foundation.onrender.com/api';
})();

// Helper function to make API requests
async function apiRequest(endpoint, options = {}) {
    const defaultOptions = {
        credentials: 'include', // Include cookies for session management
        headers: {
            'Content-Type': 'application/json',
        },
    };

    const config = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        
        // Check if response is JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Server returned non-JSON response');
        }
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'An error occurred');
        }
        
        return { success: true, data };
    } catch (error) {
        console.error('API Request Error:', error);
        return { success: false, error: error.message };
    }
}

// ==================== AUTHENTICATION API ====================

/**
 * Sign up a new admin
 */
async function signupAPI(fullName, email, password, confirmPassword) {
    return await apiRequest('/auth/signup', {
        method: 'POST',
        body: JSON.stringify({
            full_name: fullName,
            email: email,
            password: password,
            confirm_password: confirmPassword
        })
    });
}

/**
 * Login admin
 */
async function loginAPI(email, password, rememberMe) {
    return await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify({
            email: email,
            password: password,
            remember_me: rememberMe
        })
    });
}

/**
 * Logout admin
 */
async function logoutAPI() {
    return await apiRequest('/auth/logout', {
        method: 'POST'
    });
}

/**
 * Request password reset
 */
async function forgotPasswordAPI(email) {
    return await apiRequest('/auth/forgot-password', {
        method: 'POST',
        body: JSON.stringify({
            email: email
        })
    });
}

/**
 * Get current admin info
 */
async function getCurrentAdminAPI() {
    return await apiRequest('/auth/me', {
        method: 'GET'
    });
}

// ==================== OPPORTUNITY API ====================

/**
 * Get all opportunities for logged-in admin
 */
async function getOpportunitiesAPI() {
    return await apiRequest('/opportunities', {
        method: 'GET'
    });
}

/**
 * Create a new opportunity
 */
async function createOpportunityAPI(opportunityData) {
    return await apiRequest('/opportunities', {
        method: 'POST',
        body: JSON.stringify(opportunityData)
    });
}

/**
 * Get opportunity details by ID
 */
async function getOpportunityDetailsAPI(opportunityId) {
    return await apiRequest(`/opportunities/${opportunityId}`, {
        method: 'GET'
    });
}

/**
 * Update an opportunity
 */
async function updateOpportunityAPI(opportunityId, opportunityData) {
    return await apiRequest(`/opportunities/${opportunityId}`, {
        method: 'PUT',
        body: JSON.stringify(opportunityData)
    });
}

/**
 * Delete an opportunity
 */
async function deleteOpportunityAPI(opportunityId) {
    return await apiRequest(`/opportunities/${opportunityId}`, {
        method: 'DELETE'
    });
}

// ==================== HELPER FUNCTIONS ====================

/**
 * Load opportunities from backend and display them
 */
async function loadOpportunities() {
    const result = await getOpportunitiesAPI();
    
    if (result.success) {
        const opportunities = result.data.opportunities;
        displayOpportunities(opportunities);
    } else {
        console.error('Failed to load opportunities:', result.error);
        showToast('Failed to load opportunities');
    }
}

/**
 * Display opportunities in the grid
 */
function displayOpportunities(opportunities) {
    const grid = document.querySelector('.opportunities-grid');
    if (!grid) return;
    
    // Clear existing opportunities (except the modal)
    grid.innerHTML = '';
    
    if (opportunities.length === 0) {
        grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--qf-text-light);">No opportunities created yet. Click "Add New Opportunity" to create one.</div>';
        return;
    }
    
    opportunities.forEach(opp => {
        const card = createOpportunityCard(opp);
        grid.appendChild(card);
    });
}

/**
 * Create opportunity card element
 */
function createOpportunityCard(opp) {
    const card = document.createElement('div');
    card.className = 'opportunity-card';
    card.dataset.opportunityId = opp.id;
    
    const skillsList = opp.skills_list || opp.skills.split(',').map(s => s.trim());
    const applicantsText = opp.max_applicants 
        ? `${opp.current_applicants || 0}/${opp.max_applicants} applicants`
        : `${opp.current_applicants || 0} applicants`;
    
    card.innerHTML = `
        <div class="opportunity-card-header">
            <h5>${escapeHtml(opp.name)}</h5>
            <div class="opportunity-meta">
                <span><svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>${escapeHtml(opp.duration)}</span>
                <span><svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>${escapeHtml(opp.start_date)}</span>
            </div>
        </div>
        <p class="opportunity-description">${escapeHtml(opp.description)}</p>
        <div class="opportunity-skills">
            <div class="opportunity-skills-label">Skills You'll Gain</div>
            <div class="skills-tags">
                ${skillsList.map(skill => `<span class="skill-tag">${escapeHtml(skill)}</span>`).join('')}
            </div>
        </div>
        <div class="opportunity-footer">
            <span class="applicants-count">${escapeHtml(applicantsText)}</span>
            <div style="display: flex; gap: 8px;">
                <button class="edit-opportunity-btn" onclick="editOpportunity(${opp.id})" style="padding: 8px 12px; background: var(--qf-green); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 13px;">Edit</button>
                <button class="delete-opportunity-btn" onclick="deleteOpportunity(${opp.id})" style="padding: 8px 12px; background: var(--qf-red); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 13px;">Delete</button>
                <button class="view-course-btn" onclick="viewOpportunityDetails(${opp.id})" style="width: auto; padding: 8px 16px;">View Details</button>
            </div>
        </div>
    `;
    
    return card;
}

/**
 * View opportunity details
 */
async function viewOpportunityDetails(opportunityId) {
    const result = await getOpportunityDetailsAPI(opportunityId);
    
    if (result.success) {
        const opp = result.data.opportunity;
        const skillsList = opp.skills_list || opp.skills.split(',').map(s => s.trim());
        
        openOpportunityDetails(opp.name, {
            duration: opp.duration,
            startDate: opp.start_date,
            description: opp.description,
            skills: skillsList,
            applicants: opp.current_applicants || 0,
            futureOpportunities: opp.future_opportunities,
            prerequisites: ''
        });
    } else {
        showToast('Failed to load opportunity details');
    }
}

/**
 * Edit opportunity
 */
async function editOpportunity(opportunityId) {
    const result = await getOpportunityDetailsAPI(opportunityId);
    
    if (result.success) {
        const opp = result.data.opportunity;
        
        // Populate form with existing data
        document.getElementById('oppName').value = opp.name;
        document.getElementById('oppDuration').value = opp.duration;
        document.getElementById('oppStartDate').value = opp.start_date;
        document.getElementById('oppDescription').value = opp.description;
        document.getElementById('oppSkills').value = opp.skills;
        document.getElementById('oppCategory').value = opp.category;
        document.getElementById('oppFuture').value = opp.future_opportunities;
        document.getElementById('oppMaxApplicants').value = opp.max_applicants || '';
        
        // Store opportunity ID for update
        document.getElementById('opportunityForm').dataset.editId = opportunityId;
        
        // Change button text
        const submitBtn = document.querySelector('#opportunityForm button[type="submit"]');
        submitBtn.textContent = 'Update Opportunity';
        
        // Open modal
        openOpportunityModal();
    } else {
        showToast('Failed to load opportunity for editing');
    }
}

/**
 * Delete opportunity with confirmation
 */
async function deleteOpportunity(opportunityId) {
    if (!confirm('Are you sure you want to delete this opportunity? This action cannot be undone.')) {
        return;
    }
    
    const result = await deleteOpportunityAPI(opportunityId);
    
    if (result.success) {
        showToast('Opportunity deleted successfully');
        await loadOpportunities();
    } else {
        showToast('Failed to delete opportunity: ' + result.error);
    }
}

// Export functions for use in admin.js
window.signupAPI = signupAPI;
window.loginAPI = loginAPI;
window.logoutAPI = logoutAPI;
window.forgotPasswordAPI = forgotPasswordAPI;
window.getCurrentAdminAPI = getCurrentAdminAPI;
window.getOpportunitiesAPI = getOpportunitiesAPI;
window.createOpportunityAPI = createOpportunityAPI;
window.getOpportunityDetailsAPI = getOpportunityDetailsAPI;
window.updateOpportunityAPI = updateOpportunityAPI;
window.deleteOpportunityAPI = deleteOpportunityAPI;
window.loadOpportunities = loadOpportunities;
window.viewOpportunityDetails = viewOpportunityDetails;
window.editOpportunity = editOpportunity;
window.deleteOpportunity = deleteOpportunity;
