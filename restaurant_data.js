// Restaurant data with YouTuber reviews
const restaurantData = [
    {
        id: 1,
        name: "Mama's Italian Kitchen",
        cuisine: "Italian",
        lat: 40.7589,
        lng: -73.9851,
        rating: 4.8,
        youtuber: "The Food Ranger",
        videoUrl: "https://youtube.com/watch?v=example1",
        reviewDate: "2024-11-15",
        summary: "Absolutely incredible homemade pasta! The carbonara was creamy perfection, and the tiramisu transported me straight to Rome. The chef's grandmother's recipes shine through every dish. A must-visit for authentic Italian cuisine in the heart of the city.",
        highlights: ["Homemade Pasta", "Tiramisu", "Family Recipes", "Authentic Italian"],
        priceRange: "$$",
        address: "123 Broadway, New York, NY"
    },
    {
        id: 2,
        name: "Sakura Sushi House",
        cuisine: "Japanese",
        lat: 40.7614,
        lng: -73.9776,
        rating: 4.9,
        youtuber: "The Food Ranger",
        videoUrl: "https://youtube.com/watch?v=example2",
        reviewDate: "2024-10-28",
        summary: "This is hands down the best sushi I've had outside of Tokyo. The fish is incredibly fresh, melts in your mouth. The chef trained in Japan for 15 years and it shows. Try the omakase - it's an experience you won't forget. The presentation is art on a plate.",
        highlights: ["Fresh Sashimi", "Omakase Experience", "Master Chef", "Beautiful Presentation"],
        priceRange: "$$$",
        address: "456 Park Ave, New York, NY"
    },
    {
        id: 3,
        name: "BBQ King's Smokehouse",
        cuisine: "American",
        lat: 40.7489,
        lng: -73.9680,
        rating: 4.7,
        youtuber: "The Food Ranger",
        videoUrl: "https://youtube.com/watch?v=example3",
        reviewDate: "2024-12-01",
        summary: "The brisket here is legendary! Smoked for 16 hours, it's so tender it falls apart. The ribs are perfectly charred with a sweet and tangy sauce. Portions are massive - come hungry! The mac and cheese side is creamy heaven. Real Texas-style BBQ in NYC.",
        highlights: ["16-Hour Brisket", "Fall-off-bone Ribs", "Homemade Sauces", "Generous Portions"],
        priceRange: "$$",
        address: "789 E 34th St, New York, NY"
    },
    {
        id: 4,
        name: "Taco Fiesta",
        cuisine: "Mexican",
        lat: 40.7282,
        lng: -73.9942,
        rating: 4.6,
        youtuber: "The Food Ranger",
        videoUrl: "https://youtube.com/watch?v=example4",
        reviewDate: "2024-11-20",
        summary: "Street-style tacos that taste like they're straight from Mexico City! The al pastor is marinated to perfection with pineapple that caramelizes beautifully. Fresh handmade tortillas, authentic salsas with real kick. Don't sleep on the elote - best corn I've ever had!",
        highlights: ["Al Pastor Tacos", "Handmade Tortillas", "Authentic Salsas", "Street Corn"],
        priceRange: "$",
        address: "234 Lafayette St, New York, NY"
    },
    {
        id: 5,
        name: "Dragon Wok",
        cuisine: "Asian",
        lat: 40.7178,
        lng: -74.0059,
        rating: 4.5,
        youtuber: "The Food Ranger",
        videoUrl: "https://youtube.com/watch?v=example5",
        reviewDate: "2024-11-05",
        summary: "Szechuan cuisine done right! The mapo tofu has that numbing spice that's addictive. Kung pao chicken is loaded with peanuts and has incredible wok hei (breath of the wok). The dan dan noodles are silky smooth with a complex sauce. Spice lovers paradise!",
        highlights: ["Mapo Tofu", "Wok Hei", "Dan Dan Noodles", "Authentic Szechuan"],
        priceRange: "$$",
        address: "567 Canal St, New York, NY"
    },
    {
        id: 6,
        name: "Bella Napoli",
        cuisine: "Italian",
        lat: 40.7308,
        lng: -73.9973,
        rating: 4.9,
        youtuber: "The Food Ranger",
        videoUrl: "https://youtube.com/watch?v=example6",
        reviewDate: "2024-10-15",
        summary: "Wood-fired pizza perfection! The crust is charred and chewy with that perfect leopard spotting. Simple ingredients but the quality shines through - San Marzano tomatoes, buffalo mozzarella, fresh basil. The Margherita is a masterpiece. Feels like eating in Naples.",
        highlights: ["Wood-fired Pizza", "Neapolitan Style", "Fresh Mozzarella", "Leopard Spotted Crust"],
        priceRange: "$$",
        address: "890 Bleecker St, New York, NY"
    },
    {
        id: 7,
        name: "Ramen Haven",
        cuisine: "Japanese",
        lat: 40.7580,
        lng: -73.9855,
        rating: 4.7,
        youtuber: "The Food Ranger",
        videoUrl: "https://youtube.com/watch?v=example7",
        reviewDate: "2024-12-10",
        summary: "Rich, creamy tonkotsu broth that's been simmering for 20 hours. The pork belly chashu melts in your mouth, perfectly soft-boiled egg, and noodles with ideal texture. On a cold day, this bowl of ramen is pure comfort. The garlic oil adds an amazing depth of flavor.",
        highlights: ["20-Hour Tonkotsu", "Melt-in-mouth Chashu", "Perfect Eggs", "Rich Broth"],
        priceRange: "$$",
        address: "345 W 50th St, New York, NY"
    },
    {
        id: 8,
        name: "The Burger Joint",
        cuisine: "American",
        lat: 40.7614,
        lng: -73.9819,
        rating: 4.8,
        youtuber: "The Food Ranger",
        videoUrl: "https://youtube.com/watch?v=example8",
        reviewDate: "2024-11-25",
        summary: "Classic American burger done to perfection. Juicy double patty, melted cheese, crispy bacon, all in a toasted brioche bun. The secret sauce is tangy and addictive. Fries are crispy outside, fluffy inside. Thick milkshakes complete the experience. Pure nostalgia!",
        highlights: ["Double Patty", "Secret Sauce", "Crispy Fries", "Thick Milkshakes"],
        priceRange: "$$",
        address: "678 5th Ave, New York, NY"
    },
    {
        id: 9,
        name: "Casa Mexicana",
        cuisine: "Mexican",
        lat: 40.7489,
        lng: -73.9680,
        rating: 4.6,
        youtuber: "The Food Ranger",
        videoUrl: "https://youtube.com/watch?v=example9",
        reviewDate: "2024-10-20",
        summary: "Enchiladas smothered in mole sauce that takes 3 days to make with 30+ ingredients. The complexity of flavors is incredible - chocolate, chilies, spices all balanced perfectly. Guacamole made tableside with perfectly ripe avocados. Margaritas are dangerously good!",
        highlights: ["3-Day Mole Sauce", "Tableside Guacamole", "Craft Margaritas", "Authentic Enchiladas"],
        priceRange: "$$",
        address: "901 Amsterdam Ave, New York, NY"
    },
    {
        id: 10,
        name: "Dim Sum Palace",
        cuisine: "Asian",
        lat: 40.7155,
        lng: -74.0095,
        rating: 4.7,
        youtuber: "The Food Ranger",
        videoUrl: "https://youtube.com/watch?v=example10",
        reviewDate: "2024-12-05",
        summary: "Traditional dim sum with carts rolling by - the authentic experience! Har gow (shrimp dumplings) are translucent perfection, char siu bao buns are fluffy clouds, and the egg tarts have buttery flaky pastry. Come early for the freshest selection. Tea service is impeccable.",
        highlights: ["Cart Service", "Har Gow", "Char Siu Bao", "Egg Tarts"],
        priceRange: "$",
        address: "432 Mott St, New York, NY"
    },
    {
        id: 11,
        name: "Trattoria Romano",
        cuisine: "Italian",
        lat: 40.7489,
        lng: -73.9680,
        rating: 4.8,
        youtuber: "The Food Ranger",
        videoUrl: "https://youtube.com/watch?v=example11",
        reviewDate: "2024-11-10",
        summary: "Osso buco that falls off the bone, served with creamy risotto Milanese. The gremolata on top adds a fresh citrus kick. Wine selection is extensive with great Italian vintages. Panna cotta for dessert is silky smooth. Feels like dining in a Roman trattoria.",
        highlights: ["Osso Buco", "Risotto Milanese", "Italian Wines", "Panna Cotta"],
        priceRange: "$$$",
        address: "123 Mulberry St, New York, NY"
    },
    {
        id: 12,
        name: "Koji's Izakaya",
        cuisine: "Japanese",
        lat: 40.7282,
        lng: -73.9942,
        rating: 4.6,
        youtuber: "The Food Ranger",
        videoUrl: "https://youtube.com/watch?v=example12",
        reviewDate: "2024-12-15",
        summary: "Authentic Japanese pub experience! Yakitori is grilled to perfection - try the chicken skin, it's crispy and addictive. Takoyaki balls are crispy outside, gooey inside with real octopus chunks. Great sake selection. Perfect spot for late night food and drinks.",
        highlights: ["Grilled Yakitori", "Crispy Takoyaki", "Sake Selection", "Late Night Spot"],
        priceRange: "$$",
        address: "789 E 9th St, New York, NY"
    }
];

// Calculate statistics
function calculateStats() {
    const total = restaurantData.length;
    const avgRating = (restaurantData.reduce((sum, r) => sum + r.rating, 0) / total).toFixed(1);
    const totalReviews = restaurantData.length;

    return {
        total,
        avgRating,
        totalReviews
    };
}
