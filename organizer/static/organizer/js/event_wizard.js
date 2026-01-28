let currentStep = 1;
const totalSteps = 4;
let debounceTimer; // Timer for API rate-limiting

function changeStep(n) {
    const steps = document.getElementsByClassName("form-step");
    const indicators = document.getElementsByClassName("stepper-item");

    steps[currentStep - 1].classList.remove("active");
    indicators[currentStep - 1].classList.remove("active");
    if (n > 0) indicators[currentStep - 1].classList.add("completed");

    currentStep += n;

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
    if (currentStep === 2) initOSMAutocomplete();

    const $gameType = $('#id_game_type');
    const $otherDiv = $('#div_id_game_type_other');
    function toggleOther() { $gameType.val() === 'OTHER' ? $otherDiv.show() : $otherDiv.hide(); }
    $gameType.change(toggleOther);
    toggleOther();

    $('#isFreeEvent').on('change', function() {
        const $container = $('#ticket-logic-container');
        if (this.checked) {
            $container.css({'opacity': '0.3', 'pointer-events': 'none'});
            $container.find('input').val('');
        } else {
            $container.css({'opacity': '1', 'pointer-events': 'all'});
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