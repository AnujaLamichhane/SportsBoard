let currentStep = 1;
const totalSteps = 4;
let debounceTimer; // Timer for API rate-limiting



function changeStep(n) {
    const steps = document.getElementsByClassName("form-step");
    const indicators = document.getElementsByClassName("stepper-item");

    // VALIDATION: Only check when moving forward
    if (n > 0) {
        if (!validateCurrentStep()) {
            return; // Stop here if fields are missing
        }
    }

    // Hide current step
    steps[currentStep - 1].classList.remove("active");
    indicators[currentStep - 1].classList.remove("active");

    if (n > 0) indicators[currentStep - 1].classList.add("completed");

    currentStep += n;

    // Show new step
    steps[currentStep - 1].classList.add("active");
    indicators[currentStep - 1].classList.add("active");

    if (currentStep === 2) initOSMAutocomplete();

    document.getElementById("prevBtn").disabled = (currentStep === 1);

    if (currentStep === totalSteps) {
        document.getElementById("nextBtn").classList.add("d-none");
        document.getElementById("submitBtn").classList.remove("d-none");
    } else {
        document.getElementById("nextBtn").classList.remove("d-none");
        document.getElementById("submitBtn").classList.add("d-none");
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// === OPENSTREETMAP AUTOCOMPLETE WITH DEBOUNCE ===
function initOSMAutocomplete() {
    const input = document.getElementById('id_location');
    const resultsList = document.getElementById('geo-results-list');
    if (!input || input.dataset.initialized) return;

    if (!window.GeoSearch) {
        console.error("GeoSearch library not loaded!");
        return;
    }

    const provider = new window.GeoSearch.OpenStreetMapProvider({
        params: { countrycodes: 'np', limit: 6 } // Restricts to Nepal
    });

    input.addEventListener('input', function() {
        const query = this.value.trim();

        // Clear existing timer to reset the wait period
        clearTimeout(debounceTimer);
        resultsList.innerHTML = '';

        if (query.length < 3) return;

        // Wait 500ms after last keystroke before fetching
        debounceTimer = setTimeout(async () => {
            try {
                const results = await provider.search({ query });
                resultsList.innerHTML = '';

                if (!results.length) {
                    resultsList.innerHTML = '<div class="geo-item text-muted">No locations found</div>';
                    return;
                }

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
            } catch (err) {
                console.error("OSM search error:", err);
                // Handle 429 or network errors gracefully
                resultsList.innerHTML = '<div class="geo-item text-danger">Search temporarily unavailable.</div>';
            }
        }, 500);
    });

    document.addEventListener('click', function(e) {
        if (!resultsList.contains(e.target) && e.target !== input) {
            resultsList.innerHTML = '';
        }
    });

    input.dataset.initialized = "true";
}

$(document).ready(function() {

// 1. Set current time on load
    setCurrentDateTime();

    // 2. Watch for manual changes to date_time
    $('#id_date_time').on('change', function() {
        updateStatus();
    });

    if (currentStep === 2) initOSMAutocomplete();

    const $gameType = $('#id_game_type');
    const $otherDiv = $('#div_id_game_type_other');
    function toggleOther() { $gameType.val() === 'OTHER' ? $otherDiv.show() : $otherDiv.hide(); }
    $gameType.change(toggleOther);
    toggleOther();

//    $('#isFreeEvent').on('change', function() {
//        const $container = $('#ticket-logic-container');
//        if (this.checked) {
//            $container.css({'opacity': '0.3', 'pointer-events': 'none'});
//            $container.find('input').val('');
//        } else {
//            $container.css({'opacity': '1', 'pointer-events': 'all'});
//        }
//    });

$('#isFreeEvent').on('change', function() {
    const $container = $('#ticket-logic-container');
    if (this.checked) {
        $container.hide(); // Hides the inputs but keeps management_form visible if moved outside
    } else {
        $container.show();
    }
});

    function setupFormset(btnId, containerId, managementId, templateId) {
        $(`#${btnId}`).on('click', function() {
            const $totalForms = $(`#${managementId}`);
            let total = parseInt($totalForms.val());
            let template = $(`#${templateId}`).html();
            let newHtml = template.replace(/__prefix__/g, total);
            $(`#${containerId}`).append(newHtml);
            $totalForms.val(total + 1);
        });
    }

    setupFormset('add-match', 'match-formset-container', 'id_matches-TOTAL_FORMS', 'empty-match-template');
    setupFormset('add-ticket-tier', 'ticket-formset-container', 'id_tickets-TOTAL_FORMS', 'empty-ticket-tier-template');
});

function validateCurrentStep() {
    const activeStep = document.querySelector(".form-step.active");
    const requiredFields = activeStep.querySelectorAll("[required]");
    let isValid = true;

    requiredFields.forEach(field => {
        // Reset previous error styling
        field.classList.remove("is-invalid");

        // Check if field is empty
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add("is-invalid"); // Bootstrap error class

            // Optional: Shake effect or focus the first empty field
            field.placeholder = "This field is required";
        }
    });

    if (!isValid) {
        console.warn("Please fill all mandatory fields before proceeding.");
    }

    return isValid;
}

function setCurrentDateTime() {
    const dateTimeInput = document.getElementById('id_date_time');
    if (dateTimeInput) {
        const now = new Date();
        // Format: YYYY-MM-DDTHH:MM
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');

        const formattedNow = `${year}-${month}-${day}T${hours}:${minutes}`;

        // Set the MINIMUM allowed date to now
        dateTimeInput.setAttribute('min', formattedNow);

        // Only set the default value if it's currently empty
        if (!dateTimeInput.value) {
            dateTimeInput.value = formattedNow;
            updateStatus(); // Initial status update
        }
    }
}

function updateStatus() {
    const dateTimeInput = document.getElementById('id_date_time');
    const statusField = document.getElementById('id_status');

    if (!dateTimeInput || !statusField || !dateTimeInput.value) return;

    const selectedTime = new Date(dateTimeInput.value);
    const now = new Date();

    // Logic: If the selected time is in the past, reset it or handle it
    if (selectedTime < now) {
        // Optional: Force the value back to 'now' if they bypass the picker
        // dateTimeInput.value = dateTimeInput.getAttribute('min');
        statusField.value = 'PAST';
    } else if (selectedTime.toDateString() === now.toDateString() &&
               (selectedTime - now) < 3600000) { // Within 1 hour
        statusField.value = 'LIVE';
    } else {
        statusField.value = 'UPCOMING';
    }
}