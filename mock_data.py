"""
Rich mock dataset and realistic fallback generation engine for Demo Mode.
Skill Wallet Capstone Project 4.
"""

from typing import List, Dict, Any
from models import DestinationRecommendation, ActivitySlot, DayPlan, Itinerary, TripPreferences


# Curated destination recommendations matched by vibe
VIBE_DESTINATIONS: Dict[str, List[Dict[str, Any]]] = {
    "Beach": [
        {
            "city": "Bali",
            "country": "Indonesia",
            "match_score": 96,
            "vibe_tags": ["#TropicalBeaches", "#SurfingVibes", "#CliffsideSunsets", "#AffordableLuxury"],
            "weather_season": "Dry Season (May–Sep) • 28°C sunny with gentle sea breezes",
            "estimated_daily_usd": 65.0,
            "why_matched": "Matches your preference for coastal serenity with rich cultural arts, beach clubs, and ultra-affordable dining.",
            "highlights": ["Uluwatu Sunset Temple", "Canggu Beach & Surf Breaks", "Nusa Penida Day Trip", "Jimbaran Seafood BBQ"],
            "best_neighborhoods": ["Seminyak", "Canggu", "Uluwatu", "Sanur"],
        },
        {
            "city": "Barcelona",
            "country": "Spain",
            "match_score": 93,
            "vibe_tags": ["#MediterraneanVibes", "#BeachAndCulture", "#GothicQuarter", "#TapasCulture"],
            "weather_season": "Spring / Autumn (May–June, Sep–Oct) • 23°C pleasant coastal sun",
            "estimated_daily_usd": 140.0,
            "why_matched": "Combines golden Mediterranean sandy beaches with world-class Gaudí architecture and vibrant seaside promenades.",
            "highlights": ["Bogatell & Barceloneta Beach", "Gothic Quarter Tapas Bars", "Park Güell", "La Sagrada Família"],
            "best_neighborhoods": ["Barceloneta", "Poblenou", "El Born", "Eixample"],
        },
        {
            "city": "Phuket",
            "country": "Thailand",
            "match_score": 89,
            "vibe_tags": ["#IslandHopping", "#TurquoiseWaters", "#NightMarkets", "#BudgetParadise"],
            "weather_season": "High Season (Nov–Apr) • 30°C tropical sunshine and calm seas",
            "estimated_daily_usd": 55.0,
            "why_matched": "Ideal for beach lovers seeking crystal-clear lagoons, limestone karst boat trips, and flavorful street gastronomy.",
            "highlights": ["Kata Noi Beach", "Phi Phi Islands Ferry", "Old Phuket Town Heritage", "Big Buddha Viewpoint"],
            "best_neighborhoods": ["Kata", "Rawai", "Old Phuket Town", "Karon"],
        },
    ],
    "Mountains": [
        {
            "city": "Interlaken",
            "country": "Switzerland",
            "match_score": 97,
            "vibe_tags": ["#AlpinePeaks", "#GlacialLakes", "#JungfrauRegion", "#PanoramicTrains"],
            "weather_season": "Summer (June–Aug) for hiking, Winter for skiing • 18°C–22°C mountain breeze",
            "estimated_daily_usd": 240.0,
            "why_matched": "Breathtaking twin glacial lakes framed by the iconic Eiger, Mönch, and Jungfrau snowy alpine peaks.",
            "highlights": ["Jungfraujoch Top of Europe", "Harder Kulm Funicular", "Lake Brienz Steamboat", "Lauterbrunnen Waterfalls"],
            "best_neighborhoods": ["Interlaken Ost", "Unterseen", "Grindelwald", "Lauterbrunnen Valley"],
        },
        {
            "city": "Banff",
            "country": "Canada",
            "match_score": 94,
            "vibe_tags": ["#RockyMountains", "#TurquoiseLakes", "#WildlifeEncounters", "#AlpineTrekking"],
            "weather_season": "Summer (July–Sep) • 20°C crisp clear air and emerald waters",
            "estimated_daily_usd": 180.0,
            "why_matched": "Unspoiled Canadian Rocky wilderness with vibrant glacial lakes, hiking trails, and cozy alpine hot springs.",
            "highlights": ["Lake Louise Canoeing", "Moraine Lake Valley of Ten Peaks", "Banff Gondola", "Johnston Canyon Trail"],
            "best_neighborhoods": ["Banff Town Center", "Lake Louise Village", "Tunnel Mountain"],
        },
        {
            "city": "Manali",
            "country": "India",
            "match_score": 91,
            "vibe_tags": ["#HimalayanValleys", "#SnowCappedPeaks", "#CedarForests", "#ScenicPasses"],
            "weather_season": "Spring / Summer (Apr–June) • 16°C–22°C refreshing mountain climate",
            "estimated_daily_usd": 45.0,
            "why_matched": "A sanctuary nestled in the majestic Pir Panjal and Dhauladhar ranges offering scenic serenity and trekking.",
            "highlights": ["Solang Valley Adventure", "Rohtang Pass", "Old Manali Wooden Cafes", "Jogini Waterfall Hike"],
            "best_neighborhoods": ["Old Manali", "Vashisht", "Aleo", "Log Huts Area"],
        },
    ],
    "Cultural": [
        {
            "city": "Rome",
            "country": "Italy",
            "match_score": 98,
            "vibe_tags": ["#AncientRuins", "#VaticanMasterpieces", "#TrastevereDining", "#PiazzaLife"],
            "weather_season": "Spring (Apr–May) & Autumn (Sep–Oct) • 22°C golden sunshine",
            "estimated_daily_usd": 160.0,
            "why_matched": "An open-air living museum where every corner reveals 2,800 years of civilization, renaissance art, and culinary legacy.",
            "highlights": ["Colosseum & Roman Forum", "Vatican Museums & Sistine Chapel", "Pantheon & Piazza Navona", "Trastevere Al Fresco Dinner"],
            "best_neighborhoods": ["Centro Storico", "Trastevere", "Monti", "Prati"],
        },
        {
            "city": "Kyoto",
            "country": "Japan",
            "match_score": 96,
            "vibe_tags": ["#ZenTemples", "#BambooGroves", "#GeishaHeritage", "#TeaCeremonies"],
            "weather_season": "Spring Cherry Blossoms (Apr) & Autumn Foliage (Nov) • 18°C mild weather",
            "estimated_daily_usd": 135.0,
            "why_matched": "The cultural epicenter of imperial Japan featuring over 1,600 temples, serene rock gardens, and traditional kaiseki.",
            "highlights": ["Fushimi Inari Torii Shrine", "Kinkaku-ji Golden Pavilion", "Arashiyama Bamboo Forest", "Gion Historic Lantern Streets"],
            "best_neighborhoods": ["Gion", "Higashiyama", "Arashiyama", "Central Kyoto"],
        },
        {
            "city": "Jaipur",
            "country": "India",
            "match_score": 94,
            "vibe_tags": ["#PinkCity", "#RoyalPalaces", "#HandicraftBazaars", "#FortressViews"],
            "weather_season": "Winter (Oct–Mar) • 20°C–25°C pleasant sunny days and cool evenings",
            "estimated_daily_usd": 50.0,
            "why_matched": "Rajasthan's regal jewel boasting grandiose hilltop forts, pink terracotta walls, and sensory bazaar heritage.",
            "highlights": ["Amer Fort Elephant Pathway", "Hawa Mahal Palace of Winds", "City Palace & Jantar Mantar", "Nahargarh Fort Sunset Overlook"],
            "best_neighborhoods": ["Old Walled City", "C-Scheme", "Civil Lines", "Amer Foothills"],
        },
    ],
    "Urban": [
        {
            "city": "Tokyo",
            "country": "Japan",
            "match_score": 99,
            "vibe_tags": ["#FuturisticSkyline", "#MichelinDining", "#NeonNights", "#UltraModernTransit"],
            "weather_season": "Spring (Mar–May) & Autumn (Sep–Nov) • 19°C crisp and dry",
            "estimated_daily_usd": 145.0,
            "why_matched": "A hyper-efficient metropolis where ancient Shinto shrines coexist harmoniously with cyber-neon districts and izakayas.",
            "highlights": ["Shibuya Crossing & Sky", "teamLab Borderless Digital Art", "Shinjuku Omoide Yokocho", "Asakusa Senso-ji Temple"],
            "best_neighborhoods": ["Shinjuku", "Shibuya", "Ginza", "Asakusa"],
        },
        {
            "city": "New York City",
            "country": "USA",
            "match_score": 95,
            "vibe_tags": ["#BroadwayLights", "#IconicSkyline", "#WorldGastronomy", "#MuseumMile"],
            "weather_season": "Autumn (Sep–Nov) & Spring (May–June) • 18°C–22°C vibrant urban climate",
            "estimated_daily_usd": 250.0,
            "why_matched": "The quintessential global metropolis offering Broadway magic, endless world-class museums, and 24/7 culinary energy.",
            "highlights": ["Central Park & The Met", "Summit One Vanderbilt Skyline", "Brooklyn Bridge Walk", "West Village & High Line"],
            "best_neighborhoods": ["Manhattan Midtown", "Greenwich Village", "SoHo", "DUMBO Brooklyn"],
        },
        {
            "city": "Singapore",
            "country": "Singapore",
            "match_score": 92,
            "vibe_tags": ["#CityInAGarden", "#HawkerCenters", "#MarinaBaySkyline", "#FuturisticArchitecture"],
            "weather_season": "Year-round Tropical • 28°C–31°C warm with afternoon rain showers",
            "estimated_daily_usd": 175.0,
            "why_matched": "Impeccably clean garden city blending futuristic Supertree groves with Michelin-recognized hawker street culinary culture.",
            "highlights": ["Gardens by the Bay Cloud Forest", "Marina Bay Sands SkyPark", "Chinatown & Maxwell Food Centre", "Jewel Changi Vortex"],
            "best_neighborhoods": ["Marina Bay", "Chinatown", "Tiong Bahru", "Civic District"],
        },
    ],
}


# Pre-built rich curated itineraries for top destinations
CURATED_ITINERARIES: Dict[str, Dict[str, Any]] = {
    "paris": {
        "title": "Parisian Elegance & Iconic Heritage",
        "destination": "Paris",
        "country": "France",
        "days": [
            {
                "day_number": 1,
                "theme": "Monuments of the 7th & Historic Riverfront",
                "cluster_neighborhood": "7th Arrondissement & Eiffel Precinct",
                "daily_transit_overview": "All stops within 1.5 km of the Seine riverfront. Zero metro backtracking.",
                "transit_fatigue_score": "Low",
                "morning": {
                    "slot_id": "morning",
                    "slot_type": "Morning Sightseeing",
                    "time": "09:00 - 12:30",
                    "title": "Eiffel Tower Summit & Champ de Mars Stroll",
                    "description": "Pre-booked early access to the Eiffel Tower summit before crowds arrive. Descend through the manicured avenues of Champ de Mars for stunning photography angles.",
                    "neighborhood": "7th Arrondissement",
                    "estimated_cost_usd": 38.0,
                    "category": "Sightseeing",
                    "latitude": 48.8584,
                    "longitude": 2.2945,
                    "insider_tip": "Book 09:15 elevator slot to bypass the 90-minute general line.",
                },
                "lunch": {
                    "slot_id": "lunch",
                    "slot_type": "Lunch Recommendation",
                    "time": "12:30 - 14:00",
                    "title": "Bistrot Chez France - Authentic Rue Cler Brasserie",
                    "description": "Charming Parisian bistro serving classic duck confit, fresh baguettes, and goat cheese salad with outdoor wicker terrace seating.",
                    "neighborhood": "Rue Cler Market Street",
                    "estimated_cost_usd": 32.0,
                    "category": "Food",
                    "latitude": 48.8566,
                    "longitude": 2.3055,
                    "transit_from_previous": "🚶 10 min scenic walk via Avenue de la Bourdonnais",
                    "dietary_options": "Vegetarian quiche, Ratatouille, and fresh market salads available",
                    "insider_tip": "Request a street terrace table to enjoy people-watching along the pedestrian market.",
                },
                "afternoon": {
                    "slot_id": "afternoon",
                    "slot_type": "Afternoon Leisure & Culture",
                    "time": "14:30 - 17:30",
                    "title": "Musée de l'Armée & Les Invalides Dome",
                    "description": "Marvel at the golden dome of Hôtel des Invalides, Napoleon's tomb, and the expansive courtyard showcasing French military history and baroque architecture.",
                    "neighborhood": "Les Invalides",
                    "estimated_cost_usd": 17.0,
                    "category": "Culture",
                    "latitude": 48.8550,
                    "longitude": 2.3126,
                    "transit_from_previous": "🚶 8 min flat walk along Rue de Grenelle",
                    "insider_tip": "Enter from the Esplanade des Invalides side for an uncrowded security gate.",
                },
                "evening": {
                    "slot_id": "evening",
                    "slot_type": "Evening Dining & Entertainment",
                    "time": "18:30 - 22:00",
                    "title": "Seine Sunset Cruise & Latin Quarter Dinner",
                    "description": "Glide along the Seine as the city lights illuminate Notre-Dame and Pont Alexandre III, followed by a candlelit dinner in the historic Latin Quarter.",
                    "neighborhood": "Latin Quarter / Pont Neuf",
                    "estimated_cost_usd": 55.0,
                    "category": "Entertainment",
                    "latitude": 48.8530,
                    "longitude": 2.3499,
                    "transit_from_previous": "🚇 12 min direct via Metro Line 10 (La Tour-Maubourg to Cluny)",
                    "dietary_options": "Extensive wine list, French onion soup, Vegetarian truffle pasta",
                    "insider_tip": "Board the boat 20 mins before sunset to catch the golden hour transition into dusk.",
                },
            },
            {
                "day_number": 2,
                "theme": "Grand Artistry, Royal Gardens & Marais Boutiques",
                "cluster_neighborhood": "1st & 4th Arrondissements (Right Bank Core)",
                "daily_transit_overview": "Linear progression from Tuileries eastward to Place des Vosges. Minimal walking strain.",
                "transit_fatigue_score": "Low",
                "morning": {
                    "slot_id": "morning",
                    "slot_type": "Morning Sightseeing",
                    "time": "09:00 - 12:30",
                    "title": "Louvre Museum Masterpieces & Tuileries Garden",
                    "description": "Curated route through the Denon and Richelieu wings focusing on the Mona Lisa, Winged Victory of Samothrace, and Venus de Milo, followed by a stroll through Tuileries.",
                    "neighborhood": "1st Arrondissement",
                    "estimated_cost_usd": 24.0,
                    "category": "Culture",
                    "latitude": 48.8606,
                    "longitude": 2.3376,
                    "insider_tip": "Enter via the Carrousel du Louvre underground mall to skip the pyramid plaza queue.",
                },
                "lunch": {
                    "slot_id": "lunch",
                    "slot_type": "Lunch Recommendation",
                    "time": "12:30 - 14:00",
                    "title": "L'As du Fallafel - Famous Rue des Rosiers",
                    "description": "Legendary Middle Eastern culinary spot in the historic Jewish quarter known for crisp falafel pitas loaded with fried eggplant, tahini, and spicy red sauce.",
                    "neighborhood": "Le Marais",
                    "estimated_cost_usd": 15.0,
                    "category": "Food",
                    "latitude": 48.8575,
                    "longitude": 2.3592,
                    "transit_from_previous": "🚶 15 min pleasant stroll through Palais Royal gardens",
                    "dietary_options": "100% Certified Kosher & Vegan friendly",
                    "insider_tip": "Join the takeaway queue on the left; it moves three times faster than table dining.",
                },
                "afternoon": {
                    "slot_id": "afternoon",
                    "slot_type": "Afternoon Leisure & Culture",
                    "time": "14:30 - 17:30",
                    "title": "Place des Vosges & Le Marais Designer Boutiques",
                    "description": "Relax under the symmetric vaulted arcades of Paris's oldest planned royal square, visit Victor Hugo's historic residence, and explore concept art boutiques.",
                    "neighborhood": "Place des Vosges, 4th Arr.",
                    "estimated_cost_usd": 12.0,
                    "category": "Leisure",
                    "latitude": 48.8554,
                    "longitude": 2.3657,
                    "transit_from_previous": "🚶 6 min walk along Rue des Francs-Bourgeois",
                    "insider_tip": "Grab a salted butter caramel macaron from Carette on the northwest arcade.",
                },
                "evening": {
                    "slot_id": "evening",
                    "slot_type": "Evening Dining & Entertainment",
                    "time": "18:30 - 22:00",
                    "title": "Speakeasy Jazz & Natural Wine Bar Experience",
                    "description": "Sip natural organic French wines accompanied by artisanal cheese boards at a hidden cellar speakeasy featuring live acoustic jazz performers.",
                    "neighborhood": "Canal Saint-Martin / Oberkampf",
                    "estimated_cost_usd": 48.0,
                    "category": "Entertainment",
                    "latitude": 48.8647,
                    "longitude": 2.3695,
                    "transit_from_previous": "🚶 12 min walk north towards Boulevard Beaumarchais",
                    "dietary_options": "Artisanal dairy cheeses, vegan tapenade, gluten-free crackers",
                    "insider_tip": "Reservations recommended after 20:00 on weekends.",
                },
            },
            {
                "day_number": 3,
                "theme": "Bohemian Montmartre & Panoramic Vistas",
                "cluster_neighborhood": "18th Arrondissement (Montmartre Hill)",
                "daily_transit_overview": "Clustered entirely on Montmartre hill. One-way funicular ride avoids stair exhaustion.",
                "transit_fatigue_score": "Low",
                "morning": {
                    "slot_id": "morning",
                    "slot_type": "Morning Sightseeing",
                    "time": "09:00 - 12:30",
                    "title": "Sacré-Cœur Basilica & Secret Vineyard of Montmartre",
                    "description": "Ride the funicular to the Romano-Byzantine white stone basilica for the city's highest natural viewpoint, then wander past the quiet Clos Montmartre vineyard.",
                    "neighborhood": "Montmartre",
                    "estimated_cost_usd": 10.0,
                    "category": "Sightseeing",
                    "latitude": 48.8867,
                    "longitude": 2.3431,
                    "insider_tip": "Climb the 300 dome steps for a 360-degree panoramic vista stretching 30 km.",
                },
                "lunch": {
                    "slot_id": "lunch",
                    "slot_type": "Lunch Recommendation",
                    "time": "12:30 - 14:00",
                    "title": "Le Moulin de la Galette - Historic Windmill Bistro",
                    "description": "Dine beneath a preserved 17th-century wooden windmill immortalized by Renoir, indulging in beef bourguignon or mushroom risotto.",
                    "neighborhood": "Rue Lepic",
                    "estimated_cost_usd": 38.0,
                    "category": "Food",
                    "latitude": 48.8879,
                    "longitude": 2.3364,
                    "transit_from_previous": "🚶 7 min downhill amble past Place du Tertre",
                    "dietary_options": "Vegetarian truffle risotto, seasonal velouté soups",
                    "insider_tip": "Book an outdoor garden patio seat if the weather is clear.",
                },
                "afternoon": {
                    "slot_id": "afternoon",
                    "slot_type": "Afternoon Leisure & Culture",
                    "time": "14:30 - 17:30",
                    "title": "Musée de Montmartre & Renoir Gardens",
                    "description": "Step into the former studios of Pierre-Auguste Renoir, Suzanne Valadon, and Raoul Dufy overlooking the pastoral northern vineyard.",
                    "neighborhood": "Rue Cortot",
                    "estimated_cost_usd": 15.0,
                    "category": "Culture",
                    "latitude": 48.8878,
                    "longitude": 2.3406,
                    "transit_from_previous": "🚶 5 min cobbled walk through Rue Saint-Vincent",
                    "insider_tip": "The Renoir swing featured in his 1876 masterpiece is recreated in the garden.",
                },
                "evening": {
                    "slot_id": "evening",
                    "slot_type": "Evening Dining & Entertainment",
                    "time": "18:30 - 22:00",
                    "title": "Moulin Rouge Cabaret & Pigalle Nightlife",
                    "description": "Experience the world's most famous belle époque cabaret revue with champagne, acrobats, and the iconic French Cancan dance.",
                    "neighborhood": "South Pigalle (SoPi)",
                    "estimated_cost_usd": 110.0,
                    "category": "Entertainment",
                    "latitude": 48.8841,
                    "longitude": 2.3323,
                    "transit_from_previous": "🚶 10 min stroll down Rue Lepic past the Amélie cafe",
                    "dietary_options": "Gourmet champagne paired tasting menu with vegetarian options",
                    "insider_tip": "Smart dress code strictly enforced (jackets preferred, no sneakers or shorts).",
                },
            },
        ],
    },
    "tokyo": {
        "title": "Tokyo Neon Horizons & Imperial Serenity",
        "destination": "Tokyo",
        "country": "Japan",
        "days": [
            {
                "day_number": 1,
                "theme": "Historic Roots & Traditional Crafts",
                "cluster_neighborhood": "Taito Ward (Asakusa & Ueno)",
                "daily_transit_overview": "East Tokyo cluster. 1 metro stop or 15-minute walk between districts.",
                "transit_fatigue_score": "Low",
                "morning": {
                    "slot_id": "morning",
                    "slot_type": "Morning Sightseeing",
                    "time": "09:00 - 12:30",
                    "title": "Senso-ji Temple & Nakamise-dori Market",
                    "description": "Tokyo's oldest Buddhist temple founded in 645 AD. Pass beneath the giant red Kaminarimon thunder gate and browse Edo-period confectionery stalls.",
                    "neighborhood": "Asakusa",
                    "estimated_cost_usd": 8.0,
                    "category": "Culture",
                    "latitude": 35.7148,
                    "longitude": 139.7967,
                    "insider_tip": "Receive your fortune (omikuji) at the central incense burner pavilion.",
                },
                "lunch": {
                    "slot_id": "lunch",
                    "slot_type": "Lunch Recommendation",
                    "time": "12:30 - 14:00",
                    "title": "Daikokuya Tempura - Edo Style Crispy Prawns",
                    "description": "Operating since 1887, serving crispy sesame-fried tempura bowls drizzled in secret rich soy glaze over steaming rice.",
                    "neighborhood": "Asakusa Shoengai",
                    "estimated_cost_usd": 18.0,
                    "category": "Food",
                    "latitude": 35.7126,
                    "longitude": 139.7958,
                    "transit_from_previous": "🚶 3 min walk west of Senso-ji main hall",
                    "dietary_options": "Vegetable tempura bowls available on request",
                    "insider_tip": "The tatami second-floor room offers authentic seating without shoes.",
                },
                "afternoon": {
                    "slot_id": "afternoon",
                    "slot_type": "Afternoon Leisure & Culture",
                    "time": "14:30 - 17:30",
                    "title": "Ueno Park & Tokyo National Museum",
                    "description": "Explore Japan's largest art and samurai heritage museum showcasing ancient katana swords, lacquerware, and Kimono textiles within serene park grounds.",
                    "neighborhood": "Ueno Park",
                    "estimated_cost_usd": 12.0,
                    "category": "Culture",
                    "latitude": 35.7188,
                    "longitude": 139.7765,
                    "transit_from_previous": "🚇 5 min via Ginza Line from Asakusa to Ueno",
                    "insider_tip": "Check the Honkan Japanese Gallery first for the National Treasures collection.",
                },
                "evening": {
                    "slot_id": "evening",
                    "slot_type": "Evening Dining & Entertainment",
                    "time": "18:30 - 22:00",
                    "title": "Ameyoko Market Alleyways & Yakitori Izakaya",
                    "description": "Lively post-war market street under the elevated train tracks packed with sizzling yakitori skewers, draft Asahi beer, and vibrant street banter.",
                    "neighborhood": "Ameyokocho",
                    "estimated_cost_usd": 30.0,
                    "category": "Food",
                    "latitude": 35.7107,
                    "longitude": 139.7744,
                    "transit_from_previous": "🚶 4 min stroll down south exit of Ueno Station",
                    "dietary_options": "Shiitake mushroom skewers, grilled edamame, tofu dishes",
                    "insider_tip": "Sit at the outdoor red lantern tables directly beneath the train viaduct.",
                },
            },
            {
                "day_number": 2,
                "theme": "Youth Pop Culture & Neon Skylines",
                "cluster_neighborhood": "Shibuya & Harajuku District",
                "daily_transit_overview": "Walkable linear route from Meiji Shrine south through Harajuku into Shibuya.",
                "transit_fatigue_score": "Low",
                "morning": {
                    "slot_id": "morning",
                    "slot_type": "Morning Sightseeing",
                    "time": "09:00 - 12:30",
                    "title": "Meiji Jingu Shrine & Yoyogi Evergreen Forest",
                    "description": "Pass through towering 12-meter cedar Torii gates into a tranquil sacred forest of 100,000 trees planted in dedication to Emperor Meiji.",
                    "neighborhood": "Harajuku / Yoyogi",
                    "estimated_cost_usd": 5.0,
                    "category": "Culture",
                    "latitude": 35.6764,
                    "longitude": 139.6993,
                    "insider_tip": "Write a wooden prayer tablet (ema) to hang at the sacred camphor tree.",
                },
                "lunch": {
                    "slot_id": "lunch",
                    "slot_type": "Lunch Recommendation",
                    "time": "12:30 - 14:00",
                    "title": "Afuri Harajuku - Yuzu Citrus Ramen",
                    "description": "Light, refreshing golden broth infused with aromatic Japanese yuzu citrus fruit, charcoal-grilled chashu pork, and springy whole-grain noodles.",
                    "neighborhood": "Sendagaya / Harajuku",
                    "estimated_cost_usd": 14.0,
                    "category": "Food",
                    "latitude": 35.6713,
                    "longitude": 139.7042,
                    "transit_from_previous": "🚶 6 min walk from Harajuku station east exit",
                    "dietary_options": "Full Rainbow Vegan Ramen bowl with lotus root and vegetables",
                    "insider_tip": "Purchase your meal ticket at the automated vending machine at entrance.",
                },
                "afternoon": {
                    "slot_id": "afternoon",
                    "slot_type": "Afternoon Leisure & Culture",
                    "time": "14:30 - 17:30",
                    "title": "Takeshita Street & Cat Street Fashion Promenade",
                    "description": "Wander the colorful epicenter of kawaii fashion, quirky crepe stands, and vintage fashion boutiques leading along tree-shaded Cat Street.",
                    "neighborhood": "Harajuku & Jingumae",
                    "estimated_cost_usd": 20.0,
                    "category": "Shopping",
                    "latitude": 35.6672,
                    "longitude": 139.7056,
                    "transit_from_previous": "🚶 3 min walk into Takeshita pedestrian alley",
                    "insider_tip": "Cat Street is the serene, hip alternative to the crowded Takeshita strip.",
                },
                "evening": {
                    "slot_id": "evening",
                    "slot_type": "Evening Dining & Entertainment",
                    "time": "18:30 - 22:00",
                    "title": "Shibuya Sky Observation Deck & Scramble Crossing",
                    "description": "Stand 229 meters high on the open-air rooftop observing the world's busiest pedestrian crossing pulse with thousands of neon-lit people below.",
                    "neighborhood": "Shibuya Scramble",
                    "estimated_cost_usd": 42.0,
                    "category": "Entertainment",
                    "latitude": 35.6595,
                    "longitude": 139.7005,
                    "transit_from_previous": "🚶 12 min walk along Meiji-dori Avenue into Shibuya",
                    "dietary_options": "Sky lounge tapas and craft cocktails with panoramic views",
                    "insider_tip": "Book sunset tickets 4 weeks in advance; tripods are not permitted on the open roof.",
                },
            },
        ],
    },
}


def get_mock_recommendations(vibe_str: str, budget_str: str = "Moderate") -> List[DestinationRecommendation]:
    """Return top 3 curated destination recommendations based on mood/vibe."""
    vibe_key = "Cultural"
    vibe_lower = vibe_str.lower()
    if "beach" in vibe_lower or "coastal" in vibe_lower:
        vibe_key = "Beach"
    elif "mountain" in vibe_lower or "nature" in vibe_lower:
        vibe_key = "Mountains"
    elif "urban" in vibe_lower or "skyline" in vibe_lower or "nightlife" in vibe_lower:
        vibe_key = "Urban"
    elif "culture" in vibe_lower or "heritage" in vibe_lower or "ancient" in vibe_lower:
        vibe_key = "Cultural"
    elif "food" in vibe_lower or "culinary" in vibe_lower:
        vibe_key = "Urban"
    else:
        vibe_key = "Cultural"

    items = VIBE_DESTINATIONS.get(vibe_key, VIBE_DESTINATIONS["Cultural"])

    # Adjust estimated daily cost slightly according to budget tier
    multiplier = 0.7 if budget_str == "Budget" else (1.8 if budget_str == "Luxury" else 1.0)

    recommendations = []
    for item in items:
        rec = DestinationRecommendation(
            city=item["city"],
            country=item["country"],
            match_score=item["match_score"],
            vibe_tags=item["vibe_tags"],
            weather_season=item["weather_season"],
            estimated_daily_usd=round(item["estimated_daily_usd"] * multiplier, 1),
            why_matched=item["why_matched"],
            highlights=item["highlights"],
            best_neighborhoods=item.get("best_neighborhoods", []),
        )
        recommendations.append(rec)
    return recommendations


def generate_mock_itinerary(prefs: TripPreferences) -> Itinerary:
    """Generate a rich, geographically optimized itinerary for demo mode or fallback."""
    dest_clean = prefs.destination.strip().lower()

    # If destination matches Paris or Tokyo, load the deeply curated plans
    if "paris" in dest_clean and "paris" in CURATED_ITINERARIES:
        curated = CURATED_ITINERARIES["paris"]
        days = []
        for d in curated["days"][: prefs.duration_days]:
            dp = DayPlan(
                day_number=d["day_number"],
                date=prefs.start_date,
                theme=d["theme"],
                cluster_neighborhood=d["cluster_neighborhood"],
                daily_transit_overview=d["daily_transit_overview"],
                transit_fatigue_score=d["transit_fatigue_score"],
                morning=ActivitySlot(**d["morning"]),
                lunch=ActivitySlot(**d["lunch"]),
                afternoon=ActivitySlot(**d["afternoon"]),
                evening=ActivitySlot(**d["evening"]),
            )
            days.append(dp)
        
        # If requested duration is more than curated days, dynamically extend
        while len(days) < prefs.duration_days:
            day_num = len(days) + 1
            days.append(_create_dynamic_day(day_num, prefs.destination or "Paris", "France", prefs))

        itinerary = Itinerary(
            title=f"{prefs.duration_days}-Day Curated Journey in Paris",
            destination="Paris",
            country="France",
            days=days,
            preferences=prefs,
        )
        itinerary.calculate_total_cost()
        return itinerary

    elif "tokyo" in dest_clean and "tokyo" in CURATED_ITINERARIES:
        curated = CURATED_ITINERARIES["tokyo"]
        days = []
        for d in curated["days"][: prefs.duration_days]:
            dp = DayPlan(
                day_number=d["day_number"],
                date=prefs.start_date,
                theme=d["theme"],
                cluster_neighborhood=d["cluster_neighborhood"],
                daily_transit_overview=d["daily_transit_overview"],
                transit_fatigue_score=d["transit_fatigue_score"],
                morning=ActivitySlot(**d["morning"]),
                lunch=ActivitySlot(**d["lunch"]),
                afternoon=ActivitySlot(**d["afternoon"]),
                evening=ActivitySlot(**d["evening"]),
            )
            days.append(dp)

        while len(days) < prefs.duration_days:
            day_num = len(days) + 1
            days.append(_create_dynamic_day(day_num, prefs.destination or "Tokyo", "Japan", prefs))

        itinerary = Itinerary(
            title=f"{prefs.duration_days}-Day High-Tech & Heritage Tokyo Plan",
            destination="Tokyo",
            country="Japan",
            days=days,
            preferences=prefs,
        )
        itinerary.calculate_total_cost()
        return itinerary

    # Generic realistic itinerary for any city (Rome, New York, Bali, Jaipur, etc.)
    city_name = prefs.destination.strip().title() if prefs.destination else "Rome"
    country_name = "International"

    # Known country lookups
    known_countries = {
        "Rome": "Italy",
        "New York": "USA",
        "Bali": "Indonesia",
        "Jaipur": "India",
        "Barcelona": "Spain",
        "London": "United Kingdom",
        "Dubai": "United Arab Emirates",
        "Singapore": "Singapore",
        "Kyoto": "Japan",
        "Bangkok": "Thailand",
        "Amsterdam": "Netherlands",
    }
    for k, v in known_countries.items():
        if k.lower() in city_name.lower():
            country_name = v
            break

    days = []
    for day_num in range(1, prefs.duration_days + 1):
        days.append(_create_dynamic_day(day_num, city_name, country_name, prefs))

    itinerary = Itinerary(
        title=f"{prefs.duration_days}-Day Personalized Experience in {city_name}",
        destination=city_name,
        country=country_name,
        days=days,
        preferences=prefs,
    )
    itinerary.calculate_total_cost()
    return itinerary


def _create_dynamic_day(day_num: int, city: str, country: str, prefs: TripPreferences) -> DayPlan:
    """Helper to assemble a geographically sensible day plan for any city."""
    clusters = [
        {"name": f"Historic Old Town & Central Plaza", "theme": "Foundational Heritage & Iconic Landmarks"},
        {"name": f"Waterfront, Marina & Arts Quarter", "theme": "Maritime Panoramas & Creative Culture"},
        {"name": f"Hillside Viewpoints & Bohemian Enclaves", "theme": "Scenic Heights & Artisanal Cafes"},
        {"name": f"Garden Estates & Royal Architecture", "theme": "Palaces, Botany & Quiet Respite"},
        {"name": f"Modern Downtown & Gastronomy Hub", "theme": "Modern Energy & Culinary Innovation"},
    ]
    cluster_idx = (day_num - 1) % len(clusters)
    selected_cluster = clusters[cluster_idx]

    # Cost scale based on budget
    budget_mult = 0.7 if prefs.budget_level == "Budget" else (1.9 if prefs.budget_level == "Luxury" else 1.0)

    # Base coords near famous cities or neutral default
    base_lat, base_lng = 41.9028, 12.4964  # Rome default
    if "rome" in city.lower():
        base_lat, base_lng = 41.9028, 12.4964
    elif "bali" in city.lower():
        base_lat, base_lng = -8.5069, 115.2625
    elif "york" in city.lower():
        base_lat, base_lng = 40.7128, -74.0060
    elif "jaipur" in city.lower():
        base_lat, base_lng = 26.9124, 75.7873
    elif "barcelona" in city.lower():
        base_lat, base_lng = 41.3879, 2.1699

    offset = (day_num - 1) * 0.015

    morning = ActivitySlot(
        slot_id="morning",
        slot_type="Morning Sightseeing",
        time="09:00 - 12:30",
        title=f"{city} Historic Landmark & Landmark Pavilion (Day {day_num})",
        description=f"Explore the primary architectural marvel of {selected_cluster['name']}. Enjoy uncrowded morning access and guided photography spots.",
        neighborhood=selected_cluster["name"],
        estimated_cost_usd=round(25.0 * budget_mult, 1),
        category="Sightseeing",
        latitude=base_lat + offset,
        longitude=base_lng + offset,
        insider_tip="Arrive 15 minutes before ticket gates open to capture pristine photos without crowds.",
    )

    lunch = ActivitySlot(
        slot_id="lunch",
        slot_type="Lunch Recommendation",
        time="12:30 - 14:00",
        title=f"Trattoria & Artisanal Bistro {selected_cluster['name'].split()[0]}",
        description=f"Authentic local dining serving fresh regional delicacies, farm-to-table salads, and crisp local refreshments.",
        neighborhood=selected_cluster["name"],
        estimated_cost_usd=round(22.0 * budget_mult, 1),
        category="Food",
        latitude=base_lat + offset + 0.003,
        longitude=base_lng + offset + 0.002,
        transit_from_previous="🚶 5 min leisurely walk down pedestrian promenade",
        dietary_options=f"{prefs.dietary} selections featured prominently on seasonal menu",
        insider_tip="Ask the waiter for the daily chalkboard chef special.",
    )

    afternoon = ActivitySlot(
        slot_id="afternoon",
        slot_type="Afternoon Leisure & Culture",
        time="14:30 - 17:30",
        title=f"{city} Heritage Museum & Artisan Courtyards",
        description=f"Discover regional craftsmanship, historic tapestries, and tranquil courtyards showcasing the cultural evolution of {city}.",
        neighborhood=selected_cluster["name"],
        estimated_cost_usd=round(18.0 * budget_mult, 1),
        category="Culture",
        latitude=base_lat + offset + 0.006,
        longitude=base_lng + offset + 0.004,
        transit_from_previous="🚶 7 min stroll through cobblestone side-alleys",
        insider_tip="The interior shaded courtyard is an ideal spot to rest with local gelato or espresso.",
    )

    evening = ActivitySlot(
        slot_id="evening",
        slot_type="Evening Dining & Entertainment",
        time="18:30 - 22:00",
        title=f"Sunset Overlook & Rooftop Dining in {city}",
        description=f"Watch the sunset bathe the city rooftops in amber glow, followed by an intimate dinner featuring signature regional courses and live music.",
        neighborhood=selected_cluster["name"],
        estimated_cost_usd=round(45.0 * budget_mult, 1),
        category="Entertainment",
        latitude=base_lat + offset + 0.008,
        longitude=base_lng + offset + 0.006,
        transit_from_previous="🚶 9 min walk toward the illuminated square",
        dietary_options=f"Full culinary pairings catering to {prefs.dietary} diets",
        insider_tip="Reserve rooftop terrace seating 30 minutes ahead of scheduled golden hour.",
    )

    return DayPlan(
        day_number=day_num,
        theme=selected_cluster["theme"],
        cluster_neighborhood=selected_cluster["name"],
        daily_transit_overview="All 4 activities tightly clustered within 1.8 km. Easy walking route with low transit stress.",
        transit_fatigue_score="Low",
        morning=morning,
        lunch=lunch,
        afternoon=afternoon,
        evening=evening,
    )
