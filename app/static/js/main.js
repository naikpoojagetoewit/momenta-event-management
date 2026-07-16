// Auto-dismiss alerts after 4 seconds
document.addEventListener('DOMContentLoaded', function () {
    setTimeout(function () {
        document.querySelectorAll('.alert').forEach(function (alert) {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        });
    }, 5000);
});

/* ---------------- Booking form: service selection + live budget calculator ---------------- */
function initBookingForm() {
    const form = document.getElementById('bookingForm');
    if (!form) return;

    const serviceCards = document.querySelectorAll('.service-select-card');
    const eventSelect = document.getElementById('event_id');
    const guestInput = document.getElementById('guest_count');
    const exactTotalEl = document.getElementById('exactTotal');
    const aiRangeEl = document.getElementById('aiRange');

    function selectedServiceIds() {
        return Array.from(document.querySelectorAll('.service-checkbox:checked')).map(cb => cb.value);
    }

    function refreshBudget() {
        const eventId = eventSelect ? eventSelect.value : '';
        const guestCount = guestInput ? (guestInput.value || 0) : 0;
        const serviceIds = selectedServiceIds();

        if (!eventId) return;

        const params = new URLSearchParams();
        params.append('event_id', eventId);
        params.append('guest_count', guestCount);
        serviceIds.forEach(id => params.append('service_ids', id));

        fetch(`/client/api/budget-estimate?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                if (exactTotalEl) exactTotalEl.textContent = '₹ ' + Number(data.exact_total).toLocaleString('en-IN');
                if (aiRangeEl) {
                    aiRangeEl.textContent = '₹ ' + Number(data.ai_estimate_low).toLocaleString('en-IN') +
                        ' - ₹ ' + Number(data.ai_estimate_high).toLocaleString('en-IN');
                }
            })
            .catch(err => console.error('Budget estimate failed', err));
    }

    serviceCards.forEach(card => {
        card.addEventListener('click', function (e) {
            if (e.target.tagName === 'INPUT') return;
            const checkbox = card.querySelector('.service-checkbox');
            checkbox.checked = !checkbox.checked;
            card.classList.toggle('selected', checkbox.checked);
            refreshBudget();
        });
        const checkbox = card.querySelector('.service-checkbox');
        checkbox.addEventListener('change', function () {
            card.classList.toggle('selected', checkbox.checked);
            refreshBudget();
        });
    });

    if (eventSelect) eventSelect.addEventListener('change', refreshBudget);
    if (guestInput) guestInput.addEventListener('input', refreshBudget);

    refreshBudget();
}
document.addEventListener('DOMContentLoaded', initBookingForm);

/* ---------------- Star rating widget (feedback form) ---------------- */
function initStarRating() {
    const stars = document.querySelectorAll('.star-rating i');
    const ratingInput = document.getElementById('ratingInput');
    if (!stars.length) return;

    stars.forEach(star => {
        star.addEventListener('click', function () {
            const value = parseInt(this.dataset.value, 10);
            ratingInput.value = value;
            stars.forEach(s => {
                s.classList.toggle('fa-solid', parseInt(s.dataset.value, 10) <= value);
                s.classList.toggle('fa-regular', parseInt(s.dataset.value, 10) > value);
            });
        });
    });
}
document.addEventListener('DOMContentLoaded', initStarRating);
