// Restaurant data from Franchino er criminale reviews
const restaurantData = [
    {
        id: 1,
        name: "Forno Ritorno",
        cuisine: "Panificio/Bakery",
        lat: 41.8779,
        lng: 12.4787,
        rating: 4.5,
        youtuber: "Franchino er criminale",
        videoUrl: "https://youtube.com/@franchinoercriminale",
        reviewDate: "2024-11-30",
        summary: "Nuovo forno stile anni 80 a Testaccio che riporta in auge il concetto di panificazione tradizionale romana. I dolci sono eccezionali (voto 9.5) - ciavattone, cornetto romano e veneziana incredibili. Il salato buono ma alcuni prodotti scarichi. Pizza bianca con mortadella €4.50 un po' cara con poca mortadella. I tramezzini ottimi ma prezzi leggermente alti. Un ritorno al passato fatto bene, soprattutto per i dolci artigianali.",
        highlights: ["Ciavattone alla crema TOP", "Cornetto romano buonissimo", "Veneziana eccezionale", "Sfoglia incredibile", "Tramezzino pane artigianale"],
        priceRange: "€€",
        address: "Via Amerigo Vespucci 20, Testaccio, Roma",
        details: {
            itemsReviewed: [
                "Pizza bianca con mortadella €4.50 - buona ma poca mortadella",
                "Panino lingua e salsa verde €6.50 - ottimo, ben riempito",
                "Tramezzino insalata russa €3.50 - 8.5/9 se costasse €3",
                "Tramezzino insalata di pollo €3.50 - buono ma scarico",
                "Ciavattone alla crema €3 - buonissimo, tra i migliori",
                "Cornetto romano €2 - piccolo ma clamoroso",
                "Veneziana €3 - spettacolare",
                "Maritozzo con panna €3 - buono"
            ],
            totalSpent: "€29",
            strengths: "Dolci da 9.5, sfoglia incredibile, prodotti artigianali",
            weaknesses: "Prezzi 50 cent troppo alti, salato un po' scarico"
        }
    },
    {
        id: 2,
        name: "Forno Lana",
        cuisine: "Panificio/Bakery",
        lat: 41.8547,
        lng: 12.5234,
        rating: 4.5,
        youtuber: "Franchino er criminale",
        videoUrl: "https://youtube.com/@franchinoercriminale",
        reviewDate: "2024-12-01",
        summary: "Forno ad Acilia che ha lasciato Franchino super soddisfatto. Le pizzette rosse sono quasi perfette (voto 9), croccanti che si sciolgono in bocca - solo il sugo andrebbe cotto meglio per arrivare al 10. La pizza rossa bassa e scrocchiarella è una HIT assoluta, 'campione del mondo'. Pizza bianca con mortadella abbondante e buona. Dolcetto ricotta e visciole ottimo. Un forno che vale assolutamente il viaggio.",
        highlights: ["Pizzette rosse da 9", "Pizza rossa HIT campione del mondo", "Pizza bianca mortadella abbondante", "Dolce ricotta visciole", "Impasto croccante"],
        priceRange: "€€",
        address: "Via Zottoli 14, Acilia, Roma",
        details: {
            itemsReviewed: [
                "Dolcetto ricotta e visciole - buonissimo, ancora caldo",
                "Pizza con le patate - buona, 8/10",
                "Pizza bianca con mortadella - ottima, abbondante",
                "Pizzette rosse - 9/10, croccanti che si sciolgono",
                "Pizza rossa scrocchiarella - HIT, quasi 10"
            ],
            totalSpent: "€12.46",
            strengths: "Pizzette eccezionali, pizza rossa top, mortadella abbondante",
            weaknesses: "Sugo pomodoro da cuocere meglio (unico difetto)"
        }
    },
    {
        id: 3,
        name: "Le Gemme di Grano",
        cuisine: "Panificio/Bakery",
        lat: 41.8423,
        lng: 12.5189,
        rating: 4.3,
        youtuber: "Franchino er criminale",
        videoUrl: "https://youtube.com/@franchinoercriminale",
        reviewDate: "2024-12-01",
        summary: "Forno fighetto ad Axa con locale tutto nuovo e stiloso. Fanno anche rosticceria oltre al forno. La montanarina fritta molto buona (8.5), pizza rossa 8.5, pizza bianca buona con olio di qualità. Le pizzette rosse un po' mosce col sugo crudo. Prodotti di buona qualità ma non eccezionali come altri forni. Locale bello, prodotti curati, prezzi in linea. Un buon forno di quartiere che serve bene la zona.",
        highlights: ["Montanarina fritta buonissima", "Olio di qualità", "Pizza rossa 8.5", "Locale stiloso", "Anche rosticceria"],
        priceRange: "€€",
        address: "Via di Macchia Saponara 148, Axa, Roma",
        details: {
            itemsReviewed: [
                "Pizzette rosse - buone ma mosce, sugo un po' crudo",
                "Pizzetta con patate - molto buona, ben condita",
                "Pizza bianca - buona, molto salata (pregio), olio ottimo",
                "Pizza rossa - 8.5, molto buona",
                "Montanarina fritta - 8.5, buonissima",
                "Pangoccioli - buoni"
            ],
            totalSpent: "€11",
            strengths: "Montanarina top, olio buono, anche rosticceria",
            weaknesses: "Alcune pizzette mosce, prodotti non eccezionali"
        }
    },
    {
        id: 4,
        name: "Spiga d'Oro Bakery",
        cuisine: "Panificio/Bakery",
        lat: 41.8501,
        lng: 12.5267,
        rating: 4.5,
        youtuber: "Franchino er criminale",
        videoUrl: "https://youtube.com/@franchinoercriminale",
        reviewDate: "2024-12-01",
        summary: "Forno ad Acilia che fa anche rosticceria con la particolarità di fare le paste GRANDI come una volta, non i mignon moderni. I dolci sono buonissimi (voto 9+) - bigné con zabaglione e diplomatico eccezionali, un ritorno agli anni 90. La focaccia barese con verdure è molto buona (9-), ben condita con olio buono. Pizza bianca ottima ma poca mortadella. Il posto che la gente di Acilia consigliava come HIT e in effetti lo è.",
        highlights: ["Paste grandi tradizionali", "Bigné zabaglione 9+", "Diplomatico 9+", "Focaccia barese 9-", "Dolci anni 90"],
        priceRange: "€€",
        address: "Via Umberto Lilloni 62, Acilia, Roma",
        details: {
            itemsReviewed: [
                "Pizza rossa - 8.5, buona, croccante",
                "Focaccia barese verdure - 9-, condita divinamente",
                "Pizza bianca mortadella - 8.5, ottima pizza ma poca mortadella",
                "Bigné zabaglione - 9+, buonissimo",
                "Diplomatico - 9+, eccezionale"
            ],
            totalSpent: "€15.40",
            strengths: "Dolci eccezionali, paste grandi tradizionali, focaccia top",
            weaknesses: "Pizza bianca con poca mortadella"
        }
    },
    {
        id: 5,
        name: "Romanè al Banco",
        cuisine: "Rosticceria Romana",
        lat: 41.8736,
        lng: 12.4769,
        rating: 5.0,
        youtuber: "Franchino er criminale",
        videoUrl: "https://youtube.com/@franchinoercriminale",
        reviewDate: "2024-12-15",
        summary: "Rosticceria aperta da Stefano Callegari (inventore del trapizzino, proprietario di Romanè) vicino a Bonci. VOTO 10/10. La fettina panata è PERFETTA - panatura illegale, frittura perfetta. Crocchetta di patate da 10. Lasagna romana tradizionale buonissima (€18/kg, porzione €4-4.50). Supplì eccezionali. Costine con finocchietto selvatico top. Tutto fatto in maniera tradizionale ma con qualità altissima. Stefano con umiltà dice 'ho aperto la rosticceria e ho ricominciato a imparare'. Il meglio della rosticceria romana.",
        highlights: ["Fettina panata PERFETTA 10/10", "Crocchetta patate 10/10", "Lasagna romana tradizionale", "Supplì eccezionali", "Costine finocchietto", "Stefano Callegari"],
        priceRange: "€€",
        address: "Via Ostiense (vicino Bonci), Roma",
        details: {
            itemsReviewed: [
                "Lasagna romana - eccezionale, €18/kg (porzione €4-4.50)",
                "Supplì classico €3 - ottimo",
                "Supplì tortellino €3 - ottimo",
                "Crocchetta di patate €2.50 - 10/10 PERFETTA",
                "Fettina panata - 10/10 PERFETTA, panatura illegale",
                "Costine con finocchietto - top",
                "Pollo arrosto - eccellente",
                "Focaccia - ottima",
                "Trippa e pajata disponibili"
            ],
            totalSpent: "€34 (con €6 di Coca-Cole)",
            strengths: "TUTTO PERFETTO - rosticceria da 10, Stefano Callegari, tradizione + qualità",
            weaknesses: "Nessuno - voto 10"
        }
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
