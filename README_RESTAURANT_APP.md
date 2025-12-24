# Restaurant Reviews Map

An interactive web application that displays restaurant reviews from popular food YouTubers on an interactive map.

## Features

- **Interactive Map**: Browse restaurants on an interactive Leaflet map centered on New York City
- **YouTuber Reviews**: All reviews curated from "The Food Ranger" (customizable)
- **Smart Search**: Search restaurants by name, cuisine, highlights, or location
- **Cuisine Filters**: Filter by cuisine type (Italian, Japanese, American, Mexican, Asian)
- **Detailed Reviews**: Each restaurant includes comprehensive review summaries and highlights
- **Rating System**: Visual star ratings and color-coded map markers
- **Responsive Design**: Works beautifully on desktop, tablet, and mobile devices
- **Interactive Sidebar**: Browse restaurants in list view with quick navigation
- **Statistics Dashboard**: View total restaurants, average rating, and total reviews

## How to Use

### Opening the Application

Simply open `restaurant_map.html` in any modern web browser:

```bash
# Using Python's built-in server
python3 -m http.server 8000

# Or just open the file directly
open restaurant_map.html  # macOS
xdg-open restaurant_map.html  # Linux
start restaurant_map.html  # Windows
```

Then navigate to `http://localhost:8000/restaurant_map.html` in your browser.

### Navigation

1. **Map View**:
   - Click on any marker to see restaurant details
   - Colored markers indicate rating level (Green: 4.8+, Blue: 4.5+, Orange: 4.0+)
   - Zoom and pan to explore different areas

2. **Sidebar**:
   - Click any restaurant card to focus on it on the map
   - Scroll through the list to browse all restaurants
   - Cards highlight when selected

3. **Search**:
   - Type in the search box to filter restaurants
   - Search works across names, cuisines, highlights, and addresses
   - Use Ctrl/Cmd + F to quickly focus the search box

4. **Filters**:
   - Click cuisine buttons to filter by type
   - Click "All" to reset filters
   - Combine with search for refined results

## File Structure

```
LegaleApp/
├── restaurant_map.html    # Main HTML interface
├── restaurant_data.js     # Restaurant data and reviews
├── app.js                # Application logic and interactivity
└── README_RESTAURANT_APP.md  # This file
```

## Customization

### Adding Your Own Restaurants

Edit `restaurant_data.js` and add new entries to the `restaurantData` array:

```javascript
{
    id: 13,
    name: "Your Restaurant Name",
    cuisine: "Italian", // or Japanese, American, Mexican, Asian
    lat: 40.7589,  // Latitude
    lng: -73.9851, // Longitude
    rating: 4.8,
    youtuber: "Your YouTuber Name",
    videoUrl: "https://youtube.com/watch?v=...",
    reviewDate: "2024-12-24",
    summary: "Your review summary...",
    highlights: ["Highlight 1", "Highlight 2", "Highlight 3"],
    priceRange: "$$", // $, $$, or $$$
    address: "Full address"
}
```

### Changing the YouTuber

Simply update the `youtuber` field in each restaurant entry in `restaurant_data.js`.

### Adding New Cuisine Types

1. Add new filter button in `restaurant_map.html`:
```html
<button class="filter-btn" data-cuisine="French">French</button>
```

2. Add restaurants with `cuisine: "French"` in `restaurant_data.js`

### Changing the Map Location

In `app.js`, modify the `initMap()` function:

```javascript
map = L.map('map').setView([YOUR_LAT, YOUR_LNG], ZOOM_LEVEL);
```

## Technologies Used

- **Leaflet.js**: Interactive maps
- **OpenStreetMap**: Map tiles
- **Vanilla JavaScript**: Application logic
- **CSS3**: Styling and animations
- **HTML5**: Structure

## Features in Detail

### Restaurant Data Structure

Each restaurant includes:
- Name and cuisine type
- GPS coordinates for map placement
- Rating (out of 5.0)
- YouTuber name and video URL
- Review date
- Detailed summary (full review text)
- Highlights (key features)
- Price range indicator
- Full address

### Interactive Elements

- **Hover Effects**: Cards and buttons respond to mouse hover
- **Click Actions**: Click restaurants to focus on map
- **Smooth Animations**: Transitions and scroll behavior
- **Real-time Filtering**: Instant results as you type or filter
- **Dynamic Statistics**: Stats update based on current filter

### Mobile Responsive

The layout automatically adapts:
- Desktop: Side-by-side map and list
- Mobile: Stacked layout for better usability
- Touch-friendly: Large click targets and smooth scrolling

## Browser Compatibility

Works with all modern browsers:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Future Enhancements

Potential additions:
- Filter by rating range
- Sort options (rating, date, alphabetical)
- Export restaurant list
- Share specific restaurant links
- Dark mode toggle
- Multiple YouTuber support with toggle
- Distance calculator
- Directions integration
- User comments section

## License

Free to use and modify for personal and commercial projects.

## Credits

Created for restaurant review aggregation and mapping.
Map data © OpenStreetMap contributors.
