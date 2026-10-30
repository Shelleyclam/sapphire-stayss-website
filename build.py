#!/usr/bin/env python3
"""Builds the Sapphire Stayss website.

Reads content/site.json and writes every HTML page, sitemap.xml and robots.txt into public/.
public/ is the finished website: upload its contents to the hosting's public_html folder.

Run:  python3 build.py
Needs only Python 3.8+. If Pillow is installed, image sizes are added to <img> tags.
"""
import html
import json
import os
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "public")

with open(os.path.join(ROOT, "content", "site.json"), encoding="utf-8") as f:
    DATA = json.load(f)

B = DATA["business"]
ROOMS = DATA["rooms"]
BOOKING_URL = DATA["booking"]["url"].strip()
TODAY = date.today().isoformat()


def version(rel):
    """Short content hash, added to CSS/JS links so browsers fetch the new file after each change."""
    import hashlib
    with open(os.path.join(OUT, rel), "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]

try:
    from PIL import Image
except ImportError:  # sizes are optional
    Image = None


def e(text):
    return html.escape(str(text), quote=True)


def rupees(n):
    s = str(n)
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts) + "," + tail
    return "₹" + s


def km(d):
    return f"{int(d * 1000)} m" if d < 1 else f"{d:g} km"


def sleeps(room):
    return f"{room['adults']} adults"


def short(room):
    return room.get("short_name", room["name"])


TRAVEL = DATA["travel"]


def todo(text):
    """A fact the owner still has to give us. Shown as a yellow mark so it can't ship unnoticed;
    main() lists every one left after the build."""
    return f'<mark class="todo">TODO: {text}</mark>'


def site_alt(cap):
    """Alt text that says where the photo is, for search engines and screen readers."""
    return cap if ("Sapphire" in cap or "Yelagiri" in cap) else f"{cap}, Sapphire Stayss, Yelagiri"


def nap(sep=",<br>"):
    """Name, address and phones: the same wording on every page."""
    return (f"{e(B['name'])}{sep}{e(B['address_line'])}{sep}{e(B['region'])} {e(B['postcode'])}, India")


def travel_check():
    return "" if TRAVEL["verified"] else " " + todo("check this distance and time against your own Google Maps route to the resort")


def img_size(name):
    if not Image:
        return ""
    path = os.path.join(OUT, "img", name + ".webp")
    try:
        with Image.open(path) as im:
            return f' width="{im.width}" height="{im.height}"'
    except OSError:
        return ""


def img(p, name, alt, sizes="100vw", lazy=True, cls=""):
    """Responsive <img> with an 800px and a 1600px version."""
    attrs = f' class="{cls}"' if cls else ""
    loading = ' loading="lazy" decoding="async"' if lazy else ' fetchpriority="high"'
    return (f'<img src="{p}img/{name}-sm.webp" srcset="{p}img/{name}-sm.webp 800w, {p}img/{name}.webp 1600w" '
            f'sizes="{sizes}" alt="{e(alt)}"{img_size(name)}{loading}{attrs}>')


def wa(text=""):
    from urllib.parse import quote
    return f"https://wa.me/{B['phone_whatsapp_raw']}" + (f"?text={quote(text)}" if text else "")


def book_href(p, room=None):
    """Where Book buttons go: the booking page once it exists, otherwise our enquiry form."""
    if BOOKING_URL:
        return e(BOOKING_URL)
    return f"{p}contact.html" + (f"?room={room['slug']}" if room else "") + "#enquiry"


NAV = [
    ("index.html", "Home", "home"),
    ("about.html", "About", "about"),
    ("rooms.html", "Rooms", "rooms"),
    ("gallery.html", "Gallery", "gallery"),
    ("explore.html", "Explore Yelagiri", "explore"),
    ("faq.html", "FAQ", "faq"),
    ("contact.html", "Contact", "contact"),
]


def header(p, current):
    current_attr = ' aria-current="page"'
    links = "\n".join(
        f'        <a href="{p}{href}"{current_attr if key == current else ""}>{label}</a>'
        for href, label, key in NAV
    )
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-header wrap">
  <div class="topbar">
    <a class="brand" href="{p}index.html" aria-label="Sapphire Stayss home"><img src="{p}img/logo.png" alt="Sapphire Stayss, where serenity reigns" width="600" height="135"></a>
    <button class="menu-btn" id="menu-btn" type="button" aria-label="Menu" aria-expanded="false" aria-controls="site-nav"><span></span><span></span><span></span></button>
    <nav class="nav" id="site-nav" aria-label="Main">
{links}
        <a class="btn" href="{book_href(p)}">Book now</a>
    </nav>
  </div>
</header>"""


def book_band(p):
    """Booking call-to-action shown above the footer on every page."""
    return f"""<section class="book-band" aria-labelledby="book-band-title">
  <div class="wrap">
    <h2 id="book-band-title">Book your stay in Yelagiri</h2>
    <p>Call or WhatsApp <a href="tel:+{B['phone_whatsapp_raw']}">{e(B['phone_whatsapp'])}</a> or <a href="tel:+{B['phone_other_raw']}">{e(B['phone_other'])}</a>, or email <a href="mailto:{e(B['email'])}">{e(B['email'])}</a>.</p>
    <div class="btn-row"><a class="btn" href="{wa('Hi, I would like to book a stay at Sapphire Stayss.')}" target="_blank" rel="noopener">WhatsApp us</a><a class="btn btn-line" href="{book_href(p)}">Check availability</a></div>
  </div>
</section>"""


def footer(p):
    return f"""{book_band(p)}
<footer class="site-footer">
  <div class="wrap foot">
    <div>
      <img src="{p}img/logo.png" alt="Sapphire Stayss" width="600" height="135" loading="lazy">
      <address>{nap()}</address>
    </div>
    <div>
      <h2>Contact</h2>
      <ul>
        <li><a href="tel:+{B['phone_whatsapp_raw']}">{e(B['phone_whatsapp'])}</a> (WhatsApp)</li>
        <li><a href="tel:+{B['phone_other_raw']}">{e(B['phone_other'])}</a></li>
        <li><a href="mailto:{e(B['email'])}">{e(B['email'])}</a></li>
      </ul>
    </div>
    <div>
      <h2>Stay</h2>
      <ul>
        <li><a href="{p}rooms.html">Rooms &amp; prices</a></li>
        <li><a href="{p}gallery.html">Gallery</a></li>
        <li><a href="{p}explore.html">Things to do in Yelagiri</a></li>
        <li><a href="{p}faq.html">Policies &amp; FAQ</a></li>
        <li><a href="{p}yelagiri-from-bangalore.html">From Bangalore</a></li>
        <li><a href="{p}yelagiri-from-chennai.html">From Chennai</a></li>
      </ul>
    </div>
    <div>
      <h2>Follow</h2>
      <ul>
        <li><a href="{e(B['instagram'])}" target="_blank" rel="noopener">Instagram</a></li>
        <li><a href="{e(B['maps_url'])}" target="_blank" rel="noopener">Google Maps &amp; reviews</a></li>
        <li><a href="{p}about.html">About us</a></li>
      </ul>
    </div>
  </div>
  <div class="wrap copy">
    <span>© {B['year']} {e(B['name'])}. All rights reserved.</span>
    <span><a href="{p}terms.html">Terms</a> · <a href="{p}privacy.html">Privacy</a> · <a href="{p}refund-policy.html">Cancellation &amp; refunds</a></span>
  </div>
</footer>
<a class="wa-float" href="{wa()}" target="_blank" rel="noopener">WhatsApp us</a>"""


LIGHTBOX = """<div class="lightbox" id="lightbox" hidden role="dialog" aria-modal="true" aria-label="Photo viewer">
  <div class="lightbox-bar"><span class="lightbox-caption"></span><button type="button" data-close aria-label="Close">✕</button></div>
  <div class="lightbox-stage"><img src="" alt=""></div>
  <div class="lightbox-nav"><button type="button" data-prev aria-label="Previous photo">←</button><button type="button" data-next aria-label="Next photo">→</button></div>
</div>"""


def url(path):
    return B["site_url"] + "/" + ("" if path == "index.html" else path)


def breadcrumbs(trail):
    """trail: [(name, path), ...] after Home."""
    items = [("Home", "index.html")] + trail
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": url(u)} for i, (n, u) in enumerate(items)]}


def page(path, title, description, content, current="", jsonld=None, crumbs=None, image="home/hero-swamymalai",
         lightbox=False, head_extra=""):
    depth = path.count("/")
    p = "../" * depth
    canonical = url(path)
    graph = [hotel_jsonld()] + (jsonld or [])
    if crumbs:
        graph.append(breadcrumbs(crumbs))
    ld = ('\n<script type="application/ld+json">' +
          json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "</script>")
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(B['name'])}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{B['site_url']}/img/{image}.webp">
<meta name="theme-color" content="#FCFBF9">
<link rel="icon" type="image/png" href="{p}img/favicon.png">
<link rel="apple-touch-icon" href="{p}img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Marcellus&family=Jost:wght@400;500&display=swap">
<link rel="stylesheet" href="{p}css/style.css?v={version('css/style.css')}">{head_extra}{ld}
</head>
<body data-booking-url="{e(BOOKING_URL)}" data-whatsapp="{B['phone_whatsapp_raw']}">
<!-- Generated by build.py from content/site.json. Edit those, not this file. -->
{header(p, current)}
<main id="main">
{content(p)}
</main>
{footer(p)}
{LIGHTBOX if lightbox else ""}
<script src="{p}js/main.js?v={version('js/main.js')}" defer></script>
</body>
</html>
"""
    out = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    return path


def availability_form(p, room=None, boxed=False):
    """Dates + guests. Sends the guest to the booking page, or to our enquiry form with the details filled in."""
    most = room["adults"] if room else 12
    options = "".join(f'<option value="{n}"{" selected" if n == 2 else ""}>{n}</option>' for n in range(1, most + 1))
    uid = room["slug"] if room else "home"
    room_field = f'<input type="hidden" name="room" value="{room["slug"]}">' if room else ""
    return f"""<form class="booking{' boxed' if boxed else ''}" action="{p}contact.html#enquiry" method="get" data-availability aria-label="Check availability">
    {room_field}<div class="field"><label for="in-{uid}">Check-in</label><input id="in-{uid}" name="checkin" type="date" required></div>
    <div class="field"><label for="out-{uid}">Check-out</label><input id="out-{uid}" name="checkout" type="date" required></div>
    <div class="field"><label for="g-{uid}">Guests</label><select id="g-{uid}" name="guests">{options}</select></div>
    <button class="btn" type="submit">Check availability</button>
  </form>"""


def room_card(p, room, in_strip=True):
    photo, alt = room["photos"][0]
    sizes = "(max-width: 560px) 80vw, 360px" if in_strip else "(max-width: 560px) 100vw, (max-width: 920px) 50vw, 400px"
    summary = "" if in_strip else f'\n      <p class="summary">{e(room["summary"])}</p>'
    return f"""<a class="room-card" href="{p}rooms/{room['slug']}.html">
      <div class="img">{img(p, photo, site_alt(alt), sizes)}</div>
      <span class="room-tag">{e(room['tag'])}</span>
      <div class="room-top"><h3>{e(short(room) if in_strip else room['name'])}</h3></div>{summary}
      <div class="room-meta"><span>{e(room['beds_short'])} · {e(sleeps(room))}</span><b>{rupees(room['price'])}</b></div>
    </a>"""


HOTEL_ID = B["site_url"] + "/#hotel"


def amenities():
    """Hotel amenities for the schema and llms.txt. The pool is only listed once the owner confirms it."""
    names = DATA["room_amenities"] + ["Garden", "Glass-walled dining room", "Children's swing"]
    if B["pool"]:
        names.append("Swimming pool")
    return names


def hotel_jsonld():
    prices = [r["price"] for r in ROOMS]
    geo = B["geo"]
    extra = {}
    if geo["latitude"] and geo["longitude"]:
        extra["geo"] = {"@type": "GeoCoordinates", "latitude": geo["latitude"], "longitude": geo["longitude"]}
    h = {
        "@type": "Hotel",
        "@id": HOTEL_ID,
        "name": B["name"],
        "description": ("A small garden resort with " + str(sum(r["units"] for r in ROOMS)) +
                        " rooms in Mangalam, Yelagiri Hills, Tamil Nadu, at the foot of Swamymalai. "
                        "Air-conditioned rooms and a private villa, complimentary South Indian breakfast, free Wi-Fi and parking."),
        "slogan": B["tagline"],
        "url": B["site_url"] + "/",
        "image": [B["site_url"] + "/img/home/hero-swamymalai.webp", B["site_url"] + "/img/home/evening-exterior.webp"],
        "logo": B["site_url"] + "/img/logo.png",
        "telephone": B["phone_whatsapp"],
        "email": B["email"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": B["address_line"],
            "addressLocality": B["locality"],
            "addressRegion": B["region"],
            "postalCode": B["postcode"],
            "addressCountry": B["country"],
        },
        **extra,
        "hasMap": B["maps_url"],
        "sameAs": [B["instagram"]] + [u for u in [B["google_business_url"]] + B["same_as"] if u],
        "priceRange": f"{rupees(min(prices))} – {rupees(max(prices))} per night",
        "currenciesAccepted": "INR",
        "checkinTime": "12:00",
        "checkoutTime": "12:00",
        "numberOfRooms": sum(r["units"] for r in ROOMS),
        "petsAllowed": {"yes": True, "no": False}.get(B["pets"].lower()) if B["pets"] else None,
        "amenityFeature": [
            {"@type": "LocationFeatureSpecification", "name": n, "value": True} for n in amenities()
        ],
    }
    return {k: v for k, v in h.items() if v is not None}


def room_jsonld(room):
    return {
        "@type": "HotelRoom",
        "@id": url(f"rooms/{room['slug']}.html") + "#room",
        "name": room["name"],
        "url": url(f"rooms/{room['slug']}.html"),
        "description": room["summary"],
        "bed": room["beds"],
        "floorSize": {"@type": "QuantitativeValue", "value": room["size_m2"], "unitCode": "MTK"},
        "occupancy": {"@type": "QuantitativeValue", "maxValue": room["adults"],
                      "description": f"Up to {room['adults']} adults and {room['children']} children"},
        "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True}
                           for n in room["features"] + DATA["room_amenities"]],
        "image": B["site_url"] + f"/img/{room['photos'][0][0]}.webp",
        "containedInPlace": {"@id": HOTEL_ID},
        "offers": {
            "@type": "Offer",
            "url": url(f"rooms/{room['slug']}.html"),
            "priceCurrency": "INR",
            "price": room["price"],
            "priceSpecification": {"@type": "UnitPriceSpecification", "price": room["price"],
                                   "priceCurrency": "INR", "unitText": "per night, breakfast included"},
            "seller": {"@id": HOTEL_ID},
        },
    }


# ---------------------------------------------------------------- Home

def review_by(r):
    """'Vasy · Chennai · March 2026 · Google', skipping whatever we don't have."""
    return " · ".join(e(x) for x in [r["name"], r.get("city"), r.get("month"), r["source"]] if x)


def home(p):
    cards = "\n    ".join(room_card(p, r) for r in ROOMS)
    rv = DATA["reviews"]
    more = "\n      ".join(
        f'<figure><blockquote>“{e(r["quote"])}”</blockquote><figcaption>{review_by(r)}</figcaption></figure>'
        for r in rv[1:]
    )
    review_us = (f'<a class="link" href="{e(B["google_review_url"])}" target="_blank" rel="noopener">Review us on Google</a>'
                 if B["google_review_url"] else todo("add your Google review link (google_review_url) for a “Review us on Google” button"))
    stops = [(0, "Sapphire Stayss", True), (0.5, "Swamymalai trek starts, right behind us", False),
             (1, "Selfie Panda &amp; Chocolate Factory", False), (1.5, "Murugan (Velavan) Temple", False),
             (2, "Fundera Park", False), (2.5, "Nilavoor View Point", False),
             (3.5, "Boat House &amp; Nature Park", False), (4, "Mountain View Adventure Park", False)]
    road = "\n        ".join(
        f'<div class="stop{" home" if h else ""}" style="top:{int(d * 60)}px"><b>{"0 km" if d == 0 else km(d)}</b>{label}</div>'
        for d, label, h in stops
    )
    return f"""<div class="wrap">
  <section class="hero" aria-label="Welcome">
    <div class="hero-text">
      <h1><span class="label">Sapphire Stayss · Resort in Yelagiri Hills, Tamil Nadu</span>Where serenity reigns</h1>
      <p>Tucked away in Mangalam at the foot of Swamymalai, Yelagiri's highest hill, with green slopes all around, cool air and a calm you can hear.</p>
    </div>
    <figure class="hero-photo">
      <picture>
        <source media="(max-width: 920px)" srcset="{p}img/home/hero-swamymalai-m.webp">
        <source media="(max-width: 1100px)" srcset="{p}img/home/hero-swamymalai-sm.webp 1000w, {p}img/home/hero-swamymalai.webp 1600w" sizes="100vw">
        <img src="{p}img/home/hero-swamymalai.webp" alt="Forested hills and the plains below, seen from the top of Swamymalai" width="1600" height="685" fetchpriority="high">
      </picture>
      <figcaption>The view from Swamymalai, 500 m from our gate</figcaption>
    </figure>
  </section>
  {availability_form(p)}
</div>

<section class="wrap section intro" aria-label="About">
  <p class="intro-lead">Fourteen hairpin bends up from the plains, the air cools and the traffic fades. Evenings here end by the campfire.</p>
  <dl class="facts">
    <div><dt>Foothills</dt><dd>At the foot of Swamymalai, with the trek starting 500 m away</dd></div>
    <div><dt>Breakfast</dt><dd>Complimentary South Indian breakfast for every guest</dd></div>
    <div><dt>AC</dt><dd>In every room, with TV, Wi-Fi, kettle and hot water</dd></div>
    <div><dt>12 noon</dt><dd>Check-in and check-out, so you get a full day</dd></div>
  </dl>
</section>

<section class="section tight-top" id="rooms" aria-labelledby="rooms-title">
  <div class="wrap">
    <div class="rooms-head">
      <div><span class="label">Stay</span><h2 class="big" id="rooms-title">The rooms</h2></div>
      <p>Per night, breakfast included.</p>
      <div class="strip-ctrl">
        <button type="button" id="strip-prev" aria-label="Previous room">←</button>
        <button type="button" id="strip-next" aria-label="Next room">→</button>
      </div>
    </div>
    <div class="strip" id="strip" tabindex="0" aria-label="Room types">
    {cards}
    </div>
    <p style="margin-top:22px"><a class="link" href="{p}rooms.html">Compare all rooms</a></p>
  </div>
</section>

<section class="wrap section tight-top" aria-labelledby="garden-title">
  <div class="split-head">
    <div><span class="label">The property</span><h2 class="big" id="garden-title">A garden to come back to</h2></div>
    <a class="link" href="{p}gallery.html">See the gallery</a>
  </div>
  <div class="trio">
    <figure>{img(p, "home/evening-exterior", "Sapphire Stayss lit up in the evening", "(max-width: 560px) 100vw, 40vw")}<figcaption>Evenings at Sapphire Stayss</figcaption></figure>
    <figure>{img(p, "property/garden-swing", "Garden path with a children's swing", "(max-width: 560px) 50vw, 30vw")}<figcaption>Swings for the children</figcaption></figure>
    <figure>{img(p, "property/garden-pergola", "Pergola covered in green creepers", "(max-width: 560px) 50vw, 30vw")}<figcaption>Shade under the pergola</figcaption></figure>
  </div>
</section>

<section class="wrap section tight-top" id="day" aria-labelledby="day-title">
  <span class="label">Ideas for your stay</span>
  <h2 class="big" id="day-title">Noon to noon</h2>
  <p class="lead">Check-in and check-out are both at 12 noon, so even one night gives you a full afternoon, evening and morning in the hills. Here's what your day could look like. These are only suggestions; spend it however you like. Anything marked "On request" is something we can arrange for you.</p>
  <div style="margin-top:clamp(24px, 3vw, 36px)">
  <div class="moment">
    <time>12:00<small>Arrive</small></time>
    <div><h3>Settle in</h3><p>Your room is ready at noon: air-conditioning, fresh linen, a kettle with tea and coffee, and a terrace over the garden.</p></div>
    {img(p, "home/room-detail", "Grey velvet sofa beside a padded headboard", "(max-width: 920px) 100vw, 45vw")}
  </div>
  <div class="moment compact">
    <time>14:30<small>Afternoon</small></time>
    <div><h3>Boating or adventure parks</h3><p>Take a boat out on Punganoor Lake at the Boat House, or spend the afternoon at Thrill Valley, Lake Zone or Wild Waves. All are about 3.5 km away. With children? Fundera bird park is 2 km away.</p></div>
  </div>
  <div class="moment compact">
    <time>17:00<small>Late afternoon</small></time>
    <div><h3>Views from Nilavoor</h3><p>Drive 2.5 km to Nilavoor View Point for wide views over the hills and valley as the day cools down.</p></div>
  </div>
  <div class="moment compact">
    <time>19:00<small>Evening</small></time>
    <div><h3>Fountain show at the lake</h3><p>The musical fountain at the Nature Park, opposite the Boat House, starts at 7 PM every day. It is 3.5 km from us.</p></div>
  </div>
  <div class="moment">
    <time>20:30<small>Night</small></time>
    <div><h3>Campfire in the garden</h3><p>End the day around a campfire in the garden. Let us know a day ahead and we will set it up; there is an extra charge. Celebrating? We can also arrange a cake and decorate your room.</p><span class="tag">On request · extra charge</span></div>
    {img(p, "home/campfire", "Campfire in the garden seating area at night", "(max-width: 920px) 100vw, 45vw")}
  </div>
  <div class="moment">
    <time>06:30<small>Early morning</small></time>
    <div><h3>Climb Swamymalai</h3><p>The trek to Swamymalai, the highest point in Yelagiri, starts just 500 m behind the resort. Set off early for cool air and clear views, and be back in time for breakfast.</p><span class="tag">Starts behind the resort</span></div>
    {img(p, "home/swamymalai-view", "View over forested hills and the plains from the top of Swamymalai", "(max-width: 920px) 100vw, 45vw")}
  </div>
  <div class="moment morning">
    <time>08:30<small>Morning</small></time>
    <div><h3>Breakfast is on us</h3><p>Soft idly, coconut chutney and sambar in the glass-walled dining room, with the garden outside. Served {B['breakfast_time']}, complimentary for every guest.</p></div>
    <div class="pair">
      {img(p, "home/dining", "Glass-walled dining room looking onto the garden", "(max-width: 920px) 60vw, 28vw")}
      {img(p, "home/breakfast-idly", "Idly with chutney and sambar on a banana leaf", "(max-width: 920px) 40vw, 18vw")}
    </div>
  </div>
  <div class="moment compact">
    <time>10:30<small>Before you leave</small></time>
    <div><h3>Chocolates and one last stop</h3><p>Pick up homemade chocolates at the Chocolate Factory and Selfie Panda, 1 km away, or visit the Murugan Temple at 1.5 km. Check-out is at 12 noon.</p></div>
  </div>
  </div>
</section>

<section class="wrap section tight-top" aria-labelledby="about-title">
  <div class="about-band">
    {img(p, "property/garden-bench", "Garden bench under the trees at Sapphire Stayss", "(max-width: 920px) 100vw, 45vw")}
    <div>
      <span class="label">About us</span>
      <h2 class="big" id="about-title">A small stay, looked after personally</h2>
      <p class="lead">{e(ABOUT_SHORT)}</p>
      <p style="margin-top:22px"><a class="link" href="{p}about.html">Our story</a></p>
    </div>
  </div>
</section>

<section class="wrap section tight-top reviews" id="reviews" aria-label="Guest reviews">
  <span class="label">Guests on Google &amp; Tripadvisor</span>
  <p class="quote">“{e(rv[0]['quote'])}”</p>
  <p class="quote-by">{review_by(rv[0])}</p>
  <div class="more-quotes">
      {more}
  </div>
  <p class="small-print">{todo("paste more real guest reviews into content/site.json → reviews, with first name, city and month of stay (quote, name, city, month, source). Only real reviews, copied word for word.")}</p>
  <div class="btn-row" style="justify-content:center"><a class="link" href="{e(B['maps_url'])}" target="_blank" rel="noopener">All reviews on Google</a>{review_us}</div>
</section>

<section class="wrap section tight-top where" id="where" aria-labelledby="where-title">
  <div>
    <span class="label">Location</span>
    <h2 class="big" id="where-title">Mangalam, Yelagiri</h2>
    <address>{nap(", ")}</address>
    <div class="btn-row">
      <a class="btn btn-line" href="{e(B['maps_url'])}" target="_blank" rel="noopener">Get directions</a>
      <a class="link" href="{p}explore.html">Things to do</a>
    </div>
    <p class="small-print">Driving up? See the routes <a href="{p}yelagiri-from-bangalore.html">from Bangalore</a> ({e(TRAVEL['bangalore']['km'])}) and <a href="{p}yelagiri-from-chennai.html">from Chennai</a> ({e(TRAVEL['chennai']['km'])}).</p>
  </div>
  <div>
    <span class="label">From our gate, to scale</span>
    <div class="road" aria-label="Distances from Sapphire Stayss">
        {road}
    </div>
    <p class="road-far"><b>40 km</b>Jalagamparai Waterfalls, a half-day trip</p>
  </div>
</section>"""


# ---------------------------------------------------------------- Rooms

def rooms_page(p):
    cards = "\n    ".join(room_card(p, r, in_strip=False) for r in ROOMS)
    amen = "".join(f"<li>{e(a)}</li>" for a in DATA["room_amenities"])
    rows = "\n      ".join(
        f'<tr><th scope="row"><a href="{p}rooms/{r["slug"]}.html">{e(r["name"])}</a></th><td>{e(r["beds"])}</td>'
        f'<td>{r["adults"]} adults + {r["children"]} {"child" if r["children"] == 1 else "children"}</td>'
        f'<td>{r["size_m2"]} m² ({r["size_sqft"]} sq ft)</td><td>{e(r["views"])}</td><td>{r["units"]}</td>'
        f'<td>From {rupees(r["price"])}</td></tr>'
        for r in ROOMS)
    total = sum(r["units"] for r in ROOMS)
    return f"""<section class="wrap page-head">
  <span class="label">Stay</span>
  <h1>Rooms &amp; prices in Yelagiri</h1>
  <p>{total} rooms in {len(ROOMS)} types at Sapphire Stayss, Mangalam, Yelagiri, from {rupees(min(r['price'] for r in ROOMS))} to {rupees(max(r['price'] for r in ROOMS))} a night. Every stay includes breakfast.</p>
</section>
<section class="wrap section">
  <div class="room-grid">
    {cards}
  </div>
</section>
<section class="wrap section tight-top" aria-labelledby="compare-title">
  <h2 class="big" id="compare-title" style="margin-bottom:20px">Compare the rooms</h2>
  <div class="table-wrap">
    <table class="table">
      <thead><tr><th scope="col">Room</th><th scope="col">Beds</th><th scope="col">Sleeps</th><th scope="col">Size</th><th scope="col">View</th><th scope="col">Rooms</th><th scope="col">Per night</th></tr></thead>
      <tbody>
      {rows}
      </tbody>
    </table>
  </div>
  <p class="small-print" style="margin-top:14px">Prices are per room per night in Indian Rupees and include breakfast for every guest. {todo("say whether these prices include GST, and whether weekend or holiday rates are higher")}</p>
</section>
<section class="wrap section tight-top">
  <div class="highlight-box">
    <div>
      <h2>In every room</h2>
      <ul class="ticks">{amen}</ul>
    </div>
    <div>
      <p>Check-in and check-out are at {B['check_in']}. A {B['advance_percent']}% advance confirms your booking and the rest is paid at check-in. Free cancellation up to {B['free_cancellation_days']} days before arrival.</p>
      <p style="margin-top:18px"><a class="link" href="{p}faq.html">Policies &amp; FAQ</a></p>
    </div>
  </div>
</section>"""


def room_page(room):
    def content(p):
        btns = "\n      ".join(
            f'<button type="button" data-lightbox="room" data-full="{p}img/{ph}.webp" data-caption="{e(alt)}">{img(p, ph, site_alt(alt), "(max-width: 920px) 100vw, 60vw" if i == 0 else "(max-width: 920px) 50vw, 30vw", lazy=i > 0)}</button>'
            for i, (ph, alt) in enumerate(room["photos"])
        )
        feats = "".join(f"<li>{e(x)}</li>" for x in room["features"] + DATA["room_amenities"])
        others = [r for r in ROOMS if r["slug"] != room["slug"]][:3]
        other_cards = "\n    ".join(room_card(p, r, in_strip=False) for r in others)
        units = "" if room["units"] == 1 else f'<div><dt>Rooms</dt><dd>{room["units"]} rooms of this type</dd></div>'
        return f"""<section class="wrap page-head">
  <p class="crumbs"><a href="{p}index.html">Home</a> / <a href="{p}rooms.html">Rooms</a> / {e(short(room))}</p>
  <span class="label">{e(room['tag'])}</span>
  <h1>{e(room['name'])}</h1>
  <p>{e(room['summary'])}</p>
</section>
<section class="wrap section">
  <div class="room-detail">
    <div class="photos">
      {btns}
    </div>
    <aside class="room-aside">
      <div class="price-big">{rupees(room['price'])}<small>per night, breakfast included</small></div>
      <dl class="spec">
        <div><dt>Beds</dt><dd>{e(room['beds'])}</dd></div>
        <div><dt>Sleeps</dt><dd>Up to {e(sleeps(room))} and {room['children']} {"child" if room['children'] == 1 else "children"}</dd></div>
        <div><dt>Size</dt><dd>{room['size_m2']} m² ({room['size_sqft']} sq ft)</dd></div>
        <div><dt>View</dt><dd>{e(room['views'])}</dd></div>
        {units}
      </dl>
      {availability_form(p, room, boxed=True)}
      <p class="small-print">{B['advance_percent']}% advance to confirm, balance at check-in. Free cancellation up to {B['free_cancellation_days']} days before arrival. <a href="{p}faq.html">Policies</a></p>
    </aside>
  </div>
</section>
<section class="wrap section tight-top">
  <h2 class="big" style="margin-bottom:20px">What's included</h2>
  <ul class="ticks">{feats}</ul>
</section>
<section class="wrap section tight-top">
  <div class="split-head"><h2 class="big">Other rooms</h2><a class="link" href="{p}rooms.html">All rooms</a></div>
  <div class="room-grid">
    {other_cards}
  </div>
</section>"""
    return content


# ---------------------------------------------------------------- Gallery

def orientation(name):
    """'w' for wide photos, 't' for tall ones, '' for roughly square (needs Pillow)."""
    if not Image:
        return ""
    with Image.open(os.path.join(OUT, "img", name + "-sm.webp")) as im:
        r = im.width / im.height
    return "w" if r > 1.2 else "t" if r < 0.83 else ""


def gallery_page(p):
    cats = [("property", "Garden & property"), ("rooms", "Rooms"), ("dining", "Dining"), ("evenings", "Evenings")]
    counts = {k: sum(1 for c, _, _ in DATA["gallery"] if c == k) for k, _ in cats}
    btns = f'<button type="button" data-filter="all" aria-pressed="true">All <span>{len(DATA["gallery"])}</span></button>' + "".join(
        f'<button type="button" data-filter="{k}" aria-pressed="false">{v} <span>{counts[k]}</span></button>' for k, v in cats)
    seen = set()
    figs = []
    for cat, name, cap in DATA["gallery"]:
        shape = "big" if cat not in seen else orientation(name)
        seen.add(cat)
        figs.append(
            f'<figure class="{shape}" data-cat="{cat}"><button type="button" data-lightbox="gallery" data-full="{p}img/{name}.webp" data-caption="{e(cap)}" aria-label="View larger: {e(cap)}">'
            f'{img(p, name, site_alt(cap), "(max-width: 700px) 50vw, 33vw")}</button><figcaption>{e(cap)}</figcaption></figure>')
    figs = "\n    ".join(figs)
    return f"""<section class="wrap page-head">
  <span class="label">Gallery</span>
  <h1>Photos of Sapphire Stayss</h1>
  <p>The garden, the rooms, breakfast and our evenings. Tap any photo to see it larger.</p>
</section>
<section class="wrap section">
  <div class="filters gallery-filters" role="group" aria-label="Filter photos">{btns}</div>
  <div class="bento">
    {figs}
  </div>
  <div class="gallery-cta">
    <p>Like what you see?</p>
    <div class="btn-row"><a class="btn" href="{book_href(p)}">Check availability</a><a class="btn btn-line" href="{p}rooms.html">See the rooms</a></div>
  </div>
</section>"""


# ---------------------------------------------------------------- Explore

def maps_search(name):
    from urllib.parse import quote
    return "https://www.google.com/maps/search/?api=1&query=" + quote(name + ", Yelagiri")


ORIGIN = "Sapphire Stayss, Mangalam, Yelagiri"


def place_card(it, cats):
    from urllib.parse import quote
    directions = ("https://www.google.com/maps/dir/?api=1&origin=" + quote(ORIGIN) +
                  "&destination=" + quote(it["maps"]))
    times = " ".join(it["times"])
    must = it.get("must")
    badge = '<span class="place-badge">★ Must visit</span>' if must else ""
    tip = f'\n      <p class="place-tip"><b>Tip</b> {e(it["tip"])}</p>' if it.get("tip") else ""
    return f"""<article class="place{' must' if must else ''}" data-cat="{it['cat']}" data-times="{times}" data-must="{'yes' if must else 'no'}">
      {badge}<div class="place-top"><span class="place-km">{km(it['km'])}</span><span class="place-cat">{e(cats[it['cat']])}</span></div>
      <h3>{e(it['name'])}</h3>
      <p>{e(it['about'])}</p>
      <dl class="place-facts">
        <div><dt>Best time</dt><dd>{e(it['best'])}</dd></div>
        <div><dt>Time needed</dt><dd>{e(it['duration'])}</dd></div>
        <div><dt>Good for</dt><dd>{e(it['good_for'])}</dd></div>
        <div><dt>Where</dt><dd>{e(it['where'])}</dd></div>
      </dl>{tip}
      <a class="btn place-btn" href="{directions}" target="_blank" rel="noopener">Get directions</a>
    </article>"""


def explore_page(p):
    from urllib.parse import quote
    P = DATA["places"]
    cats = dict(P["categories"])
    items = sorted(P["list"], key=lambda x: (not x.get("must"), x["km"]))
    cards = "\n    ".join(place_card(it, cats) for it in items)
    cat_btns = ('<button type="button" data-place-cat="all" aria-pressed="true">All</button>'
                '<button type="button" data-place-cat="must" aria-pressed="false">★ Must visit</button>') + "".join(
        f'<button type="button" data-place-cat="{k}" aria-pressed="false">{e(v)}</button>' for k, v in P["categories"])
    time_btns = '<button type="button" data-place-time="any" aria-pressed="true">Any time</button>' + "".join(
        f'<button type="button" data-place-time="{k}" aria-pressed="false">{v}</button>'
        for k, v in [("morning", "Morning"), ("afternoon", "Afternoon"), ("evening", "Evening")])
    trek = next(it for it in items if it["name"].startswith("Swamymalai"))
    trek_dir = ("https://www.google.com/maps/dir/?api=1&origin=" + quote(ORIGIN) + "&destination=" + quote(trek["maps"]))
    return f"""<section class="wrap page-head">
  <span class="label">Explore Yelagiri</span>
  <h1>Things to do in Yelagiri</h1>
  <p>Most of Yelagiri's lakes, parks, temples and viewpoints are within 4 km of Sapphire Stayss in Mangalam. Pick what you are in the mood for, or the time of day, and we will show you what fits. Distances are by road from our gate.</p>
</section>
<section class="wrap section">
  <div class="highlight-box">
    <div>
      <span class="label">Right behind us</span>
      <h2>The Swamymalai trek</h2>
      <p>{e(trek['about'])}</p>
      <p style="margin-top:12px">{e(trek['tip'])}</p>
      <div class="btn-row" style="margin-top:22px"><a class="btn" href="{trek_dir}" target="_blank" rel="noopener">Get directions</a></div>
    </div>
    {img(p, "home/swamymalai-view", "View over forested hills and the plains from the top of Swamymalai", "(max-width: 920px) 100vw, 45vw")}
  </div>
</section>
<section class="wrap section tight-top" aria-labelledby="places-title">
  <div class="split-head"><h2 class="big" id="places-title">Plan your outing</h2><p class="place-count" id="place-count" aria-live="polite">{len(items)} places</p></div>
  <div class="place-filters">
    <div class="filters" role="group" aria-label="What are you in the mood for?">{cat_btns}</div>
    <div class="filters" role="group" aria-label="Time of day">{time_btns}</div>
  </div>
  <div class="place-grid" id="place-grid">
    {cards}
  </div>
  <p class="place-empty" id="place-empty" hidden>Nothing matches both choices. Try another time of day.</p>
  <p class="small-print" style="margin-top:28px">Opening hours and ticket prices change during the year, so please check before you go. We are always happy to help you plan.</p>
</section>
<section class="wrap section tight-top">
  <div class="split-head">
    <div><h2 class="big">Getting here</h2><p class="lead">We are in Mangalam, Yelagiri. Read the driving guides <a href="{p}yelagiri-from-bangalore.html">from Bangalore</a> and <a href="{p}yelagiri-from-chennai.html">from Chennai</a>, or open the map for directions.</p></div>
    <a class="btn" href="{e(B['maps_url'])}" target="_blank" rel="noopener">Open in Google Maps</a>
  </div>
</section>"""


def explore_jsonld():
    items = sorted(DATA["places"]["list"], key=lambda x: (not x.get("must"), x["km"]))
    return [{"@type": "ItemList", "name": "Things to do in Yelagiri near Sapphire Stayss", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "item": {
            "@type": "TouristAttraction", "name": it["name"],
            "description": f"{it['about']} {km(it['km'])} by road from Sapphire Stayss. Best time: {it['best']}. Time needed: {it['duration']}."}}
        for i, it in enumerate(items)]}]


# ---------------------------------------------------------------- About

ABOUT_SHORT = ("Sapphire Stayss is a small, quiet stay at the foot of Swamymalai. With only a handful of rooms "
               "and a villa around the garden, we can look after every guest ourselves, from your first WhatsApp "
               "message to the campfire on your last night.")


def about_page(p):
    rv = DATA["reviews"][0]
    A = B["about"]
    run_by = e(A["run_by"]) if A["run_by"] else todo("who runs Sapphire Stayss (the hosts' names)")
    since = e(A["since"]) if A["since"] else todo("the year you started hosting guests")
    story = f"<p>{e(A['story'])}</p>" if A["story"] else f"<p>{todo('two or three lines in your own words: why you started Sapphire Stayss and what makes it different')}</p>"
    return f"""<section class="wrap page-head">
  <span class="label">About us</span>
  <h1>About Sapphire Stayss</h1>
  <p>{e(ABOUT_SHORT)}</p>
</section>
<section class="wrap section">
  <dl class="policy-grid">
    <div><dt>Hosts</dt><dd>{run_by}</dd></div>
    <div><dt>Hosting since</dt><dd>{since}</dd></div>
    <div><dt>Rooms</dt><dd>{sum(r['units'] for r in ROOMS)} rooms, including a private villa</dd></div>
    <div><dt>Where</dt><dd>Mangalam, Yelagiri, at the foot of Swamymalai</dd></div>
  </dl>
</section>
<section class="wrap section tight-top">
  <div class="prose">
    <h2>Our story</h2>
    {story}
  </div>
</section>
<section class="wrap section">
  <div class="about-band">
    {img(p, "home/evening-exterior", "Sapphire Stayss lit up in the evening", "(max-width: 920px) 100vw, 45vw", lazy=False)}
    <div class="prose">
      <h2>Our place</h2>
      <p>Sapphire Stayss sits in Mangalam, on the quieter side of Yelagiri, a few kilometres from the busy lake area. Mornings start with birdsong, and the Swamymalai trail begins almost at our gate.</p>
      <p>We keep it small on purpose: a garden with swings and shady benches, clean and comfortable rooms, a good South Indian breakfast, and people who are there when you need something.</p>
    </div>
  </div>
</section>
<section class="wrap section tight-top">
  <h2 class="big" style="margin-bottom:24px">What we care about</h2>
  <div class="values">
    <div><h3>Clean, comfortable rooms</h3><p>Fresh linen, spotless bathrooms and hot water, every stay. It is the thing our guests mention most.</p></div>
    <div><h3>Help when you need it</h3><p>Dinner ordered in, a campfire in the garden, a cake for a birthday, directions to the trek. Just ask us.</p></div>
    <div><h3>A quiet place to rest</h3><p>No crowds and no loud music. Just the hills, the garden and time to slow down.</p></div>
  </div>
</section>
<section class="wrap section tight-top reviews">
  <span class="label">In our guests' words</span>
  <p class="quote">“{e(rv['quote'])}”</p>
  <p class="quote-by">{review_by(rv)}</p>
  <div class="btn-row" style="justify-content:center;margin-top:30px"><a class="btn" href="{book_href(p)}">Plan your stay</a><a class="btn btn-line" href="{p}rooms.html">See the rooms</a></div>
</section>"""


# ---------------------------------------------------------------- Policies & FAQ

def faq_items(p):
    """(question, answer HTML). Answers holding a TODO are shown on the page but left out of the FAQPage schema."""
    bl, ch, st = TRAVEL["bangalore"], TRAVEL["chennai"], TRAVEL["station"]
    pool = (f"Yes. {e(B['pool'])}" if B["pool"] else
            todo("say whether there is a swimming pool and, if so, its timings and rules. Until then the pool is left out of the site and the schema"))
    pets = e(B["pets"]) if B["pets"] else todo("say whether pets are allowed, and on what conditions")
    pickup = (f" {e(B['station_pickup'])}" if B["station_pickup"] else
              " " + todo("say whether you can arrange a taxi or pickup from Jolarpettai station, and the cost"))
    return [
        ("What are the check-in and check-out times?",
         f"Check-in and check-out are both at {B['check_in']}. If you need an early check-in or late check-out, message us and we will try to arrange it."),
        ("How far is Sapphire Stayss from Bangalore?",
         f"Yelagiri is {e(bl['km'])} from Bengaluru, usually {e(bl['time'])} by car, via Hosur, Krishnagiri and Vaniyambadi, then up the ghat road from Ponneri.{travel_check()} "
         f'See <a href="{p}yelagiri-from-bangalore.html">how to reach Yelagiri from Bangalore</a>.'),
        ("How far is Sapphire Stayss from Chennai?",
         f"Yelagiri is {e(ch['km'])} from Chennai, usually {e(ch['time'])} by car, on the Chennai–Bengaluru highway via Vellore, Ambur and Vaniyambadi, then up the ghat road from Ponneri.{travel_check()} "
         f'See <a href="{p}yelagiri-from-chennai.html">how to reach Yelagiri from Chennai</a>.'),
        ("What is the nearest railway station?",
         f"{e(st['name'])}, {e(st['km'])} from Yelagiri by road. From the station you can take a taxi up the ghat road.{pickup}"),
        ("Is breakfast included?",
         f"Yes. A South Indian breakfast is complimentary for every guest, including anyone on an extra mattress. It is served {B['breakfast_time']} in our glass-walled dining room."),
        ("Do you serve lunch or dinner?",
         "We do not run a restaurant, but we can order lunch or dinner for you from a good local restaurant and serve it at the property. Let us know in advance."),
        ("Is there a swimming pool?", pool),
        ("Are pets allowed?", pets),
        ("Can I bring children or add an extra bed?",
         f"Yes. Children {B['child_age']} years count as children; guests aged 6 and over count as adults. Each double bed sleeps two adults and one child, and the single bed sleeps one. "
         f'We can add an extra mattress, and breakfast is included for the extra guest; ask us for the price. Every <a href="{p}rooms.html">room page</a> shows the maximum number of guests.'),
        ("Is there parking and Wi-Fi?",
         "Yes, both are free. Parking is inside the property."),
        ("What is the cancellation policy?",
         f'Cancel up to {B["free_cancellation_days"]} days before your check-in date and we refund your advance in full. If you cancel later than that, or do not arrive, the advance is not refunded. '
         f'Bookings on Booking.com, Agoda or other sites follow that site\'s terms. Read the <a href="{p}refund-policy.html">cancellation &amp; refund policy</a>.'),
        ("How do I book?",
         f'WhatsApp or call us on <a href="tel:+{B["phone_whatsapp_raw"]}">{e(B["phone_whatsapp"])}</a> or <a href="tel:+{B["phone_other_raw"]}">{e(B["phone_other"])}</a>, '
         f'email <a href="mailto:{e(B["email"])}">{e(B["email"])}</a>, or send your dates through our <a href="{book_href(p)}">booking form</a>. '
         f"A {B['advance_percent']}% advance confirms your room and you pay the balance at check-in."),
        ("What ID do I need?",
         "All adult guests need a valid government photo ID, such as an Aadhaar card, passport, driving licence or voter ID, at check-in."),
        ("Can you arrange a campfire, cake or decoration?",
         "Yes. Campfires, birthday or anniversary cakes and room decoration can be arranged if you ask at least a day ahead. There is an extra charge; message us for prices."),
        ("When is the best time to visit Yelagiri?",
         "Most visitors find November to February the most pleasant, with cool weather. March to May is the warmest time of year, and the "
         "Tamil Nadu tourism department's summer festival is usually held in May. July to September brings the monsoon rains. "
         "Jalagamparai Waterfalls, a half-day trip, is fullest from October to February."),
    ]


def faq_jsonld():
    import re
    return [{"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q,
         "acceptedAnswer": {"@type": "Answer", "text": html.unescape(re.sub(r"<[^>]+>", "", a))}}
        for q, a in faq_items("") if 'class="todo"' not in a]}]


def faq_page(p):
    faq = "\n  ".join(f"<details><summary>{e(q)}</summary><p>{a}</p></details>" for q, a in faq_items(p))
    return f"""<section class="wrap page-head">
  <span class="label">Good to know</span>
  <h1>Policies &amp; FAQ</h1>
  <p>Everything you need to know before you arrive. Anything else, just message us on WhatsApp.</p>
</section>
<section class="wrap section">
  <dl class="policy-grid">
    <div><dt>Check-in</dt><dd>{B['check_in']}</dd></div>
    <div><dt>Check-out</dt><dd>{B['check_out']}</dd></div>
    <div><dt>Advance</dt><dd>{B['advance_percent']}% to confirm</dd></div>
    <div><dt>Cancellation</dt><dd>Free up to {B['free_cancellation_days']} days before</dd></div>
    <div><dt>Breakfast</dt><dd>Included, {B['breakfast_time']}</dd></div>
    <div><dt>Children</dt><dd>{B['child_age'].capitalize()} years</dd></div>
    <div><dt>ID</dt><dd>Photo ID for all adults</dd></div>
    <div><dt>Parking &amp; Wi-Fi</dt><dd>Free</dd></div>
  </dl>
</section>
<section class="wrap section tight-top">
  <h2 class="big" style="margin-bottom:20px">Questions</h2>
  <div class="faq">
  {faq}
  </div>
  <p class="small-print" style="margin-top:24px">Read the full <a href="{p}terms.html">terms</a> and <a href="{p}refund-policy.html">cancellation &amp; refund policy</a>.</p>
</section>"""


def moved_page(target):
    """Old address kept for the preview host, which can't do redirects. On GoDaddy, .htaccess redirects it first."""
    def content(p):
        return f"""<section class="wrap page-head" style="border-bottom:0">
  <span class="label">This page has moved</span>
  <h1>Policies &amp; FAQ</h1>
  <p>This page is now at <a href="{p}{target}">{target}</a>.</p>
</section>"""
    return content


# ---------------------------------------------------------------- How to reach

def route_page(city):
    t = TRAVEL[city]
    name = {"bangalore": "Bangalore", "chennai": "Chennai"}[city]
    if city == "bangalore":
        intro = (f"Yelagiri is {e(t['km'])} from Bengaluru, an easy weekend drive of {e(t['time'])}. "
                 "Most of it is on the national highway; only the last stretch climbs the hills.")
        steps = [
            ("Bengaluru to Krishnagiri", "Leave the city on the Hosur Road (NH 44) to Hosur, just inside Tamil Nadu and about 40 km out, and carry on to Krishnagiri, about 90 km from Bengaluru and a good place for a break."),
            ("Krishnagiri to Vaniyambadi", "At Krishnagiri, take NH 48 towards Chennai and drive on towards Vaniyambadi."),
            ("Up to Yelagiri", "Leave the highway near Vaniyambadi and follow the signs for Yelagiri through Ponneri, where the ghat road starts. Google Maps will show you the exact turn."),
        ]
        other = ("chennai", "Chennai")
    else:
        intro = (f"Yelagiri is {e(t['km'])} from Chennai, a drive of {e(t['time'])}. "
                 "Almost all of it is on the Chennai–Bengaluru highway; only the last stretch climbs the hills.")
        steps = [
            ("Chennai to Vellore", "Leave Chennai on NH 48 (the Bengaluru highway) through Poonamallee, Sriperumbudur and Walajapet to Vellore. Vellore, with its fort, is a good place for a break."),
            ("Vellore to Vaniyambadi", "Stay on NH 48 through Ambur, known for its biryani, to Vaniyambadi."),
            ("Up to Yelagiri", "Leave the highway at Vaniyambadi and follow the signs for Yelagiri through Ponneri, where the ghat road starts. Google Maps will show you the exact turn."),
        ]
        other = ("bangalore", "Bangalore")
    g, st = TRAVEL["ghat"], TRAVEL["station"]
    route = " → ".join(e(x) for x in t["route"])
    step_html = "\n    ".join(f"<h3>{e(h)}</h3>\n    <p>{e(x)}</p>" for h, x in steps)
    turn = "" if TRAVEL["verified"] else f"<p>{todo('confirm the highway turn-off and route you tell guests, and any landmark near the resort gate')}</p>"

    def content(p):
        return f"""<section class="wrap page-head">
  <p class="crumbs"><a href="{p}index.html">Home</a> / How to reach Yelagiri from {name}</p>
  <span class="label">Getting here</span>
  <h1>How to reach Yelagiri from {name}</h1>
  <p>{intro}</p>
</section>
<section class="wrap section">
  <dl class="policy-grid">
    <div><dt>Distance</dt><dd>{e(t['km'])}</dd></div>
    <div><dt>Drive time</dt><dd>{e(t['time'])}</dd></div>
    <div><dt>Ghat road</dt><dd>{g['hairpins']} hairpin bends from Ponneri</dd></div>
    <div><dt>By train</dt><dd>{e(st['name'])}, {e(st['km'])}</dd></div>
  </dl>
  <p class="small-print" style="margin-top:14px">Distances and times are approximate and depend on traffic.{travel_check()}</p>
</section>
<section class="wrap section tight-top">
  <div class="prose">
    <h2>The route</h2>
    <p>{route}</p>
    {step_html}
    {turn}
    <h2>The ghat road</h2>
    <p>The road up from {e(g['starts'])} climbs through {g['hairpins']} hairpin bends. It is a two-way road, so expect buses and cars coming down as you go up.</p>
    <ul>
      <li>Climb in a low gear and use the engine to brake on the way down.</li>
      <li>Sound your horn before blind bends, and don't overtake on them.</li>
      <li>If you haven't driven it before, try to arrive in daylight.</li>
      <li>Fill up on fuel and cash in the plains before you start the climb.</li>
    </ul>
    <h2>When you reach Yelagiri</h2>
    <p>At the top, the air is noticeably cooler than in the plains. Sapphire Stayss is in Mangalam, on the quieter side of Yelagiri at the foot of Swamymalai; open <a href="{e(B['maps_url'])}" target="_blank" rel="noopener">our Google Maps pin</a> for the last few kilometres. Check-in is at {B['check_in']}, so leaving {name} early in the morning gets you here in time to check in and enjoy a full afternoon.</p>
    <p>Weekends and holidays are busier on the highway and at Yelagiri's lake and parks, so allow extra time.</p>
    <h2>By train</h2>
    <p>The nearest railway station is {e(st['name'])}, {e(st['km'])} from Yelagiri. Taxis from the station take the same ghat road up from Ponneri.</p>
  </div>
</section>
<section class="wrap section tight-top">
  <div class="highlight-box">
    <div>
      <h2>Plan your stay</h2>
      <p>Pick a room, then message us your dates on WhatsApp. Breakfast is included with every stay.</p>
      <div class="btn-row" style="margin-top:22px"><a class="btn" href="{book_href(p)}">Check availability</a><a class="btn btn-line" href="{p}rooms.html">See the rooms</a></div>
    </div>
    <div class="prose">
      <h3>Once you're here</h3>
      <p>See <a href="{p}explore.html">things to do in Yelagiri</a>, most within 4 km of the resort. Coming from {other[1]} instead? Read <a href="{p}yelagiri-from-{other[0]}.html">how to reach Yelagiri from {other[1]}</a>.</p>
    </div>
  </div>
</section>"""
    return content


# ---------------------------------------------------------------- Contact

def contact_page(p):
    from urllib.parse import quote
    map_embed = B["maps_embed_url"] or ("https://www.google.com/maps?output=embed&q=" + quote(f"{B['name']}, {B['address_line']}, {B['region']} {B['postcode']}"))
    map_todo = "" if B["maps_embed_url"] else " " + todo("paste the embed link from Google Maps (your listing → Share → Embed a map, the src=\"…\" part) into maps_embed_url so the map shows your exact pin")
    room_options = "".join(f'<option value="{r["slug"]}">{e(r["name"])}</option>' for r in ROOMS)
    return f"""<section class="wrap page-head">
  <span class="label">Contact</span>
  <h1>Contact &amp; directions</h1>
  <p>The quickest way to reach us is WhatsApp. We are happy to help with availability, directions and special requests.</p>
</section>
<section class="wrap section">
  <div class="contact-grid">
    <div>
      <ul class="contact-list">
        <li><span>WhatsApp &amp; phone</span><a href="{wa()}" target="_blank" rel="noopener">{e(B['phone_whatsapp'])}</a></li>
        <li><span>Phone</span><a href="tel:+{B['phone_other_raw']}">{e(B['phone_other'])}</a></li>
        <li><span>Email</span><a href="mailto:{e(B['email'])}">{e(B['email'])}</a></li>
        <li><span>Instagram</span><a href="{e(B['instagram'])}" target="_blank" rel="noopener">{e(B['instagram_handle'])}</a></li>
        <li><span>Address</span><address style="font-style:normal;font-size:19px">{nap()}</address></li>
      </ul>
      <p style="margin-top:22px"><a class="btn btn-line" href="{e(B['maps_url'])}" target="_blank" rel="noopener">Get directions</a></p>
    </div>
    <div>
      <h2 class="big" id="enquiry" style="margin-bottom:8px">Book or enquire</h2>
      <p class="lead" style="margin-bottom:22px">Tell us your dates and we will confirm availability. Tapping send opens WhatsApp with your details ready to go.</p>
      <form class="form" id="enquiry-form">
        <div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" required autocomplete="name"></div>
        <div class="field"><label for="f-phone">Phone</label><input id="f-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel"></div>
        <div class="field"><label for="f-in">Check-in</label><input id="f-in" name="checkin" type="date" required></div>
        <div class="field"><label for="f-out">Check-out</label><input id="f-out" name="checkout" type="date" required></div>
        <div class="field">
          <label for="f-guests">Guests</label>
          <div class="stepper">
            <button type="button" data-step="-1" aria-label="One guest fewer">−</button>
            <input id="f-guests" name="guests" type="number" min="1" max="20" value="2" inputmode="numeric">
            <button type="button" data-step="1" aria-label="One guest more">+</button>
          </div>
        </div>
        <div class="field"><label for="f-room">Room</label><select id="f-room" name="room"><option value="">Any room</option>{room_options}</select></div>
        <div class="field full"><label for="f-msg">Message (optional)</label><textarea id="f-msg" name="message" placeholder="Anything we should know, such as a campfire or a birthday"></textarea></div>
        <div class="actions"><button class="btn" type="submit">Send on WhatsApp</button></div>
      </form>
    </div>
  </div>
</section>
<section class="wrap section tight-top" aria-labelledby="map-title">
  <div class="split-head"><h2 class="big" id="map-title">Find us in Mangalam, Yelagiri</h2><a class="btn" href="{e(B['maps_url'])}" target="_blank" rel="noopener">Get directions</a></div>
  <div class="map"><iframe src="{e(map_embed)}" title="Map showing Sapphire Stayss in Mangalam, Yelagiri" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>
  <p class="small-print" style="margin-top:14px">Coming by road? Read the routes <a href="{p}yelagiri-from-bangalore.html">from Bangalore</a> and <a href="{p}yelagiri-from-chennai.html">from Chennai</a>.{map_todo}</p>
</section>"""


# ---------------------------------------------------------------- Legal pages

def legal(title, label, body):
    def content(p):
        return f"""<section class="wrap page-head">
  <span class="label">{label}</span>
  <h1>{title}</h1>
</section>
<section class="wrap section">
  <div class="prose">
    <p class="updated">Last updated {date.today().strftime('%d %B %Y')}</p>
{body(p)}
  </div>
</section>"""
    return content


def terms_body(p):
    return f"""    <p>These terms apply to bookings made directly with {e(B['name'])}, {e(B['address_line'])}, {e(B['region'])} {e(B['postcode'])}, through this website, by phone or on WhatsApp. Bookings made through Booking.com, Agoda or other travel sites are also subject to that site's terms.</p>
    <h2>Bookings and payment</h2>
    <p>Prices on this website are per room per night in Indian Rupees and include breakfast. Taxes are shown when you book. A booking is confirmed once we receive an advance of {B['advance_percent']}% of the total. The balance is paid at check-in.</p>
    <p>Online payments are processed securely by our payment partner. We do not see or store your card details.</p>
    <h2>Cancellations and refunds</h2>
    <p>See our <a href="{p}refund-policy.html">cancellation &amp; refund policy</a>.</p>
    <h2>Check-in and check-out</h2>
    <p>Check-in and check-out are at {B['check_in']}. All adult guests must show a valid government photo ID at check-in. We may refuse check-in if valid ID is not provided.</p>
    <h2>Occupancy</h2>
    <p>Children are guests {B['child_age']} years old; guests aged 6 and over count as adults. Each room has a maximum number of guests, shown on its page. Extra guests need an extra mattress, subject to space in the room.</p>
    <h2>House rules</h2>
    <ul>
      <li>Please respect other guests and keep noise low at night.</li>
      <li>Guests are responsible for any damage to the room or property during their stay.</li>
    </ul>
    <h2>Services from others</h2>
    <p>Meals we order for you come from local restaurants. Attractions and activities mentioned on this website are run by others, and we are not responsible for them.</p>
    <h2>Contact</h2>
    <p>Questions about these terms: {e(B['phone_whatsapp'])} or <a href="mailto:{e(B['email'])}">{e(B['email'])}</a>.</p>"""


def privacy_body(p):
    return f"""    <p>This policy explains what personal information {e(B['name'])} collects and how we use it.</p>
    <h2>What we collect</h2>
    <ul>
      <li>Details you give us when you book or enquire: your name, phone number, email address, dates and number of guests.</li>
      <li>ID details at check-in, as required by law.</li>
      <li>Payment confirmations from our payment partner. Card and bank details are handled by the payment partner, not by us.</li>
    </ul>
    <h2>How we use it</h2>
    <p>We use your information only to manage your booking, contact you about your stay, meet legal requirements and improve our service. We do not sell your information.</p>
    <h2>Who we share it with</h2>
    <p>We share information only with the services needed to run your booking: our booking system, our payment partner, and authorities when the law requires it.</p>
    <h2>This website</h2>
    <p>This website does not use advertising cookies. Fonts are loaded from Google Fonts, and the map on the contact page is shown by Google Maps. When you tap a WhatsApp button, your message is sent through WhatsApp, which has its own privacy policy.</p>
    <h2>Your choices</h2>
    <p>You can ask us to see, correct or delete the information we hold about you, unless we must keep it by law. Contact us at <a href="mailto:{e(B['email'])}">{e(B['email'])}</a> or {e(B['phone_whatsapp'])}.</p>"""


def refund_body(p):
    d = B["free_cancellation_days"]
    return f"""    <p>This policy applies to bookings made directly with {e(B['name'])}. Bookings made on Booking.com, Agoda or other travel sites follow the cancellation terms shown on that site.</p>
    <h2>Free cancellation</h2>
    <p>Cancel at least <strong>{d} days before your check-in date</strong> and we refund your advance in full.</p>
    <h2>Late cancellation and no-show</h2>
    <p>If you cancel less than {d} days before your check-in date, or do not arrive, the advance is not refunded.</p>
    <h2>Changing your dates</h2>
    <p>Message us as early as possible. We will move your booking to new dates if a room is available.</p>
    <h2>How refunds are paid</h2>
    <p>Refunds go back to the original payment method, usually within 5 to 7 working days of the cancellation being confirmed. The exact time depends on your bank.</p>
    <h2>If we have to cancel</h2>
    <p>If we cannot host you for reasons on our side, we refund everything you have paid.</p>
    <h2>How to cancel</h2>
    <p>Send us your booking details on WhatsApp at {e(B['phone_whatsapp'])} or email <a href="mailto:{e(B['email'])}">{e(B['email'])}</a>. We will confirm the cancellation in writing.</p>"""


def not_found(p):
    return f"""<section class="wrap page-head" style="border-bottom:0">
  <span class="label">Page not found</span>
  <h1>This page has moved</h1>
  <p>We have a new website, so some old links no longer work.</p>
  <div class="btn-row" style="margin-top:26px"><a class="btn" href="{p}index.html">Go to the home page</a><a class="link" href="{p}rooms.html">See the rooms</a></div>
</section>"""


# ---------------------------------------------------------------- Build

ROBOTS_ALLOWED = ["Googlebot", "Bingbot", "Google-Extended", "OAI-SearchBot", "ChatGPT-User", "GPTBot",
                  "PerplexityBot", "Perplexity-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "Applebot"]


def robots_txt():
    named = "\n".join(f"User-agent: {b}" for b in ROBOTS_ALLOWED)
    return (f"# Search engines and AI assistants are welcome to read this site.\n{named}\nAllow: /\n\n"
            f"User-agent: *\nAllow: /\n\nSitemap: {B['site_url']}/sitemap.xml\n")


def llms_txt():
    """Plain-text summary for AI assistants (llmstxt.org). Only confirmed facts; unknowns are left out."""
    total = sum(r["units"] for r in ROOMS)
    bl, ch, st = TRAVEL["bangalore"], TRAVEL["chennai"], TRAVEL["station"]
    rooms = "\n".join(
        f"- {r['name']}: {r['beds']}; up to {r['adults']} adults and {r['children']} "
        f"{'child' if r['children'] == 1 else 'children'}; {r['size_m2']} m² ({r['size_sqft']} sq ft); {r['views']}; "
        f"{r['units']} {'room' if r['units'] == 1 else 'rooms'}; from {rupees(r['price'])} per night with breakfast. {url('rooms/' + r['slug'] + '.html')}"
        for r in ROOMS)
    places = "\n".join(f"- {it['name']}: {km(it['km'])} from the resort. {it['about']}"
                        for it in sorted(DATA["places"]["list"], key=lambda x: x["km"]))
    extra = []
    if B["pool"]:
        extra.append(f"- Swimming pool: {B['pool']}")
    if B["pets"]:
        extra.append(f"- Pets: {B['pets']}")
    extra = ("\n" + "\n".join(extra)) if extra else ""
    return f"""# {B['name']}

> {B['name']} is a small garden resort with {total} rooms in Mangalam, Yelagiri Hills, Tamil Nadu, India, at the foot of Swamymalai, Yelagiri's highest hill. Rooms from {rupees(min(r['price'] for r in ROOMS))} to {rupees(max(r['price'] for r in ROOMS))} per night, complimentary South Indian breakfast for every guest. Most guests drive up from Bangalore ({bl['km']}) and Chennai ({ch['km']}).

## Location
- Address: {B['name']}, {B['address_line']}, {B['region']} {B['postcode']}, India
- Map: {B['maps_url']}
- From Bangalore: {bl['km']}, {bl['time']} by car via Hosur, Krishnagiri and Vaniyambadi. {url('yelagiri-from-bangalore.html')}
- From Chennai: {ch['km']}, {ch['time']} by car via Vellore, Ambur and Vaniyambadi. {url('yelagiri-from-chennai.html')}
- The last stretch is the Yelagiri ghat road from Ponneri, with {TRAVEL['ghat']['hairpins']} hairpin bends.
- Nearest railway station: {st['name']}, {st['km']}.

## Rooms
{rooms}

## Amenities
{chr(10).join('- ' + a for a in amenities())}

## Policies
- Check-in {B['check_in']}, check-out {B['check_out']}.
- Breakfast included, served {B['breakfast_time']}. No restaurant; lunch and dinner can be ordered in from local restaurants on request.
- Direct bookings: {B['advance_percent']}% advance, balance at check-in. Free cancellation up to {B['free_cancellation_days']} days before arrival.
- Children: {B['child_age']} years. Extra mattress available on request.
- Valid government photo ID needed for all adults.
- Campfire, cakes and room decoration on request (extra charge).{extra}

## Contact and booking
- Phone and WhatsApp: {B['phone_whatsapp']}
- Phone: {B['phone_other']}
- Email: {B['email']}
- WhatsApp link: {wa()}
- Instagram: {B['instagram']}

## Things to do nearby
{places}

## Key pages
- [Home]({url('index.html')})
- [Rooms and prices]({url('rooms.html')})
- [Policies and FAQ]({url('faq.html')})
- [Things to do in Yelagiri]({url('explore.html')})
- [How to reach Yelagiri from Bangalore]({url('yelagiri-from-bangalore.html')})
- [How to reach Yelagiri from Chennai]({url('yelagiri-from-chennai.html')})
- [Gallery]({url('gallery.html')})
- [About]({url('about.html')})
- [Contact]({url('contact.html')})
"""


def main():
    built = []
    rooms_title = f"{sum(r['units'] for r in ROOMS)} rooms"
    built.append(page("index.html", "Sapphire Stayss | Garden Resort in Yelagiri Hills with Breakfast",
                      f"Sapphire Stayss is a quiet garden resort with {rooms_title} in Mangalam, Yelagiri, Tamil Nadu. Air-conditioned rooms and a private villa from ₹2,350 a night, complimentary breakfast, free Wi-Fi and parking.",
                      home, "home"))
    built.append(page("about.html", "About Sapphire Stayss | Small Resort in Yelagiri",
                      "About Sapphire Stayss, a small, quiet resort at the foot of Swamymalai in Mangalam, Yelagiri, looked after personally by its hosts.",
                      about_page, "about", crumbs=[("About", "about.html")], image="home/evening-exterior"))
    built.append(page("rooms.html", "Rooms & Prices in Yelagiri | Sapphire Stayss",
                      "Compare the six room types at Sapphire Stayss, Yelagiri: beds, guests, size, views and prices from ₹2,350 to ₹5,050 a night with breakfast.",
                      rooms_page, "rooms", jsonld=[room_jsonld(r) for r in ROOMS], crumbs=[("Rooms", "rooms.html")],
                      image=ROOMS[0]["photos"][0][0]))
    for r in ROOMS:
        built.append(page(f"rooms/{r['slug']}.html", f"{r['name']} in Yelagiri | Sapphire Stayss",
                          f"{r['name']} at Sapphire Stayss, Yelagiri: {r['beds']}, sleeps {sleeps(r)}, {r['size_m2']} m². {rupees(r['price'])} a night with breakfast.",
                          room_page(r), "rooms", image=r["photos"][0][0], lightbox=True, jsonld=[room_jsonld(r)],
                          crumbs=[("Rooms", "rooms.html"), (r["name"], f"rooms/{r['slug']}.html")]))
    built.append(page("gallery.html", "Photo Gallery | Sapphire Stayss Resort, Yelagiri",
                      "Photos of the garden, rooms, villa, dining room and evenings at Sapphire Stayss resort in Mangalam, Yelagiri.",
                      gallery_page, "gallery", lightbox=True, crumbs=[("Gallery", "gallery.html")], image="home/evening-exterior"))
    built.append(page("explore.html", "Things to Do in Yelagiri | Sapphire Stayss",
                      "Things to do in Yelagiri, with distances from Sapphire Stayss: the Swamymalai trek 500 m away, Punganoor Lake, the Nature Park fountain show, Fundera bird park, adventure parks, temples and viewpoints.",
                      explore_page, "explore", jsonld=explore_jsonld(), crumbs=[("Things to do in Yelagiri", "explore.html")]))
    built.append(page("faq.html", "Policies & FAQ | Sapphire Stayss, Yelagiri",
                      "Sapphire Stayss, Yelagiri FAQ: 12 noon check-in and check-out, breakfast included, distance from Bangalore and Chennai, nearest station, parking, Wi-Fi, children and cancellation.",
                      faq_page, "faq", jsonld=faq_jsonld(), crumbs=[("Policies & FAQ", "faq.html")]))
    for city, name in [("bangalore", "Bangalore"), ("chennai", "Chennai")]:
        t = TRAVEL[city]
        built.append(page(f"yelagiri-from-{city}.html", f"How to Reach Yelagiri from {name} by Road | Sapphire Stayss",
                          f"Driving from {name} to Yelagiri: {t['km']}, {t['time']}. Route, stops, the {TRAVEL['ghat']['hairpins']}-bend ghat road from Ponneri and the nearest railway station.",
                          route_page(city), "", crumbs=[(f"How to reach Yelagiri from {name}", f"yelagiri-from-{city}.html")]))
    built.append(page("contact.html", "Contact & Directions | Sapphire Stayss, Yelagiri",
                      f"Call or WhatsApp Sapphire Stayss on {B['phone_whatsapp']} or {B['phone_other']}. Address, map and directions: Mangalam, Yelagiri, Tamil Nadu 635853.",
                      contact_page, "contact", crumbs=[("Contact", "contact.html")]))
    built.append(page("terms.html", "Terms & Conditions | Sapphire Stayss, Yelagiri", "Booking terms for Sapphire Stayss resort in Yelagiri, Tamil Nadu.",
                      legal("Terms &amp; conditions", "Legal", terms_body), crumbs=[("Terms", "terms.html")]))
    built.append(page("privacy.html", "Privacy Policy | Sapphire Stayss, Yelagiri", "How Sapphire Stayss, Yelagiri collects and uses your personal information.",
                      legal("Privacy policy", "Legal", privacy_body), crumbs=[("Privacy", "privacy.html")]))
    built.append(page("refund-policy.html", "Cancellation & Refund Policy | Sapphire Stayss, Yelagiri",
                      "Free cancellation up to 3 days before check-in at Sapphire Stayss, Yelagiri. How refunds work.",
                      legal("Cancellation &amp; refund policy", "Legal", refund_body), crumbs=[("Cancellation & refunds", "refund-policy.html")]))
    page("404.html", "Page not found | Sapphire Stayss, Yelagiri", "This page could not be found.", not_found)
    # Old address: .htaccess redirects it on GoDaddy; this copy covers the preview host. Not in the sitemap.
    page("policies.html", "Policies & FAQ has moved | Sapphire Stayss", "This page is now at faq.html.", moved_page("faq.html"),
         head_extra=f'\n<meta http-equiv="refresh" content="0; url=faq.html">\n<meta name="robots" content="noindex">')
    with open(os.path.join(OUT, "policies.html"), encoding="utf-8") as f:  # point the canonical at the new page
        moved = f.read().replace(f'<link rel="canonical" href="{url("policies.html")}">', f'<link rel="canonical" href="{url("faq.html")}">')
    with open(os.path.join(OUT, "policies.html"), "w", encoding="utf-8") as f:
        f.write(moved)

    urls = "\n".join(
        f"  <url><loc>{url(u)}</loc><lastmod>{TODAY}</lastmod></url>" for u in built
    )
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots_txt())
    with open(os.path.join(OUT, "llms.txt"), "w", encoding="utf-8") as f:
        f.write(llms_txt())
    print(f"Built {len(built) + 2} pages, sitemap.xml, robots.txt and llms.txt into public/")

    # List every TODO still showing, so nothing goes live unnoticed.
    import re
    left = {}
    for u in built:
        with open(os.path.join(OUT, u), encoding="utf-8") as f:
            for t in re.findall(r'<mark class="todo">TODO: (.*?)</mark>', f.read()):
                pages = left.setdefault(html.unescape(t), [])
                if u not in pages:
                    pages.append(u)
    # Facts that only go into the schema and llms.txt, so they don't show on a page
    if not (B["geo"]["latitude"] and B["geo"]["longitude"]):
        left["latitude and longitude of the resort gate (geo) for the Hotel schema"] = ["content/site.json"]
    if not B["google_business_url"]:
        left["your Google Business Profile link (google_business_url) for the schema's sameAs"] = ["content/site.json"]
    if not B["same_as"]:
        left["your Booking.com, Agoda, MakeMyTrip and Tripadvisor listing links (same_as) for the schema's sameAs"] = ["content/site.json"]
    if left:
        print(f"\n{len(left)} TODO(s) still on the site (fill them in content/site.json, then rebuild):")
        for t, pages in left.items():
            print(f"  - {t}  [{', '.join(pages[:3])}{' …' if len(pages) > 3 else ''}]")


if __name__ == "__main__":
    main()
