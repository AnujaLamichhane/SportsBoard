// === GLOBAL STATE ===
let currentStep = 1;
const totalSteps = 4;
let debounceTimer; 

// === 1. NAVIGATION LOGIC ===
function changeStep(n) {
    console.log("Attempting to change step by:", n);
    const steps = document.getElementsByClassName("form-step");
    const indicators = document.getElementsByClassName("stepper-item");

    // Validation check when moving forward
    if (n > 0) {
        const isStepValid = validateCurrentStep();
        console.log("Step validation result:", isStepValid);
        if (!isStepValid) {
            console.warn("Validation failed. Check for red fields.");
            return; 
        }
    }

    // Safety check: Ensure the step exists
    if (!steps[currentStep + n - 1]) {
        console.error("Target step does not exist in HTML.");
        return;
    }

    // Hide current step
    steps[currentStep - 1].classList.remove("active");
    if(indicators[currentStep - 1]) {
        indicators[currentStep - 1].classList.remove("active");
        if (n > 0) indicators[currentStep - 1].classList.add("completed");
    }

    // Update Counter
    currentStep += n;

    // Show new step
    steps[currentStep - 1].classList.add("active");
    if(indicators[currentStep - 1]) {
        indicators[currentStep - 1].classList.add("active");
    }

    // Initialize map if we enter step 2
    if (currentStep === 2) initOSMAutocomplete();

    // Update Button Visibility
    updateNavButtons();

    // Smooth scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateNavButtons() {
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const submitBtn = document.getElementById("submitBtn");

    if (!prevBtn || !nextBtn || !submitBtn) {
        console.error("Navigation buttons not found in DOM!");
        return;
    }

    prevBtn.disabled = (currentStep === 1);

    if (currentStep === totalSteps) {
        nextBtn.classList.add("d-none");
        submitBtn.classList.remove("d-none");
    } else {
        nextBtn.classList.remove("d-none");
        submitBtn.classList.add("d-none");
    }
    console.log("Navigation buttons updated. Now on step:", currentStep);
}

// === 2. VALIDATION ===
function validateCurrentStep() {
    const activeStep = document.querySelector(".form-step.active");
    if (!activeStep) return true;

    const requiredFields = activeStep.querySelectorAll("[required]");
    let isValid = true;

    requiredFields.forEach(field => {
        const wrapper = field.closest('.input-group') || field.closest('.mb-3') || field.parentElement;
        const label = wrapper ? wrapper.querySelector('label') : null;

        // Reset previous states
        field.classList.remove("is-invalid");
        if (label) label.classList.remove("invalid-label");
        
        // Only validate if visible
        const isVisible = !!(field.offsetWidth || field.offsetHeight || field.getClientRects().length);

        if (isVisible && !field.value.trim()) {
            isValid = false;
            field.classList.add("is-invalid");
            if (label) {
                label.classList.add("invalid-label");
            }
            
            console.log("Required field empty:", field.name);
        }
    });

    return isValid;
}

// === 3. LOCATION AUTOCOMPLETE ===
function initOSMAutocomplete() {
    const input = document.getElementById('id_location');
    const resultsList = document.getElementById('geo-results-list');
    
    if (!input || input.dataset.initialized || !window.GeoSearch) return;

    const provider = new window.GeoSearch.OpenStreetMapProvider({
        params: { countrycodes: 'np', limit: 6 } 
    });

    input.addEventListener('input', function() {
        const query = this.value.trim();
        clearTimeout(debounceTimer);
        resultsList.innerHTML = '';
        if (query.length < 3) return;

        debounceTimer = setTimeout(async () => {
            try {
                const results = await provider.search({ query });
                resultsList.innerHTML = '';
                results.forEach(place => {
                    const item = document.createElement('div');
                    item.className = 'geo-item';
                    item.textContent = place.label;
                    item.addEventListener('click', () => {
                        input.value = place.label;
                        resultsList.innerHTML = '';
                    });
                    resultsList.appendChild(item);
                });
            } catch (err) { console.error("OSM error:", err); }
        }, 500);
    });

    input.dataset.initialized = "true";
}

// === 4. DATE & STATUS ===
function setCurrentDateTime() {
    const dateTimeInput = document.getElementById('id_date_time');
    if (dateTimeInput) {
        const now = new Date();
        const formattedNow = now.toISOString().slice(0, 16);
        dateTimeInput.setAttribute('min', formattedNow);
        if (!dateTimeInput.value) {
            dateTimeInput.value = formattedNow;
            updateStatus();
        }
    }
}

function updateStatus() {
    const dateTimeInput = document.getElementById('id_date_time');
    const statusField = document.getElementById('id_status');

    if (!dateTimeInput || !statusField || !dateTimeInput.value) return;

    const selectedTime = new Date(dateTimeInput.value);
    const now = new Date();
    
    // Buffer: If the event is within the next 1 hour, call it LIVE
    const oneHourFromNow = new Date(now.getTime() + (60 * 60 * 1000));

    let newStatus = 'UPCOMING';

    if (selectedTime < now) {
        newStatus = 'PAST';
    } else if (selectedTime <= oneHourFromNow) {
        newStatus = 'LIVE';
    } else {
        newStatus = 'UPCOMING';
    }

    // Update the dropdown value
    statusField.value = newStatus;
    
    // Trigger a 'change' event so other scripts know it updated
    statusField.dispatchEvent(new Event('change'));
    
    console.log("Status auto-updated to:", newStatus);
}

// === 5. JQUERY INIT ===
$(document).ready(function() {
    setCurrentDateTime();
    updateNavButtons();

    $('#id_date_time').on('change', updateStatus);

    const $gameType = $('#id_game_type');
    const $otherDiv = $('#div_id_game_type_other');
    function toggleOther() { $gameType.val() === 'OTHER' ? $otherDiv.show() : $otherDiv.hide(); }
    $gameType.on('change', toggleOther);
    toggleOther();

    $('#isFreeEvent').on('change', function() {
        $('#ticket-logic-container').toggle(!this.checked);
    });

    function setupFormset(btnId, containerId, managementId, templateId) {
        $(`#${btnId}`).on('click', function() {
            const $totalForms = $(`#${managementId}`);
            let total = parseInt($totalForms.val());
            let template = $(`#${templateId}`).html();
            if(!template) { console.error("Template missing:", templateId); return; }
            let newHtml = template.replace(/__prefix__/g, total);
            $(`#${containerId}`).append(newHtml);
            $totalForms.val(total + 1);
        });
    }

    setupFormset('add-match', 'match-formset-container', 'id_matches-TOTAL_FORMS', 'empty-match-template');
    setupFormset('add-ticket-tier', 'ticket-formset-container', 'id_tickets-TOTAL_FORMS', 'empty-ticket-tier-template');
});
