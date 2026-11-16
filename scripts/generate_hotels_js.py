#!/usr/bin/env python3
"""Compile verified hotel simulation data, reviews, activities, and downloaded photos into data/hotels_data.js."""
from __future__ import annotations

import json
from pathlib import Path

BASE_DIR = Path("/Users/video/.gemini/antigravity/scratch/vacaciones-familia-colombia")
MANIFEST_PATH = BASE_DIR / "data" / "photos_manifest.json"
OUT_JS_PATH = BASE_DIR / "data" / "hotels_data.js"


def main():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    photos_by_slug = manifest.get("hotels", {})
    proofs = manifest.get("proofs", {})

    def attach_proof(slug: str, proof_key: str, caption: str):
        lst = list(photos_by_slug.get(slug, []))
        if proof_key in proofs:
            lst.append({
                "localPath": proofs[proof_key],
                "remoteUrl": proofs[proof_key],
                "category": "captura",
                "caption": caption,
                "bytes": 0,
                "width": 0,
                "height": 0,
            })
        return lst

    hotels = [
        {
            "id": "hotel-las-mananitas",
            "rank": 1,
            "name": "Hotel Las Mañanitas",
            "chain": "Capurganá Caribe (Independiente)",
            "destination": "Capurganá, Chocó Caribe",
            "regionGroup": "otros",
            "regionFilter": "capurgana",
            "coords": [8.6358, -77.3508],
            "status": "active_rate",
            "statusLabel": "Tarifa Oficial Activa (Confirmar cupo WhatsApp)",
            "badgeTone": "green",
            "roomType": "Habitación Familiar con balcón vista al mar",
            "officialUrl": "https://hotellasmananitas.com/",
            "bookingUrl": "https://hotellasmananitas.com/#plan",
            "whatsapp": "+57 311 310 4811",
            "antiScamNote": "Cotizador directo oficial en hotellasmananitas.com (RNT 7537, Playa de los Pescadores).",
            "proofKey": None,
            "pricing": {
                "nights7Total": 10010000,
                "regular7Total": 12320000,
                "savingsAmount": 2310000,
                "nightlyRates7": [1430000, 1430000, 1430000, 1430000, 1430000, 1430000, 1430000],
                "adultNight": 440000,
                "childNight": 275000,
                "preNye7Total": 10010000,
                "jan7Total": 9200000,
                "ivaIncludedText": "Impuestos de alimentación y alojamiento incluidos",
                "mandatoryExtras": 760000,
                "mandatoryExtrasLabel": "Lanchas Necoclí–Capurganá ida/vuelta (~$190.000 × 4)",
                "fits10M": True,
                "isAvailableNye": True,
            },
            "discount": {
                "hasDiscount": True,
                "badge": "🏷️ Niños 3–11 años -37,5%",
                "detail": "Los niños de 7 y 10 años pagan $275.000/noche en lugar de $440.000/noche de adulto (ahorras $2.310.000 en la semana).",
                "deadline": "Bloqueo anticipado por temporada alta",
            },
            "cancellation": "Confirmación y reserva directa con asesoría de hotel en Playa de los Pescadores.",
            "meals": {
                "planName": "Todo Incluido + Barra Libre Vespertina",
                "included": [
                    "Desayuno, almuerzo y cena buffet de cocina típica chocoana (pescado fresco del día, arroz con coco, patacones, frutas).",
                    "Barra libre diaria de 5:00 p.m. a 9:00 p.m. (cócteles de la casa, licores nacionales y cerveza).",
                    "Almuerzo típico incluido durante la excursión de día completo a Playa Soledad y Bahía El Aguacate.",
                    "Recibimiento en el muelle, transporte de equipaje y tarjeta de asistencia médica.",
                ],
                "excluded": [
                    "Bebidas alcohólicas fuera del horario 5:00 p.m.–9:00 p.m.",
                    "Tiquetes aéreos (vuelo a Apartadó/chárter) y lancha desde Necoclí (~$190.000/pers. ida y vuelta).",
                ],
            },
            "activities": {
                "includedHotel": [
                    "Piscina y jacuzzi frente al Mar Caribe.",
                    "Excursión en lancha a Sapzurro + caminata por la selva hasta La Miel (Panamá) — incluida.",
                    "Día completo en lancha a Playa Soledad y Bahía El Aguacate con guía y tasa portuaria — incluida.",
                    "Caminata ecológica a cascadas El Cielo o piscinas naturales La Coquerita — incluida.",
                ],
                "kidsFriendly": [
                    "Snorkel seguro en aguas calmas y transparentes de Bahía El Aguacate y La Miel (ideal para 7 y 10 años).",
                    "Pueblo libre de carros: los niños caminan seguros entre playas y heladerías.",
                    "Observación de cangrejos, peces de arrecife y cascadas de agua dulce.",
                ],
            },
            "reviews": {
                "overall": "4.1 / 5",
                "sources": [
                    {"name": "Google", "score": "4.3 / 5"},
                    {"name": "TripAdvisor", "score": "4.0 / 5"},
                    {"name": "Kayak / Otros", "score": "3.9 / 5"},
                ],
                "pros": [
                    "Arquitectura estilo hacienda caribeña con balcones privados frente al mar y piscina muy cuidada.",
                    "Sazón casera con pescado fresco y gran ahorro al incluir las 3 excursiones marítimas clave.",
                    "Excelente ubicación cerca del muelle sin estar en medio del ruido.",
                ],
                "cons": [
                    "Instalaciones tradicionales que muestran el paso de los años (revisar aire acondicionado y grifería).",
                    "Wi-Fi lento limitado a zonas comunes por la ubicación remota en el Darién.",
                ],
            },
            "photos": photos_by_slug.get("hotel-las-mananitas", []),
        },
        {
            "id": "ecolodge-el-almejal",
            "rank": 2,
            "name": "Ecolodge El Almejal",
            "chain": "El Valle, Bahía Solano",
            "destination": "Bahía Solano, Chocó Pacífico",
            "regionGroup": "otros",
            "regionFilter": "bahia-solano",
            "coords": [6.1105, -77.4328],
            "status": "available_limited",
            "statusLabel": "DISPONIBLE EN VIVO (Máx. 5 noches web: 26–31 dic)",
            "badgeTone": "green",
            "roomType": "Cabaña Familiar (2 alcobas independientes + terraza con hamaca)",
            "officialUrl": "https://www.almejal.com.co/",
            "bookingUrl": "https://hotels.cloudbeds.com/es/reservation/vGqrUN/guests?currency=cop&checkin=2026-12-26&checkout=2026-12-31&guests=4",
            "whatsapp": "+57 320 674 6023",
            "antiScamNote": "Reserva directa oficial verificada en Cloudbeds desde almejal.com.co.",
            "proofKey": "almejal-checkout.png",
            "pricing": {
                "nights7Total": 12516000,
                "nights5Total": 8940000,
                "regular7Total": 14560000,
                "savingsAmount": 2044000,
                "nightlyRates7": [1788000, 1788000, 1788000, 1788000, 1788000, 1788000, 1788000],
                "adultNight": 520000,
                "childNight": 374000,
                "preNye7Total": 12516000,
                "jan7Total": 11800000,
                "ivaIncludedText": "Exento de IVA ($0 COP) · Depósito 50% ($4.470.000 para 5 noches)",
                "mandatoryExtras": 180000,
                "mandatoryExtrasLabel": "Tasa municipal Proturismo + entrada PNN Utría (~$180.000 los 4)",
                "fits10M": True,
                "isAvailableNye": True,
                "maxOnlineNights": 5,
            },
            "discount": {
                "hasDiscount": True,
                "badge": "🏷️ Niños -28% · Exento de IVA",
                "detail": "Tarifa infantil de $374.000/noche vs $520.000/noche adulto. El plan de 5 noches (26–31 dic) cuesta $8.940.000 COP total en vivo.",
                "deadline": "Motor web permite máx. 5 noches por reserva (extensión a 7 noches por solicitud directa)",
            },
            "cancellation": "30+ días antes: penalidad $70.000/pers.; 15–28 días: 40%; 1–14 días: 60%.",
            "meals": {
                "planName": "Plan Pacífico Mágico (Pensión Completa + Excursiones)",
                "included": [
                    "Desayunos, almuerzos y cenas diarias con cocina del Pacífico (pescado fresco, cocina casera, opciones infantiles).",
                    "Traslados terrestres aeropuerto Bahía Solano (BSC) – Ecolodge – Aeropuerto.",
                    "Tarjeta de asistencia médica y recuerdo conmemorativo.",
                ],
                "excluded": [
                    "Bebidas alcohólicas y barra libre (se facturan aparte).",
                    "Tiquetes aéreos Satena / Clic a Bahía Solano, tasa Proturismo y boleta de ingreso a PNN Utría.",
                ],
            },
            "activities": {
                "includedHotel": [
                    "Caminata guiada en la Reserva Natural El Almejal — incluida.",
                    "Excursión en lancha al Parque Nacional Natural Ensenada de Utría — incluida.",
                    "Excursión por el Río Valle y tubing — incluida.",
                    "Caminata a Cascadas Chadó con guía local — incluida.",
                ],
                "kidsFriendly": [
                    "¡Temporada dic–ene de nacimiento y liberación de tortugas marinas golfina frente a la playa del lodge!",
                    "Playa extensa casi privada y piscina natural de roca segura para explorar.",
                    "Tubing tranquilo por río rodeado de selva tropical (ideal para edades de 7 y 10 años).",
                ],
            },
            "reviews": {
                "overall": "4.8 / 5",
                "sources": [
                    {"name": "Booking", "score": "9.1 / 10"},
                    {"name": "TripAdvisor", "score": "Travelers' Choice"},
                    {"name": "Google", "score": "4.8 / 5"},
                ],
                "pros": [
                    "Puntuación élite: calificado como uno de los mejores ecolodges familiares de Colombia.",
                    "Alimentación deliciosa y variada; cabañas familiares amplias con hamacas entre selva y mar.",
                    "Educación ambiental inolvidable para niños (tortugas, ranitas, senderos, ríos).",
                ],
                "cons": [
                    "Trayecto de 40–45 min por carretera desde el aeropuerto de Bahía Solano hasta El Valle.",
                    "Ambiente de selva húmeda tropical (indispensable llevar repelente ecológico y linterna).",
                ],
            },
            "photos": attach_proof("ecolodge-el-almejal", "almejal-checkout.png", "Captura oficial Cloudbeds: 5 noches 26–31 dic por $8.940.000 COP"),
        },
        {
            "id": "sol-caribe-san-andres",
            "rank": 3,
            "name": "Hotel Sol Caribe San Andrés",
            "chain": "Hoteles Solar",
            "destination": "Centro / Spratt Bight, San Andrés",
            "regionGroup": "san-andres",
            "regionFilter": "san-andres",
            "coords": [12.5836, -81.6968],
            "status": "available",
            "statusLabel": "DISPONIBLE EN VIVO (26 dic – 2 ene)",
            "badgeTone": "amber",
            "roomType": "Habitación Estándar (4 huéspedes: 2 adultos + 2 niños)",
            "officialUrl": "https://www.solarhoteles.com/es/hoteles/sol-caribe-san-andres-en-isla-san-andres/",
            "bookingUrl": "https://www.solarhoteles.com/es/bookcore/availability/solcaribesanandres/2026-12-26/2027-01-02/2;7;10/?rrc=1&adults=2&children-ages=7%2C10&ninos=2",
            "whatsapp": "Reserva directa web",
            "antiScamNote": "Motor oficial Roiback en solarhoteles.com (activar switch 'Unirse a VIP Club' para el -5%).",
            "proofKey": "sol-caribe-checkout.png",
            "pricing": {
                "nights7Total": 13067250,
                "regular7Total": 13755000,
                "savingsAmount": 687750,
                "nightlyRates7": [1650150, 1650150, 1650150, 2029200, 2029200, 2029200, 2029200],
                "preNye7Total": 11551050,
                "jan7Total": 10200000,
                "ivaIncludedText": "Exento de IVA ($0 COP) · Tarifa VIP Club -5% aplicada",
                "mandatoryExtras": 584000,
                "mandatoryExtrasLabel": "4 Tarjetas de Turismo OCCRE en aeropuerto (~$146.000 × 4)",
                "fits10M": False,
                "fits10MShortStay": True,
                "isAvailableNye": True,
            },
            "discount": {
                "hasDiscount": True,
                "badge": "🏷️ Club VIP -5% (-$687k) · Cancela Gratis 11 dic",
                "detail": "Al activar 'Unirse a VIP Club' en su web oficial ahorras $687.750 COP. Además, bajando a 5 noches (ej. 26–31 dic) queda en $9.008.850 COP (¡bajo $10M!).",
                "deadline": "Cancelación gratuita hasta el 11 de diciembre de 2026",
            },
            "cancellation": "GRATIS hasta el 11/12/2026. Desde el 12/12/2026 penalidad de 1ra noche ($1.650.150 COP).",
            "meals": {
                "planName": "Todo Incluido Clásico (Desayuno, Almuerzo, Cena, Snacks y Barra Libre)",
                "included": [
                    "Desayuno, almuerzo y cena tipo buffet en restaurantes del hotel (Bucanero / Mirador).",
                    "Snacks entre comidas y bebidas/licores ilimitados nacionales.",
                    "Guarda-equipaje gratuito si llegas antes del check-in (3:00 p.m.).",
                ],
                "excluded": [
                    "No incluye traslados al club de playa de Sol Caribe Campo (a 15 min al sur).",
                    "Tours a cayos (ej. lancha Johnny Cay ~$50.000 + impuesto ecológico $15.000 por persona).",
                ],
            },
            "activities": {
                "includedHotel": [
                    "Piscina al aire libre y recreación dirigida diaria.",
                    "A 4 minutos caminando de Playa Spratt Bight y del malecón peatonal.",
                    "Gimnasio, zona de juegos y entretenimiento nocturno.",
                ],
                "kidsFriendly": [
                    "Cero gasto en taxis diarios: bajas caminando a la playa principal y heladerías.",
                    "Muelle de salida a Johnny Cay y Acuario/Haynes Cay a pocos pasos.",
                    "Alquiler opcional de carrito/mulita para dar la vuelta a la isla (West View, Hoyo Soplador, La Piscinita).",
                ],
            },
            "reviews": {
                "overall": "4.4 / 5",
                "sources": [
                    {"name": "Google", "score": "4.4 / 5"},
                    {"name": "TripAdvisor", "score": "4.4 / 5"},
                    {"name": "Ubicación", "score": "9.6 / 10"},
                ],
                "pros": [
                    "Ubicación estrella en pleno North End cerca de playa Spratt Bight, tiendas y muelles.",
                    "Habitaciones amplias, camas cómodas, aires acondicionados potentes y personal muy amable.",
                    "La mejor relación precio-comodidad Todo Incluido en San Andrés para familias.",
                ],
                "cons": [
                    "Mobiliario clásico que denota varios años de trayectoria.",
                    "Comedor concurrido en horas pico de temporada alta y Wi-Fi débil en cuartos.",
                ],
            },
            "photos": attach_proof("sol-caribe-san-andres", "sol-caribe-checkout.png", "Captura oficial solarhoteles.com: 7 noches VIP $13.067.250 COP"),
        },
        {
            "id": "decameron-maryland",
            "rank": 4,
            "name": "Decameron Maryland All Inclusive",
            "chain": "Hoteles Decameron (Trademark Collection)",
            "destination": "Sarie Bay / Centro, San Andrés",
            "regionGroup": "san-andres",
            "regionFilter": "san-andres",
            "coords": [12.5819, -81.6908],
            "status": "available",
            "statusLabel": "DISPONIBLE EN VIVO (Único Decameron con cupo para 4)",
            "badgeTone": "amber",
            "roomType": "Junior Suite Familiar (2 adultos + 2 niños)",
            "officialUrl": "https://www.decameron.com/es/hoteles/san-andres-islas/decameron-maryland/",
            "bookingUrl": "https://www.decameron.com/es/bookcore/availability/dcmmrl/2026-12-26/2027-01-02/2;7;10/?rrc=1&adults=2&children-ages=7%2C10&ninos=2",
            "whatsapp": "Reserva directa decameron.com",
            "antiScamNote": "Motor oficial Roiback en decameron.com. (Isleño, Los Delfines, Marazul y San Luis no tienen cupo para 4).",
            "proofKey": None,
            "pricing": {
                "nights7Total": 14664747,
                "regular7Total": 24139502,
                "savingsAmount": 9474755,
                "nightlyRates7": [2094964, 2094964, 2094964, 2094964, 2094964, 2094964, 2094963],
                "flex7Total": 16093000,
                "preNye7Total": 13500000,
                "jan7Total": 11900000,
                "ivaIncludedText": "Exento de IVA ($0 COP) · Tarifa Black Days No Reembolsable",
                "mandatoryExtras": 584000,
                "mandatoryExtrasLabel": "4 Tarjetas de Turismo OCCRE en aeropuerto (~$146.000 × 4)",
                "fits10M": False,
                "isAvailableNye": True,
            },
            "discount": {
                "hasDiscount": True,
                "badge": "🔥 BLACK DAYS -39,2% (Ahorras $9,47M)",
                "detail": "Tarifa 'Anticípate Black Days' rebaja la semana de $24.139.502 a $14.664.747 COP (No Reembolsable) o $16.093.000 COP en Black Days Flex.",
                "deadline": "Black Days Flex permite cancelar gratis hasta el 23 de diciembre de 2026",
            },
            "cancellation": "Tarifa $14.664.747 es No Reembolsable; versión Flex ($16.093.000) cancela gratis hasta 23/12/2026.",
            "meals": {
                "planName": "Todo Incluido Decameron (Buffet, A la Carta, Snacks y Barra Libre)",
                "included": [
                    "Desayunos, almuerzos y cenas buffet + cenas a la carta en Restaurante North End.",
                    "Snacks diarios y bebidas alcohólicas/no alcohólicas ilimitadas.",
                    "Cenas temáticas especiales en temporada de Fin de Año.",
                ],
                "excluded": [
                    "Traslados aeropuerto-hotel-aeropuerto y tours externos.",
                    "Acceso automático garantizado a sedes como Decameron Isleño (sujeto a políticas/cupo Intercambio).",
                ],
            },
            "activities": {
                "includedHotel": [
                    "Piscina frente al mar con vista panorámica directa hacia el islote Johnny Cay.",
                    "Actividades diurnas, toallas de playa/piscina y shows nocturnos.",
                    "A 5–7 minutos caminando del comercio y de la playa de arena blanca Spratt Bight.",
                ],
                "kidsFriendly": [
                    "Piscina tranquila y Junior Suite Familiar amplia para descansar los 4.",
                    "⚠️ Ojo con la playa justo frente al hotel: tiene rocas y oleaje; para baño seguro de niños se camina ~5 min a Spratt Bight.",
                    "Fácil acceso caminando al letrero 'I Love San Andrés' y muelle de lanchas.",
                ],
            },
            "reviews": {
                "overall": "7.5 / 10",
                "sources": [
                    {"name": "Booking", "score": "7.5 / 10"},
                    {"name": "Expedia", "score": "7.8 / 10"},
                    {"name": "Ubicación", "score": "9.0 / 10"},
                ],
                "pros": [
                    "Ambiente pequeño, tranquilo y menos masivo que otros resorts grandes.",
                    "Vistas espectaculares hacia Johnny Cay y excelente atención de meseros en Fin de Año.",
                    "Junior Suite Familiar espaciosa para 2 adultos y 2 niños.",
                ],
                "cons": [
                    "La costa justo enfrente tiene piedras y oleaje (no es playa de arena plana para niños).",
                    "Infraestructura tradicional con algo de desgaste por salitre y buffet más pequeño.",
                ],
            },
            "photos": photos_by_slug.get("decameron-maryland", []),
        },
        {
            "id": "hotel-arena-blanca",
            "rank": 5,
            "name": "Hotel Arena Blanca by Dorado",
            "chain": "Dorado Plaza Hoteles",
            "destination": "Punta Hansa, San Andrés",
            "regionGroup": "san-andres",
            "regionFilter": "san-andres",
            "coords": [12.5861, -81.6924],
            "status": "available",
            "statusLabel": "DISPONIBLE EN VIVO (26 dic – 2 ene)",
            "badgeTone": "amber",
            "roomType": "Estándar Cuádruple (u Oasis Superior renovada por +$756k)",
            "officialUrl": "https://www.hotelarenablanca.com.co/",
            "bookingUrl": "https://aresai.backhotelite.com/es/bookcore/availability/aresai/2026-12-26/2027-01-02/2;7;10/?adults=2&children-ages=7%2C10",
            "whatsapp": "Reserva directa web",
            "antiScamNote": "Motor oficial en aresai.backhotelite.com (Hotel El Dorado está 100% agotado).",
            "proofKey": "arena-blanca-checkout.png",
            "pricing": {
                "nights7Total": 16962000,
                "regular7Total": 16992000,
                "savingsAmount": 30000,
                "nightlyRates7": [2423143, 2423143, 2423143, 2423143, 2423143, 2423143, 2423142],
                "oasis7Total": 17718000,
                "preNye7Total": 14800000,
                "jan7Total": 12400000,
                "ivaIncludedText": "Impuestos incluidos ($0 IVA) · Descuento Dorado -$30.000",
                "mandatoryExtras": 584000,
                "mandatoryExtrasLabel": "4 Tarjetas de Turismo OCCRE en aeropuerto (~$146.000 × 4)",
                "fits10M": False,
                "isAvailableNye": True,
            },
            "discount": {
                "hasDiscount": False,
                "badge": "Promo Dorado -$30.000 (No Reembolsable)",
                "detail": "Estándar Cuádruple en $16.962.000 COP (Torre Oasis renovada con 2 camas Queen en $17.718.000 COP). Pago 100% anticipado no reembolsable.",
                "deadline": "Sujeto a disponibilidad de inventario Fin de Año",
            },
            "cancellation": "Tarifa No Reembolsable: 100% pago anticipado sin cambios ni devoluciones.",
            "meals": {
                "planName": "Todo Incluido (Restaurante Alcatraz + Bar Piscina)",
                "included": [
                    "Desayuno, almuerzo y cena tipo buffet en Restaurante Alcatraz (frutas tropicales, jugos y platos caribeños).",
                    "Snacks de tarde y bebidas en bar junto a la piscina.",
                ],
                "excluded": [
                    "Consumos de restaurantes externos o tours náuticos.",
                ],
            },
            "activities": {
                "includedHotel": [
                    "2 piscinas al aire libre + zona de chapoteadero infantil CON TOBOGÁN.",
                    "Espectáculos nocturnos y clases de baile para toda la familia.",
                    "A 5 minutos caminando de la playa de Bahía Sardina / Spratt Bight.",
                ],
                "kidsFriendly": [
                    "El tobogán acuático infantil en la piscina es uno de los favoritos para edades de 7 y 10 años.",
                    "Cercanía inmediata a playa tranquila de arena blanca y restaurantes familiares.",
                ],
            },
            "reviews": {
                "overall": "4.3 / 5",
                "sources": [
                    {"name": "Google", "score": "4.5 / 5"},
                    {"name": "Booking / Kayak", "score": "7.8 / 10"},
                    {"name": "Ubicación", "score": "9.3 / 10"},
                ],
                "pros": [
                    "Excelente ubicación en Punta Hansa, muy cerca de Spratt Bight sin ruido excesivo.",
                    "Piscina con tobogán infantil, buen aseo diario y personal cordial.",
                    "Torre Oasis ofrece habitaciones modernas y amplias con camas Queen.",
                ],
                "cons": [
                    "Variedad del buffet puede sentirse repetitiva en estancias de 7 noches.",
                    "Habitaciones estándar muestran paso de los años y Wi-Fi débil en pisos altos.",
                ],
            },
            "photos": attach_proof("hotel-arena-blanca", "arena-blanca-checkout.png", "Captura oficial Arena Blanca: 7 noches $16.962.000 COP"),
        },
        {
            "id": "wayira-beach",
            "rank": 6,
            "name": "Wayira Beach by On Vacation",
            "chain": "On Vacation",
            "destination": "Mayapo, La Guajira (35 min de Riohacha)",
            "regionGroup": "otros",
            "regionFilter": "mayapo",
            "coords": [11.6445, -72.7962],
            "status": "sold_out_nye_available_other",
            "statusLabel": "Agotado dic 23–31 (4 pax) · DISPONIBLE enero con 50% OFF",
            "badgeTone": "amber",
            "roomType": "Bungalow Wayuu — Superior Cuádruple Kids",
            "officialUrl": "https://www.onvacation.com/co/destinos/nacionales/guajira/hotel-wayira-beach/",
            "bookingUrl": "https://www.onvacation.com/co/",
            "whatsapp": "Canal oficial onvacation.com",
            "antiScamNote": "⚠️ CUIDADO: hotelwayirabeach.com y reservaswayira.com son agencias externas. Reserva SOLO en onvacation.com/co/.",
            "proofKey": "wayira-checkout.png",
            "pricing": {
                "nights7Total": None,
                "regular7Total": 9100028,
                "jan7Total": 4550014,
                "savingsAmount": 4550014,
                "nightlyRates7": [650002, 650002, 650002, 650002, 650002, 650002, 650002],
                "preNye7Total": None,
                "ivaIncludedText": "Incluye impuestos, tasas y cargos (simulación real enero 2027)",
                "mandatoryExtras": 0,
                "mandatoryExtrasLabel": "No exige tarjeta de entrada como San Andrés (vuelo a Riohacha RCH aparte)",
                "fits10M": True,
                "isAvailableNye": False,
            },
            "discount": {
                "hasDiscount": True,
                "badge": "🔥 BLACK DAYS 2×1 (-50% OFF)",
                "detail": "Si pueden viajar en enero (ej. 16–23 ene 2027), los 7 días Todo Incluido para los 4 bajan de $9.100.028 a ¡$4.550.014 COP! (En dic 23–30 y 26–30 aparece agotado para 4 personas online).",
                "deadline": "Promo Black Days On Vacation anunciada del 12 al 18 de noviembre",
            },
            "cancellation": "Verificado en vivo: 23–30 dic, 26–30 dic y 26 dic–2 ene arrojan 0 cupos online para 4 pax; preguntar vía telefónica por chárter.",
            "meals": {
                "planName": "Todo Incluido Pulsera (Buffet + Bebidas en Comidas)",
                "included": [
                    "Desayuno (7–9 a.m.), almuerzo (12–3 p.m.) y cena (6–9 p.m.) buffet con bebidas en restaurante Jasai.",
                    "Acceso directo a playa privada de Mayapo (232 m), piscina gigante y jacuzzi.",
                ],
                "excluded": [
                    "Kioskos especializados (Kiosko Fritos, Isashi), consumo de minibar, spa y alquiler de cuatrimotos.",
                ],
            },
            "activities": {
                "includedHotel": [
                    "Piscina central (9 a.m.–8:40 p.m.), jacuzzi al aire libre, canchas de vóleibol y fútbol playa.",
                    "Columpios y camas de playa frente al mar esmeralda de Mayapo.",
                    "Actividades de recreación familiar y música en vivo.",
                ],
                "kidsFriendly": [
                    "Visita cultural a Rancherías Wayuu y telares artesanales.",
                    "Excursión opcional al Santuario de Flamencos Rosados de Camarones o dunas de La Guajira.",
                    "Bungalows familiares inspirados en la cultura Wayuu.",
                ],
            },
            "reviews": {
                "overall": "3.8 / 5",
                "sources": [
                    {"name": "Google", "score": "4.0 / 5"},
                    {"name": "Expedia", "score": "3.8 / 5"},
                    {"name": "Booking", "score": "7.2 / 10"},
                ],
                "pros": [
                    "Playa amplísima y hermosa en Mayapo, atardeceres únicos y piscina muy disfrutable.",
                    "Con el 50% OFF de Black Days en enero es por lejos el Todo Incluido más económico de Colombia ($4,55M los 4).",
                ],
                "cons": [
                    "Filas en buffet y variedad limitada en temporada alta.",
                    "Viento fuerte en tardes y aire acondicionado justo en algunas habitaciones frente al calor de La Guajira.",
                ],
            },
            "photos": attach_proof("wayira-beach", "wayira-checkout.png", "Captura oficial On Vacation: 7 noches enero con 50% OFF por $4.550.014 COP"),
        },
        {
            "id": "grand-sirenis-san-andres",
            "rank": 7,
            "name": "Grand Sirenis San Andrés",
            "chain": "Sirenis Hotels & Resorts",
            "destination": "North End, San Andrés",
            "regionGroup": "san-andres",
            "regionFilter": "san-andres",
            "coords": [12.5852, -81.6941],
            "status": "available",
            "statusLabel": "DISPONIBLE EN VIVO (Solo queda Suite Presidencial)",
            "badgeTone": "amber",
            "roomType": "Junior Presidential Suite (Estándar agotadas)",
            "officialUrl": "https://www.sirenishotels.com/hoteles-san-andres/grand-sirenis-san-andres/",
            "bookingUrl": "https://bookings.sirenishotels.com/es/bookcore/availability/gssandres/2026-12-26/2027-01-02/2;7;10/",
            "whatsapp": "Reserva directa sirenishotels.com",
            "antiScamNote": "Motor oficial Bookcore en bookings.sirenishotels.com.",
            "proofKey": None,
            "pricing": {
                "nights7Total": 28560000,
                "regular7Total": 28560000,
                "savingsAmount": 0,
                "nightlyRates7": [4080000, 4080000, 4080000, 4080000, 4080000, 4080000, 4080000],
                "preNye7Total": 24000000,
                "jan7Total": 18500000,
                "ivaIncludedText": "Exento de IVA ($0 COP) · Todo incluido gama alta",
                "mandatoryExtras": 584000,
                "mandatoryExtrasLabel": "4 Tarjetas de Turismo OCCRE en aeropuerto (~$146.000 × 4)",
                "fits10M": False,
                "isAvailableNye": True,
            },
            "discount": {
                "hasDiscount": False,
                "badge": "Cancelación Gratis hasta 26 nov",
                "detail": "Es el resort más nuevo de la isla (fin 2023), pero al quedar solo la Junior Presidential Suite cuesta casi el triple del tope ($28,56M).",
                "deadline": "Cancelación gratuita hasta el 26 de noviembre de 2026 (23:59)",
            },
            "cancellation": "Cancelación gratuita hasta el 26 de noviembre de 2026.",
            "meals": {
                "planName": "Todo Incluido 5 Estrellas (Buffet + A la Carta + Minibar Diario)",
                "included": [
                    "Restaurante buffet principal + cenas a la carta en restaurante italiano La Pérgola.",
                    "Bebidas nacionales e internacionales ilimitadas + reposición diaria de minibar.",
                    "Snacks, toallas de piscina y entretenimiento diurno/nocturno.",
                ],
                "excluded": [
                    "Algunas marcas ultra-premium en bares (según categoría) y tours externos.",
                ],
            },
            "activities": {
                "includedHotel": [
                    "Piscina infantil moderna, alberca principal estética y terraza solárium.",
                    "Kids club / zona infantil y gimnasio nuevo.",
                    "A 5 minutos caminando de Playa Spratt Bight.",
                ],
                "kidsFriendly": [
                    "Habitaciones de última generación con Smart TV (Netflix) y excelente aislamiento del ruido.",
                    "Alberca infantil muy cuidada y cercana al centro comercial.",
                ],
            },
            "reviews": {
                "overall": "8.4 / 10",
                "sources": [
                    {"name": "Booking", "score": "8.4 / 10"},
                    {"name": "Expedia", "score": "8.5 / 10"},
                    {"name": "Google", "score": "4.5 / 5"},
                ],
                "pros": [
                    "Instalaciones completamente nuevas (inaugurado finales de 2023), duchas lluvia y camas de alta gama.",
                    "Muy buen sabor en el buffet y restaurante italiano.",
                ],
                "cons": [
                    "No está sobre la playa directamente (toca caminar ~5 min a Spratt Bight).",
                    "Filas reportadas en barra en horas pico; precio muy alto en Fin de Año.",
                ],
            },
            "photos": photos_by_slug.get("grand-sirenis-san-andres", []),
        },
        {
            "id": "punta-faro-mucura",
            "rank": 8,
            "name": "Isla Múcura (Punta Faro y Hotel Isla Múcura)",
            "chain": "Archipiélago de San Bernardo",
            "destination": "Isla Múcura, Bolívar / Sucre",
            "regionGroup": "otros",
            "regionFilter": "covenas-mucura",
            "coords": [9.7845, -75.8705],
            "status": "sold_out",
            "statusLabel": "Sin hab. para 4 en Punta Faro · Isla Múcura 100% Agotado",
            "badgeTone": "slate",
            "roomType": "Solo quedan hab. máx. 3 pers. en Punta Faro (exige 2 hab.)",
            "officialUrl": "https://www.puntafaro.com/",
            "bookingUrl": "https://direct-book.com/properties/hotelpuntafarodirect?locale=es",
            "whatsapp": "Sitios oficiales puntafaro.com / hotelislamucura.com",
            "antiScamNote": "Motores SiteMinder verificados. Hotel Isla Múcura muestra 0 cupos en sus 13 categorías.",
            "proofKey": None,
            "pricing": {
                "nights7Total": 43480000,
                "regular7Total": 43480000,
                "savingsAmount": 0,
                "nightlyRates7": [6211428, 6211428, 6211428, 6211428, 6211428, 6211428, 6211432],
                "preNye7Total": 28000000,
                "jan7Total": 24000000,
                "ivaIncludedText": "Incluye IVA 19% + $1.400.000/hab. sobrecargo Fin de Año (2 hab. necesarias)",
                "mandatoryExtras": 846000,
                "mandatoryExtrasLabel": "Lancha Tolú–Múcura ($180k × 4) + entrada Parque Corales ($31.5k × 4)",
                "fits10M": False,
                "isAvailableNye": False,
            },
            "discount": {
                "hasDiscount": False,
                "badge": "Agotado para 1 habitación familiar",
                "detail": "Una sola habitación Deluxe (máx. 3 pax) cuesta $21.740.000 COP; alojar a los 4 exige 2 habitaciones (~$43,48M) sin contar lanchas.",
                "deadline": "Agotado en formato familiar",
            },
            "cancellation": "Verificado en SiteMinder: Punta Faro cobra 19% IVA + sobrecargo gala Fin de Año.",
            "meals": {
                "planName": "Pensión Completa (3 comidas + jugos en comidas)",
                "included": [
                    "Desayuno, almuerzo y cena con bebidas no alcohólicas durante las comidas.",
                ],
                "excluded": [
                    "Licores, snacks entre comidas, lancha desde Cartagena ($320k/pers.) o Tolú ($180k/pers.) y tasa del Parque Nacional.",
                ],
            },
            "activities": {
                "includedHotel": [
                    "Playa privada de arena blanca coralina y mar turquesa cristalino.",
                    "Kayaks y paddleboard (no motorizados en Punta Faro).",
                ],
                "kidsFriendly": [
                    "Aguas súper tranquilas como piscina natural y tour nocturno de plancton luminoso (extra).",
                ],
            },
            "reviews": {
                "overall": "4.6 / 5",
                "sources": [
                    {"name": "Booking", "score": "9.0 / 10"},
                    {"name": "TripAdvisor", "score": "4.6 / 5"},
                    {"name": "Google", "score": "4.7 / 5"},
                ],
                "pros": [
                    "Playa de postal idílica, descanso absoluto y mar cristalino.",
                ],
                "cons": [
                    "Precio altísimo en Fin de Año y logística costosa de lanchas.",
                ],
            },
            "photos": photos_by_slug.get("punta-faro-mucura", []),
        },
        {
            "id": "poblado-covenas-tesoro",
            "rank": 9,
            "name": "Coveñas y Tolú (Hotel Poblado y Cabañas El Tesoro)",
            "chain": "Golfo de Morrosquillo, Sucre",
            "destination": "Coveñas y Tolú, Sucre",
            "regionGroup": "otros",
            "regionFilter": "covenas-mucura",
            "coords": [9.4136, -75.6761],
            "status": "sold_out",
            "statusLabel": "100% AGOTADO ONLINE (26 dic – 2 ene)",
            "badgeTone": "slate",
            "roomType": "Habitación Familiar / Cabaña Ecológica (Sin cupo web)",
            "officialUrl": "https://hotelpoblado.com/",
            "bookingUrl": "https://cabanaseltesoro.com/",
            "whatsapp": "+57 314 551 6564 (El Tesoro)",
            "antiScamNote": "Ambos motores oficiales (SynXis en Poblado y e-GDS en El Tesoro) muestran 0 cupos del 26 dic al 2 ene.",
            "proofKey": None,
            "pricing": {
                "nights7Total": None,
                "regular7Total": None,
                "savingsAmount": 0,
                "nightlyRates7": None,
                "preNye7Total": None,
                "jan7Total": None,
                "ivaIncludedText": "Aplica IVA 19% residentes + cena San Silvestre 31 dic",
                "mandatoryExtras": 0,
                "mandatoryExtrasLabel": "Cabañas El Tesoro cotiza paquetes fijos de Fin de Año por WhatsApp",
                "fits10M": False,
                "isAvailableNye": False,
            },
            "discount": {
                "hasDiscount": False,
                "badge": "Agotado en web Fin de Año",
                "detail": "Aunque ambos ofrecen Pensión Completa (Plan PA en Poblado y Plan Americano en El Tesoro), cerraron inventario web para Fin de Año.",
                "deadline": "Requiere consultar lista de espera o paquete directo por WhatsApp",
            },
            "cancellation": "Consultar condiciones directas por WhatsApp (+57 314 551 6564) o central Aviatur.",
            "meals": {
                "planName": "Pensión Completa (3 comidas buffet, sin barra libre)",
                "included": [
                    "Desayuno, almuerzo y cena buffet caribeña/nacional.",
                    "Acceso a piscinas, toboganes/zonas infantiles y playa privada.",
                ],
                "excluded": [
                    "No incluye barra libre ni licores.",
                ],
            },
            "activities": {
                "includedHotel": [
                    "Playa de aguas cálidas, muy mansas y poco profundas (de las más seguras de Colombia para niños).",
                    "Piscinas para adultos y niños, jacuzzis y recreación.",
                ],
                "kidsFriendly": [
                    "Ideal para niños pequeños fuera de la semana pico de diciembre por sus playas sin olas.",
                ],
            },
            "reviews": {
                "overall": "4.3 / 5",
                "sources": [
                    {"name": "Google", "score": "4.4 / 5"},
                    {"name": "Booking", "score": "8.1 / 10"},
                    {"name": "TripAdvisor", "score": "4.2 / 5"},
                ],
                "pros": [
                    "Aguas súper tranquilas para niños y ambiente familiar cercano.",
                ],
                "cons": [
                    "Completamente agotados en motores directos para la semana de Fin de Año.",
                ],
            },
            "photos": photos_by_slug.get("poblado-covenas-tesoro", []),
        },
        {
            "id": "on-vacation-san-andres",
            "rank": 10,
            "name": "On Vacation, Portobelo, Las Américas y Sol Caribe Campo",
            "chain": "Cadenas Agotadas en San Andrés",
            "destination": "San Andrés Isla (9+ propiedades)",
            "regionGroup": "san-andres",
            "regionFilter": "san-andres",
            "coords": [12.5560, -81.7060],
            "status": "sold_out",
            "statusLabel": "100% AGOTADOS ONLINE (Solo Hotel 26 dic – 2 ene)",
            "badgeTone": "slate",
            "roomType": "Toné, Blue Cove, Acantilado, Caribbean, Portobelo, Las Américas, El Dorado, Campo",
            "officialUrl": "https://www.onvacation.com/co/",
            "bookingUrl": "https://www.hotelamericas.com.co/",
            "whatsapp": "Motores oficiales verificados",
            "antiScamNote": "Auditados los 9 hoteles On Vacation/Portobelo, Sol Caribe Campo, Hotel El Dorado, Hotel Las Américas, Decameron Marazul/San Luis y GHL Sunrise: todos sin cupo online para los 4.",
            "proofKey": "las-americas-agotado.png",
            "pricing": {
                "nights7Total": None,
                "regular7Total": None,
                "savingsAmount": 0,
                "nightlyRates7": None,
                "preNye7Total": 11839177,
                "jan7Total": None,
                "ivaIncludedText": "Referencia Hotel Las Américas días previos dic: $1.691.311/noche (Plan Full)",
                "mandatoryExtras": 584000,
                "mandatoryExtrasLabel": "4 Tarjetas OCCRE (~$146.000 × 4)",
                "fits10M": False,
                "isAvailableNye": False,
            },
            "discount": {
                "hasDiscount": False,
                "badge": "Agotados Fin de Año online",
                "detail": "Hotel Las Américas se bloquea justo el 1 de enero; On Vacation cierra cupo Solo Hotel en San Andrés para Año Nuevo (solo vía chárter telefónico).",
                "deadline": "Sin inventario web directo",
            },
            "cancellation": "N/A (sin cupo web disponible).",
            "meals": {
                "planName": "Todo Incluido / Plan Full (según propiedad)",
                "included": [
                    "Desayuno, almuerzo, cena y barra libre según cadena.",
                ],
                "excluded": [
                    "Sin disponibilidad directa en motores web para 26 dic – 2 ene.",
                ],
            },
            "activities": {
                "includedHotel": [
                    "Piscinas, tobogán al mar en Blue Cove (cerrado en fecha), ubicación céntrica en Toné / Las Américas.",
                ],
                "kidsFriendly": [
                    "Se dejan como referencia para confirmar a tu esposa que ya revisamos toda la isla.",
                ],
            },
            "reviews": {
                "overall": "3.7–4.2 / 5",
                "sources": [
                    {"name": "Toné / Cove", "score": "3.7 / 5"},
                    {"name": "Las Américas", "score": "4.1 / 5"},
                    {"name": "Sol Campo", "score": "4.3 / 5"},
                ],
                "pros": [
                    "Opciones populares cuando se consiguen en temporada baja o media.",
                ],
                "cons": [
                    "Agotados en Fin de Año; reseñas de On Vacation reportan buffet básico y filas largas.",
                ],
            },
            "photos": attach_proof("on-vacation-san-andres", "las-americas-agotado.png", "Captura oficial SynXis: Hotel Las Américas bloqueado el 1 de enero de 2027"),
        },
    ]

    san_andres_landmarks = [
        {"name": "🏖️ Playa Spratt Bight (Playa Principal)", "coords": [12.5858, -81.6952], "note": "Arena blanca y mar tranquilo ideal para niños (a 4–5 min a pie de Sol Caribe, Arena Blanca y Grand Sirenis)."},
        {"name": "⛵ Muelle Portofino (Lanchas a Johnny Cay y Acuario)", "coords": [12.5813, -81.6914], "note": "Punto de salida a los cayos (~$50k + $15k tasa ecológica/pers.)."},
        {"name": "✈️ Aeropuerto Internacional Gustavo Rojas Pinilla (ADZ)", "coords": [12.5836, -81.7112], "note": "A 5–8 min en taxi de todos los hoteles del centro."},
    ]

    timeline = [
        {
            "date": "18 Nov 2026",
            "urgent": True,
            "title": "Cierre promo Black Days 2×1 On Vacation (-50% OFF)",
            "detail": "Wayira Beach (Mayapo) cae a $4.550.014 COP por 7 noches en enero para los 4; en Fin de Año ya está agotado en web.",
        },
        {
            "date": "26 Nov 2026",
            "urgent": True,
            "title": "Límite cancelación gratuita — Grand Sirenis San Andrés",
            "detail": "Último día para cancelar sin costo la Junior Presidential Suite ($28.560.000 COP).",
        },
        {
            "date": "11 Dic 2026",
            "urgent": False,
            "title": "Límite cancelación gratuita — Hotel Sol Caribe San Andrés",
            "detail": "Puedes bloquear hoy tu cupo con VIP Club -5% ($13.067.250 por 7N o $9.008.850 por 5N) y cancelar sin penalidad hasta el 11 de diciembre.",
        },
        {
            "date": "23 Dic 2026",
            "urgent": False,
            "title": "Límite cancelación gratuita — Decameron Maryland Black Days Flex",
            "detail": "Ahorras $9,47M con Black Days No Reembolsable ($14.664.747) o aseguras cancelación gratis hasta 72h antes con Black Days Flex ($16.093.000).",
        },
        {
            "date": "Lo antes posible",
            "urgent": True,
            "title": "Cupo limitado en Capurganá (Las Mañanitas) y Bahía Solano (El Almejal)",
            "detail": "Las Mañanitas ($10.010.000 los 7 días con 3 tours) requiere bloqueo por WhatsApp; El Almejal ($8.940.000 por 5 noches) ya tiene pocas cabañas familiares.",
        },
    ]

    payload = {
        "generatedAt": "2026-11-16",
        "budgetDefault": 10000000,
        "family": "2 adultos + 2 niños (7 y 10 años)",
        "targetDates": "26 dic 2026 – 2 ene 2027",
        "hotels": hotels,
        "landmarks": san_andres_landmarks,
        "timeline": timeline,
    }

    OUT_JS_PATH.write_text(
        "window.VACATION_DATA = " + json.dumps(payload, indent=2, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT_JS_PATH} with {len(hotels)} hotels.")


if __name__ == "__main__":
    main()
