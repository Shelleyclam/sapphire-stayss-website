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
    a, c = room["adults"], room["children"]
    return f"{a} adults + {c} {'child' if c == 1 else 'children'}"


def short(room):
    return room.get("short_name", room["name"])


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


NAV = [
    ("index.html", "Home", "home"),
    ("rooms.html", "Rooms", "rooms"),
    ("gallery.html", "Gallery", "gallery"),
    ("explore.html", "Explore Yelagiri", "explore"),
    ("policies.html", "Policies & FAQ", "policies"),
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
        <a class="btn" href="{wa()}" data-book>Book now</a>
    </nav>
  </div>
</header>"""


def footer(p):
    return f"""<footer class="site-footer">
  <div class="wrap foot">
    <div>
      <img src="{p}img/logo.png" alt="Sapphire Stayss" width="600" height="135" loading="lazy">
      <p>{e(B['address_line'])},<br>{e(B['region'])} {e(B['postcode'])}</p>
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
        <li><a href="{p}explore.html">Explore Yelagiri</a></li>
        <li><a href="{p}policies.html">Policies &amp; FAQ</a></li>
      </ul>
    </div>
    <div>
      <h2>Follow</h2>
      <ul>
        <li><a href="{e(B['instagram'])}" target="_blank" rel="noopener">Instagram</a></li>
        <li><a href="{e(B['maps_url'])}" target="_blank" rel="noopener">Google Maps &amp; reviews</a></li>
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


def page(path, title, description, content, current="", jsonld=None, image="home/hills-view", lightbox=False):
    depth = path.count("/")
    p = "../" * depth
    canonical = B["site_url"] + "/" + ("" if path == "index.html" else path)
    ld = ""
    if jsonld:
        ld = '\n<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False) + "</script>"
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
<link rel="stylesheet" href="{p}css/style.css">{ld}
</head>
<body data-booking-url="{e(BOOKING_URL)}" data-whatsapp="{B['phone_whatsapp_raw']}">
<!-- Generated by build.py from content/site.json. Edit those, not this file. -->
{header(p, current)}
<main id="main">
{content(p)}
</main>
{footer(p)}
{LIGHTBOX if lightbox else ""}
<script src="{p}js/main.js" defer></script>
</body>
</html>
"""
    out = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)
    return path


def availability_form(room=None, boxed=False):
    opts = ["1 adult", "2 adults", "2 adults, 1 child", "3 adults", "3 adults, 1 child",
            "4 adults", "4 adults, 1 child", "4 adults, 2 children", "More than 4 adults"]
    if room:
        def fits(o):
            if o.startswith("More"):
                return False
            adults = int(o[0])
            kids = int(o.split(", ")[1][0]) if ", " in o else 0
            return adults <= room["adults"] and kids <= room["children"]
        opts = [o for o in opts if fits(o)]
    default = "2 adults"
    options = "".join(f'<option{" selected" if o == default else ""}>{o}</option>' for o in opts)
    uid = room["slug"] if room else "home"
    room_attr = f' data-room="{e(room["name"])}"' if room else ""
    note = ("Opens the booking page in a new tab." if BOOKING_URL else
            "Sends your dates to us on WhatsApp. We reply with availability, usually within the hour.")
    return f"""<form class="booking{' boxed' if boxed else ''}" data-availability{room_attr} aria-label="Check availability">
    <div class="field"><label for="in-{uid}">Check-in</label><input id="in-{uid}" name="checkin" type="date" required></div>
    <div class="field"><label for="out-{uid}">Check-out</label><input id="out-{uid}" name="checkout" type="date" required></div>
    <div class="field"><label for="g-{uid}">Guests</label><select id="g-{uid}" name="guests">{options}</select></div>
    <button class="btn" type="submit">Check availability</button>
    <p class="booking-note">{note}</p>
  </form>"""


def room_card(p, room, in_strip=True):
    photo, alt = room["photos"][0]
    sizes = "(max-width: 560px) 80vw, 360px" if in_strip else "(max-width: 560px) 100vw, (max-width: 920px) 50vw, 400px"
    summary = "" if in_strip else f'\n      <p class="summary">{e(room["summary"])}</p>'
    return f"""<a class="room-card" href="{p}rooms/{room['slug']}.html">
      <div class="img">{img(p, photo, alt, sizes)}</div>
      <span class="room-tag">{e(room['tag'])}</span>
      <div class="room-top"><h3>{e(short(room) if in_strip else room['name'])}</h3><span class="room-size">{room['size_m2']} m²</span></div>{summary}
      <div class="room-meta"><span>{e(room['beds_short'])} · {e(sleeps(room))}</span><b>{rupees(room['price'])}</b></div>
    </a>"""


def hotel_jsonld():
    prices = [r["price"] for r in ROOMS]
    return {
        "@context": "https://schema.org",
        "@type": "Hotel",
        "name": B["name"],
        "slogan": B["tagline"],
        "url": B["site_url"] + "/",
        "image": [B["site_url"] + "/img/home/hills-view.webp", B["site_url"] + "/img/home/evening-exterior.webp"],
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
        "hasMap": B["maps_url"],
        "sameAs": [B["instagram"]],
        "priceRange": f"{rupees(min(prices))} – {rupees(max(prices))} per night",
        "currenciesAccepted": "INR",
        "checkinTime": "12:00",
        "checkoutTime": "12:00",
        "numberOfRooms": sum(r["units"] for r in ROOMS),
        "amenityFeature": [
            {"@type": "LocationFeatureSpecification", "name": n, "value": True}
            for n in ["Free Wi-Fi", "Free parking", "Air-conditioning", "Complimentary breakfast", "Garden"]
        ],
    }


# ---------------------------------------------------------------- Home

def home(p):
    cards = "\n    ".join(room_card(p, r) for r in ROOMS)
    rv = DATA["reviews"]
    more = "\n      ".join(
        f'<figure><blockquote>“{e(r["quote"])}”</blockquote><figcaption>{e(r["name"])} · {e(r["source"])}</figcaption></figure>'
        for r in rv[1:4]
    )
    stops = [(0, "Sapphire Stayss", True), (0.5, "Swamymalai trek starts, right behind us", False),
             (1, "Selfie Panda &amp; Chocolate Factory", False), (1.5, "Yelagiri Birds Park", False),
             (2, "Fundura Park", False), (2.5, "Nilavoor View Point", False),
             (3.5, "Boat House &amp; Nature Park", False), (4, "Mountain View Adventure Park", False)]
    road = "\n        ".join(
        f'<div class="stop{" home" if h else ""}" style="top:{int(d * 60)}px"><b>{"0 km" if d == 0 else km(d)}</b>{label}</div>'
        for d, label, h in stops
    )
    return f"""<div class="wrap">
  <section class="hero" aria-label="Welcome">
    <div class="hero-text">
      <span class="label">Yelagiri Hills · Tamil Nadu</span>
      <h1>Where serenity reigns</h1>
      <p>Seven rooms and a private villa around a quiet garden in Mangalam, with views across the Yelagiri hills.</p>
    </div>
    <figure class="hero-photo">
      {img(p, "home/hills-view", "Green Yelagiri hills under a blue sky", "(max-width: 1280px) 100vw, 1240px", lazy=False)}
      <figcaption>The hills around Mangalam</figcaption>
    </figure>
  </section>
  {availability_form()}
</div>

<section class="wrap section intro" aria-label="About">
  <p class="intro-lead">Fourteen hairpin bends up from the plains, the air cools and the traffic fades. Evenings here end by the campfire.</p>
  <dl class="facts">
    <div><dt>7 rooms</dt><dd>Six room types, including a separate villa with its own balcony</dd></div>
    <div><dt>Breakfast</dt><dd>Complimentary South Indian breakfast for every guest</dd></div>
    <div><dt>AC</dt><dd>In every room, with TV, Wi-Fi, kettle and hot water</dd></div>
    <div><dt>12 noon</dt><dd>Check-in and check-out, so you get a full day</dd></div>
  </dl>
</section>

<section class="section tight-top" id="rooms" aria-labelledby="rooms-title">
  <div class="wrap">
    <div class="rooms-head">
      <div><span class="label">Stay</span><h2 class="big" id="rooms-title">The rooms</h2></div>
      <p>Per night, breakfast included. Extra mattress {B['extra_mattress']} a night, breakfast included.</p>
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
  <span class="label">Your stay</span>
  <h2 class="big" id="day-title">Noon to noon</h2>
  <p class="lead">Check-in and check-out are both at 12 noon, so even one night gives you a full afternoon, evening and morning in the hills.</p>
  <div style="margin-top:clamp(24px, 3vw, 36px)">
  <div class="moment">
    <time>12:00<small>Arrive</small></time>
    <div><h3>Settle in</h3><p>Your room is ready at noon: air-conditioning, fresh linen, a kettle with tea and coffee, and a terrace over the garden.</p></div>
    {img(p, "home/room-detail", "Grey velvet sofa beside a padded headboard", "(max-width: 920px) 100vw, 45vw")}
  </div>
  <div class="moment compact">
    <time>14:30<small>Afternoon</small></time>
    <div><h3>Boating or adventure parks</h3><p>Take a boat out on Punganoor Lake at the Boat House, or spend the afternoon at Thrill Valley, Lake Zone or Wild Waves. All are about 3.5 km away. With children? Fundura Park is 2 km and the Birds Park is 1.5 km.</p></div>
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
    <div><h3>Campfire and dinner</h3><p>Tell us a day ahead and we will light a campfire in the garden and order dinner in from a good local restaurant. Celebrating? We can arrange a cake and decorate your room.</p><span class="tag">On request</span></div>
    {img(p, "home/campfire", "Campfire in the garden seating area at night", "(max-width: 920px) 100vw, 45vw")}
  </div>
  <div class="moment compact">
    <time>06:30<small>Early morning</small></time>
    <div><h3>Climb Swamymalai</h3><p>The trek to Swamymalai, the highest point in Yelagiri, starts just 500 m behind the resort. Set off early for cool air and clear views, and be back in time for breakfast.</p><span class="tag">Starts behind the resort</span></div>
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

<section class="wrap section tight-top reviews" id="reviews" aria-label="Guest reviews">
  <span class="label">Guests on Google &amp; Tripadvisor</span>
  <p class="quote">“{e(rv[0]['quote'])}”</p>
  <p class="quote-by">{e(rv[0]['name'])} · {e(rv[0]['source'])}</p>
  <div class="more-quotes">
      {more}
  </div>
  <a class="link" href="{e(B['maps_url'])}" target="_blank" rel="noopener">All reviews on Google</a>
</section>

<section class="wrap section tight-top where" id="where" aria-labelledby="where-title">
  <div>
    <span class="label">Location</span>
    <h2 class="big" id="where-title">Mangalam, Yelagiri</h2>
    <address>{e(B['address_line'])}, {e(B['region'])} {e(B['postcode'])}</address>
    <div class="btn-row">
      <a class="btn btn-line" href="{e(B['maps_url'])}" target="_blank" rel="noopener">Get directions</a>
      <a class="link" href="{p}explore.html">Things to do</a>
    </div>
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
    return f"""<section class="wrap page-head">
  <span class="label">Stay</span>
  <h1>Rooms &amp; prices</h1>
  <p>Six room types, seven rooms in all. Prices are per room per night and include breakfast. An extra mattress is {B['extra_mattress']} a night, breakfast included.</p>
</section>
<section class="wrap section">
  <div class="room-grid">
    {cards}
  </div>
</section>
<section class="wrap section tight-top">
  <div class="highlight-box">
    <div>
      <h2>In every room</h2>
      <ul class="ticks">{amen}</ul>
    </div>
    <div>
      <p>Check-in and check-out are at {B['check_in']}. A {B['advance_percent']}% advance confirms your booking and the rest is paid at check-in. Free cancellation up to {B['free_cancellation_days']} days before arrival.</p>
      <p style="margin-top:18px"><a class="link" href="{p}policies.html">Policies &amp; FAQ</a></p>
    </div>
  </div>
</section>"""


def room_page(room):
    def content(p):
        btns = "\n      ".join(
            f'<button type="button" data-lightbox="room" data-full="{p}img/{ph}.webp">{img(p, ph, alt, "(max-width: 920px) 100vw, 60vw" if i == 0 else "(max-width: 920px) 50vw, 30vw", lazy=i > 0)}</button>'
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
        <div><dt>Size</dt><dd>{room['size_m2']} m² ({room['size_sqft']} sq ft)</dd></div>
        <div><dt>Beds</dt><dd>{e(room['beds'])}</dd></div>
        <div><dt>Sleeps</dt><dd>Up to {e(sleeps(room))} ({B['child_age']} years)</dd></div>
        <div><dt>View</dt><dd>{e(room['views'])}</dd></div>
        {units}
        <div><dt>Extra bed</dt><dd>Mattress {B['extra_mattress']} a night, breakfast included</dd></div>
      </dl>
      {availability_form(room, boxed=True)}
      <p class="small-print">{B['advance_percent']}% advance to confirm, balance at check-in. Free cancellation up to {B['free_cancellation_days']} days before arrival. <a href="{p}policies.html">Policies</a></p>
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

def gallery_page(p):
    cats = [("all", "All"), ("property", "Garden & property"), ("rooms", "Rooms"), ("dining", "Dining"), ("evenings", "Evenings")]
    btns = "".join(f'<button type="button" data-filter="{k}" aria-pressed="{"true" if k == "all" else "false"}">{v}</button>' for k, v in cats)
    figs = "\n    ".join(
        f'<figure data-cat="{cat}"><button type="button" data-lightbox="gallery" data-full="{p}img/{name}.webp">{img(p, name, cap, "(max-width: 600px) 100vw, (max-width: 1000px) 50vw, 400px")}</button><figcaption>{e(cap)}</figcaption></figure>'
        for cat, name, cap in DATA["gallery"]
    )
    return f"""<section class="wrap page-head">
  <span class="label">Gallery</span>
  <h1>Around the property</h1>
  <p>The garden, the rooms, breakfast and our evenings. Tap any photo to see it larger.</p>
</section>
<section class="wrap section">
  <div class="filters" role="group" aria-label="Filter photos">{btns}</div>
  <div class="masonry">
    {figs}
  </div>
</section>"""


# ---------------------------------------------------------------- Explore

def place_list(items):
    rows = []
    for it in sorted(items, key=lambda x: x["km"]):
        note = f"<p>{e(it['note'])}</p>" if it["note"] else ""
        rows.append(f'<li><span class="km">{km(it["km"])}</span><div><h3>{e(it["name"])}</h3>{note}</div></li>')
    return "\n      ".join(rows)


def explore_page(p):
    a = DATA["attractions"]
    return f"""<section class="wrap page-head">
  <span class="label">Explore Yelagiri</span>
  <h1>Things to do nearby</h1>
  <p>Most of Yelagiri's parks, lakes and viewpoints are within 4 km of Sapphire Stayss. Distances are by road from our gate.</p>
</section>
<section class="wrap section">
  <div class="highlight-box">
    <div>
      <span class="label">Right behind us</span>
      <h2>The Swamymalai trek</h2>
      <p>The trail to Swamymalai, the highest point in Yelagiri, starts about 500 m behind the resort. Go early in the morning when the air is cool, carry water and wear good shoes. Ask us for directions to the start.</p>
    </div>
    {img(p, "property/garden-path", "Stone path through the garden at Sapphire Stayss", "(max-width: 920px) 100vw, 45vw")}
  </div>
</section>
<section class="wrap section tight-top">
  <div class="explore-cols">
    <div>
      <h2 class="big">Things to do</h2>
      <ul class="places">
      {place_list(a['do'])}
      </ul>
    </div>
    <div>
      <h2 class="big">Places to visit</h2>
      <ul class="places">
      {place_list(a['visit'])}
      </ul>
    </div>
  </div>
</section>
<section class="wrap section tight-top">
  <div class="split-head">
    <div><h2 class="big">Getting here</h2><p class="lead">We are in Mangalam, Yelagiri. Open the map for directions from Chennai, Bengaluru or Jolarpettai.</p></div>
    <a class="btn" href="{e(B['maps_url'])}" target="_blank" rel="noopener">Open in Google Maps</a>
  </div>
</section>"""


# ---------------------------------------------------------------- Policies & FAQ

FAQ = [
    ("What are the check-in and check-out times?",
     f"Check-in and check-out are both at {B['check_in']}. If you need an early check-in or late check-out, message us and we will try to arrange it."),
    ("Is breakfast included?",
     f"Yes. A South Indian breakfast is complimentary for every guest, including anyone on an extra mattress. It is served {B['breakfast_time']}."),
    ("How do I pay?",
     f"For bookings made on this website, a {B['advance_percent']}% advance confirms your room. You pay the balance at check-in. Bookings made on Booking.com, Agoda or other sites follow the payment terms shown on that site."),
    ("What is the cancellation policy?",
     f"Cancel up to {B['free_cancellation_days']} days before your check-in date and we refund your advance in full. If you cancel later than that, or do not arrive, the advance is not refunded."),
    ("Can I add an extra bed?",
     f"Yes. An extra mattress costs {B['extra_mattress']} a night and includes breakfast for the extra guest."),
    ("How many people can stay in a room?",
     "Each double bed sleeps two adults and one child, and the single bed sleeps one. Every room page shows the maximum number of guests."),
    ("Who counts as a child?",
     f"Children {B['child_age']} years count as children. Guests aged 6 and over count as adults."),
    ("Do you serve lunch or dinner?",
     "We do not run a restaurant, but we can order lunch or dinner for you from a good local restaurant and serve it at the property. Let us know in advance."),
    ("Can you arrange a campfire, cake or decoration?",
     "Yes. Campfires, birthday or anniversary cakes and room decoration can be arranged if you ask at least a day ahead. Message us for prices."),
    ("Is there parking and Wi-Fi?",
     "Yes, both are free. Parking is inside the property."),
    ("What ID do I need?",
     "All adult guests need a valid government photo ID, such as an Aadhaar card, passport, driving licence or voter ID, at check-in."),
]


def policies_page(p):
    faq = "\n  ".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in FAQ)
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
    <div><dt>Extra mattress</dt><dd>{B['extra_mattress']} a night</dd></div>
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


# ---------------------------------------------------------------- Contact

def contact_page(p):
    return f"""<section class="wrap page-head">
  <span class="label">Contact</span>
  <h1>Talk to us</h1>
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
        <li><span>Address</span><address style="font-style:normal;font-size:19px">{e(B['address_line'])},<br>{e(B['region'])} {e(B['postcode'])}</address></li>
      </ul>
      <p style="margin-top:22px"><a class="btn btn-line" href="{e(B['maps_url'])}" target="_blank" rel="noopener">Get directions</a></p>
    </div>
    <div>
      <h2 class="big" style="margin-bottom:8px">Send an enquiry</h2>
      <p class="lead" style="margin-bottom:22px">Fill this in and tap send. It opens WhatsApp with your message ready to go.</p>
      <form class="form" id="enquiry-form">
        <div class="field"><label for="f-name">Your name</label><input id="f-name" name="name" required autocomplete="name"></div>
        <div class="field"><label for="f-phone">Phone (optional)</label><input id="f-phone" name="phone" type="tel" autocomplete="tel"></div>
        <div class="field"><label for="f-dates">Dates (optional)</label><input id="f-dates" name="dates" placeholder="e.g. 14–16 Nov"></div>
        <div class="field"><label for="f-guests">Guests (optional)</label><input id="f-guests" name="guests" placeholder="e.g. 2 adults, 1 child"></div>
        <div class="field full"><label for="f-msg">Message</label><textarea id="f-msg" name="message" required></textarea></div>
        <div class="actions"><button class="btn" type="submit">Send on WhatsApp</button></div>
      </form>
    </div>
  </div>
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
    <p>Children are guests {B['child_age']} years old; guests aged 6 and over count as adults. Each room has a maximum number of guests, shown on its page. Extra guests need an extra mattress at {B['extra_mattress']} per night, subject to space in the room.</p>
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
    <p>This website does not use advertising cookies. Fonts are loaded from Google Fonts. When you tap a WhatsApp button, your message is sent through WhatsApp, which has its own privacy policy.</p>
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

def main():
    built = []
    built.append(page("index.html", "Sapphire Stayss | Resort in Yelagiri Hills with Breakfast",
                      "A quiet garden resort in Mangalam, Yelagiri. Air-conditioned rooms and a private villa from ₹2,350 a night, complimentary breakfast, campfire on request.",
                      home, "home", jsonld=hotel_jsonld()))
    built.append(page("rooms.html", "Rooms & Prices | Sapphire Stayss, Yelagiri",
                      "Six room types at Sapphire Stayss, Yelagiri, from ₹2,350 to ₹5,050 a night with breakfast. Family rooms, a private villa and mountain-view doubles.",
                      rooms_page, "rooms", image=ROOMS[0]["photos"][0][0]))
    for r in ROOMS:
        built.append(page(f"rooms/{r['slug']}.html", f"{r['name']} | Sapphire Stayss, Yelagiri",
                          f"{r['name']} at Sapphire Stayss, Yelagiri: {r['size_m2']} m², {r['beds']}, sleeps {sleeps(r)}. {rupees(r['price'])} a night with breakfast.",
                          room_page(r), "rooms", image=r["photos"][0][0], lightbox=True,
                          jsonld={"@context": "https://schema.org", "@type": "HotelRoom", "name": r["name"],
                                  "description": r["summary"], "bed": r["beds"],
                                  "occupancy": {"@type": "QuantitativeValue", "maxValue": r["adults"] + r["children"]},
                                  "floorSize": {"@type": "QuantitativeValue", "value": r["size_m2"], "unitCode": "MTK"},
                                  "containedInPlace": {"@type": "Hotel", "name": B["name"], "url": B["site_url"] + "/"}}))
    built.append(page("gallery.html", "Photo Gallery | Sapphire Stayss, Yelagiri",
                      "Photos of the garden, rooms, villa, dining room and evenings at Sapphire Stayss in Yelagiri.",
                      gallery_page, "gallery", lightbox=True, image="home/evening-exterior"))
    built.append(page("explore.html", "Things to Do in Yelagiri Near Sapphire Stayss",
                      "Swamymalai trek starts 500 m behind Sapphire Stayss. Boat House, Nature Park fountain show, adventure parks, temples and viewpoints within 4 km.",
                      explore_page, "explore"))
    built.append(page("policies.html", "Policies & FAQ | Sapphire Stayss, Yelagiri",
                      "Check-in and check-out at 12 noon, 50% advance, free cancellation up to 3 days before arrival, breakfast included, extra mattress ₹200.",
                      policies_page, "policies"))
    built.append(page("contact.html", "Contact | Sapphire Stayss, Yelagiri",
                      f"Call or WhatsApp Sapphire Stayss on {B['phone_whatsapp']}. Mangalam, Yelagiri, Tamil Nadu 635853.",
                      contact_page, "contact"))
    built.append(page("terms.html", "Terms & Conditions | Sapphire Stayss", "Booking terms for Sapphire Stayss, Yelagiri.",
                      legal("Terms &amp; conditions", "Legal", terms_body)))
    built.append(page("privacy.html", "Privacy Policy | Sapphire Stayss", "How Sapphire Stayss collects and uses your personal information.",
                      legal("Privacy policy", "Legal", privacy_body)))
    built.append(page("refund-policy.html", "Cancellation & Refund Policy | Sapphire Stayss",
                      "Free cancellation up to 3 days before check-in at Sapphire Stayss. How refunds work.",
                      legal("Cancellation &amp; refund policy", "Legal", refund_body)))
    page("404.html", "Page not found | Sapphire Stayss", "This page could not be found.", not_found)

    urls = "\n".join(
        f"  <url><loc>{B['site_url']}/{'' if u == 'index.html' else u}</loc><lastmod>{TODAY}</lastmod></url>" for u in built
    )
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>\n')
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\n\nSitemap: {B['site_url']}/sitemap.xml\n")
    print(f"Built {len(built) + 1} pages into public/")


if __name__ == "__main__":
    main()
