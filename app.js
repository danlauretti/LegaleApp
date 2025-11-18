// Initialize the map centered on Rome
const map = L.map('map').setView([41.9028, 12.4964], 12);

// Add tile layer (OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Custom marker icon
const createCustomIcon = (rating) => {
    const color = rating >= 4.7 ? '#DC143C' : rating >= 4.5 ? '#FF6347' : '#FF8C00';

    return L.divIcon({
        className: 'custom-marker',
        html: `
            <div style="
                background-color: ${color};
                width: 30px;
                height: 30px;
                border-radius: 50% 50% 50% 0;
                transform: rotate(-45deg);
                border: 3px solid #ffffff;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                <span style="
                    transform: rotate(45deg);
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                ">★</span>
            </div>
        `,
        iconSize: [30, 42],
        iconAnchor: [15, 42],
        popupAnchor: [0, -42]
    });
};

// Store markers for reference
const markers = {};

// Generate star rating HTML
const generateStars = (rating) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    let starsHtml = '';

    for (let i = 0; i < fullStars; i++) {
        starsHtml += '★';
    }
    if (hasHalfStar) {
        starsHtml += '½';
    }

    return starsHtml;
};

// Create popup content for a restaurant
const createPopupContent = (restaurant) => {
    return `
        <div class="popup-content">
            <h3>${restaurant.name}</h3>
            <span class="category">${restaurant.categoryLabel}</span>
            <div class="rating">
                <span class="stars">${generateStars(restaurant.rating)}</span>
                <strong>${restaurant.rating}</strong>
            </div>
            <p class="address">${restaurant.address}</p>
            <p class="quote">"${restaurant.quote}"</p>
        </div>
    `;
};

// Create restaurant card HTML
const createRestaurantCard = (restaurant) => {
    return `
        <div class="restaurant-card" data-id="${restaurant.id}">
            <h3 class="restaurant-name">${restaurant.name}</h3>
            <span class="restaurant-category">${restaurant.categoryLabel}</span>
            <div class="restaurant-rating">
                <span class="stars">${generateStars(restaurant.rating)}</span>
                <span class="rating-value">${restaurant.rating}</span>
            </div>
            <p class="restaurant-address">${restaurant.address}</p>
            <p class="restaurant-quote">"${restaurant.quote}"</p>
        </div>
    `;
};

// Add markers to the map
const addMarkers = (restaurantList) => {
    // Clear existing markers
    Object.values(markers).forEach(marker => map.removeLayer(marker));

    restaurantList.forEach(restaurant => {
        const marker = L.marker([restaurant.lat, restaurant.lng], {
            icon: createCustomIcon(restaurant.rating)
        }).addTo(map);

        marker.bindPopup(createPopupContent(restaurant));

        // Store marker reference
        markers[restaurant.id] = marker;

        // Add click handler
        marker.on('click', () => {
            highlightCard(restaurant.id);
        });
    });
};

// Render restaurant list in sidebar
const renderRestaurantList = (restaurantList) => {
    const listContainer = document.getElementById('restaurantList');

    if (restaurantList.length === 0) {
        listContainer.innerHTML = `
            <div class="no-results">
                <p>Nessun ristorante trovato</p>
                <p>Prova a modificare i filtri</p>
            </div>
        `;
        return;
    }

    listContainer.innerHTML = restaurantList.map(createRestaurantCard).join('');

    // Add click handlers to cards
    document.querySelectorAll('.restaurant-card').forEach(card => {
        card.addEventListener('click', () => {
            const id = parseInt(card.dataset.id);
            const restaurant = restaurants.find(r => r.id === id);

            if (restaurant && markers[id]) {
                // Pan to marker and open popup
                map.setView([restaurant.lat, restaurant.lng], 15);
                markers[id].openPopup();

                // Highlight the card
                highlightCard(id);
            }
        });
    });
};

// Highlight a card in the sidebar
const highlightCard = (id) => {
    // Remove active class from all cards
    document.querySelectorAll('.restaurant-card').forEach(card => {
        card.classList.remove('active');
    });

    // Add active class to selected card
    const selectedCard = document.querySelector(`.restaurant-card[data-id="${id}"]`);
    if (selectedCard) {
        selectedCard.classList.add('active');
        selectedCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
};

// Filter restaurants
const filterRestaurants = () => {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const categoryFilter = document.getElementById('categoryFilter').value;

    let filtered = restaurants;

    // Apply search filter
    if (searchTerm) {
        filtered = filtered.filter(r =>
            r.name.toLowerCase().includes(searchTerm) ||
            r.address.toLowerCase().includes(searchTerm) ||
            r.specialties.some(s => s.toLowerCase().includes(searchTerm))
        );
    }

    // Apply category filter
    if (categoryFilter !== 'all') {
        filtered = filtered.filter(r => r.category === categoryFilter);
    }

    // Update map and list
    addMarkers(filtered);
    renderRestaurantList(filtered);

    // Fit bounds to show all markers if there are results
    if (filtered.length > 0) {
        const bounds = L.latLngBounds(filtered.map(r => [r.lat, r.lng]));
        map.fitBounds(bounds, { padding: [50, 50] });
    }
};

// Initialize the app
const init = () => {
    // Add markers to map
    addMarkers(restaurants);

    // Render restaurant list
    renderRestaurantList(restaurants);

    // Set up event listeners
    document.getElementById('searchInput').addEventListener('input', filterRestaurants);
    document.getElementById('categoryFilter').addEventListener('change', filterRestaurants);

    // Fit map to show all markers
    const bounds = L.latLngBounds(restaurants.map(r => [r.lat, r.lng]));
    map.fitBounds(bounds, { padding: [50, 50] });
};

// Run initialization when DOM is ready
document.addEventListener('DOMContentLoaded', init);
