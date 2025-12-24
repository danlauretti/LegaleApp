// Initialize the map
let map;
let markers = [];
let currentFilter = 'all';
let searchTerm = '';

// Initialize map when page loads
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    displayStats();
    displayRestaurants(restaurantData);
    setupEventListeners();
});

function initMap() {
    // Initialize map centered on New York City
    map = L.map('map').setView([40.7489, -73.9680], 12);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
    }).addTo(map);

    // Add all restaurant markers
    addMarkers(restaurantData);
}

function addMarkers(restaurants) {
    // Clear existing markers
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];

    // Add new markers
    restaurants.forEach(restaurant => {
        // Create custom icon based on rating
        const iconColor = getIconColor(restaurant.rating);
        const icon = L.divIcon({
            className: 'custom-marker',
            html: `<div style="background-color: ${iconColor}; width: 30px; height: 30px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; font-size: 14px;">${restaurant.rating}</div>`,
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });

        // Create marker
        const marker = L.marker([restaurant.lat, restaurant.lng], { icon: icon })
            .addTo(map)
            .bindPopup(createPopupContent(restaurant));

        // Add click event to marker
        marker.on('click', function() {
            highlightRestaurant(restaurant.id);
        });

        markers.push(marker);
    });
}

function getIconColor(rating) {
    if (rating >= 4.8) return '#10b981'; // Green for excellent
    if (rating >= 4.5) return '#3b82f6'; // Blue for very good
    if (rating >= 4.0) return '#f59e0b'; // Orange for good
    return '#ef4444'; // Red for average
}

function createPopupContent(restaurant) {
    const stars = '⭐'.repeat(Math.round(restaurant.rating));

    return `
        <div class="custom-popup" style="min-width: 250px;">
            <div class="youtuber-badge" style="display: inline-flex; align-items: center; gap: 5px; padding: 5px 12px; background: #ff0000; color: white; border-radius: 15px; font-size: 0.85em; font-weight: 600; margin-bottom: 10px;">
                📺 ${restaurant.youtuber}
            </div>
            <h3 style="color: #667eea; margin-bottom: 10px; font-size: 1.3em;">${restaurant.name}</h3>
            <div class="popup-rating" style="color: #ffc107; font-size: 1.1em; margin: 5px 0;">
                ${stars} ${restaurant.rating}
            </div>
            <p style="margin: 5px 0; color: #6c757d;"><strong>Cuisine:</strong> ${restaurant.cuisine}</p>
            <p style="margin: 5px 0; color: #6c757d;"><strong>Price:</strong> ${restaurant.priceRange}</p>
            <p style="margin: 5px 0; color: #6c757d;"><strong>Location:</strong> ${restaurant.address}</p>
            <div class="popup-summary" style="margin: 10px 0; color: #495057; line-height: 1.5; max-height: 100px; overflow-y: auto;">
                <strong>Review:</strong> ${restaurant.summary.substring(0, 150)}...
            </div>
            <div style="margin-top: 10px;">
                <strong style="color: #495057;">Highlights:</strong><br>
                ${restaurant.highlights.map(h => `<span style="display: inline-block; padding: 3px 10px; background: #e9ecef; border-radius: 10px; font-size: 0.8em; margin: 3px;">${h}</span>`).join('')}
            </div>
        </div>
    `;
}

function displayStats() {
    const stats = calculateStats();
    document.getElementById('totalRestaurants').textContent = stats.total;
    document.getElementById('avgRating').textContent = stats.avgRating + ' ⭐';
    document.getElementById('totalReviews').textContent = stats.totalReviews;
}

function displayRestaurants(restaurants) {
    const listContainer = document.getElementById('restaurantList');

    if (restaurants.length === 0) {
        listContainer.innerHTML = '<div class="loading">No restaurants found matching your criteria.</div>';
        return;
    }

    listContainer.innerHTML = restaurants.map(restaurant => `
        <div class="restaurant-card" data-id="${restaurant.id}" onclick="focusOnRestaurant(${restaurant.id})">
            <div class="youtuber-badge">📺 ${restaurant.youtuber}</div>
            <h3>${restaurant.name}</h3>
            <div class="rating">
                <span class="stars">${'⭐'.repeat(Math.round(restaurant.rating))}</span>
                <span class="rating-value">${restaurant.rating}/5.0</span>
            </div>
            <div>
                <span class="cuisine-tag">${restaurant.cuisine}</span>
                <span class="cuisine-tag">${restaurant.priceRange}</span>
            </div>
            <div class="summary">
                <strong>📍</strong> ${restaurant.address}<br>
                <strong>📅</strong> Reviewed: ${new Date(restaurant.reviewDate).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}<br><br>
                ${restaurant.summary}
            </div>
            <div style="margin-top: 10px;">
                ${restaurant.highlights.map(h => `<span class="cuisine-tag">${h}</span>`).join('')}
            </div>
        </div>
    `).join('');
}

function focusOnRestaurant(id) {
    const restaurant = restaurantData.find(r => r.id === id);
    if (restaurant) {
        // Pan and zoom to restaurant
        map.setView([restaurant.lat, restaurant.lng], 15);

        // Find and open the marker popup
        const marker = markers.find(m => {
            const latlng = m.getLatLng();
            return latlng.lat === restaurant.lat && latlng.lng === restaurant.lng;
        });

        if (marker) {
            marker.openPopup();
        }

        highlightRestaurant(id);
    }
}

function highlightRestaurant(id) {
    // Remove previous highlights
    document.querySelectorAll('.restaurant-card').forEach(card => {
        card.style.borderColor = 'transparent';
    });

    // Highlight selected card
    const card = document.querySelector(`[data-id="${id}"]`);
    if (card) {
        card.style.borderColor = '#667eea';
        card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

function setupEventListeners() {
    // Search functionality
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', function(e) {
        searchTerm = e.target.value.toLowerCase();
        filterRestaurants();
    });

    // Filter buttons
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Update active state
            filterButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            // Update filter
            currentFilter = this.getAttribute('data-cuisine');
            filterRestaurants();
        });
    });
}

function filterRestaurants() {
    let filtered = restaurantData;

    // Apply cuisine filter
    if (currentFilter !== 'all') {
        filtered = filtered.filter(r => r.cuisine === currentFilter);
    }

    // Apply search filter
    if (searchTerm) {
        filtered = filtered.filter(r =>
            r.name.toLowerCase().includes(searchTerm) ||
            r.cuisine.toLowerCase().includes(searchTerm) ||
            r.summary.toLowerCase().includes(searchTerm) ||
            r.highlights.some(h => h.toLowerCase().includes(searchTerm)) ||
            r.address.toLowerCase().includes(searchTerm)
        );
    }

    // Update display
    displayRestaurants(filtered);
    addMarkers(filtered);

    // Update stats for filtered results
    if (filtered.length > 0) {
        const avgRating = (filtered.reduce((sum, r) => sum + r.rating, 0) / filtered.length).toFixed(1);
        document.getElementById('totalRestaurants').textContent = filtered.length;
        document.getElementById('avgRating').textContent = avgRating + ' ⭐';
        document.getElementById('totalReviews').textContent = filtered.length;
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Focus search on Ctrl/Cmd + F
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        document.getElementById('searchInput').focus();
    }
});
