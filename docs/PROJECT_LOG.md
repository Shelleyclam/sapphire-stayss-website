# Sapphire Stayss website: project log

A running record of what has been built and what is planned, kept for updating a resume or portfolio.
Last updated: 30 October 2026.

## The project

A full redesign of **sapphirestayss.in**, the website of Sapphire Stayss, a small resort in Mangalam,
Yelagiri (Tamil Nadu), plus a plan for direct online booking that stays in sync with Booking.com and Agoda.

- **Role:** project owner. Set the requirements, made the design and business decisions, wrote and checked
  the content, and reviewed every round. The code was written with Claude Code, an AI coding assistant.
- **Timeline:** planning and build started 17 October 2026. First full version on 17 October, then 11 rounds of revisions.
- **Code:** https://github.com/Shelleyclam/sapphire-stayss-website (branch `new-website`)
- **Live preview:** https://shelleyclam.github.io/sapphire-stayss-website/

## Tech stack

- Static website with plain HTML, CSS and JavaScript. No framework and no paid services.
- A Python build script (`build.py`) generates all pages from one content file (`content/site.json`),
  so prices, rooms, places and policies are edited in one place.
- Images converted to WebP in two sizes (800 px and 1600 px) and loaded responsively.
- GitHub for version control, and GitHub Actions to publish to GitHub Pages automatically on every change.
- Hosting at go-live: the existing GoDaddy cPanel plan (already paid until December 2027), with an `.htaccess`
  for https, caching and redirects from the old page addresses.

## What has been built (done)

### Site structure
- **20 pages:** Home, About, Rooms, 6 room pages, Gallery, Things to do in Yelagiri, Policies & FAQ,
  How to reach Yelagiri from Bangalore, How to reach Yelagiri from Chennai, Contact, Terms, Privacy,
  Cancellation & Refund Policy, and a "page not found" page.
- The old site had 6 pages, one shared title, no descriptions, file paths with spaces and WhatsApp-named images.

### Design
- Light, minimal design based on the brand logo (sapphire blue and mountain brown), with an easy-to-read serif and sans-serif pairing.
- Went through four design rounds with the owner: standard layout, bold dark theme, light minimal, then final tweaks to fonts, spacing and the hero image.
- Works on phones, tablets and computers. Mobile menu, and a floating WhatsApp button on phones.

### Home page
- Full-width hero photo (separate sharper crop for phones), tagline "Where serenity reigns" and an intro about the foothill location.
- Date and guest picker that opens the booking enquiry with the details filled in.
- Swipeable room cards with prices, a garden photo section, and an About us section.
- **"Noon to noon":** a suggested itinerary from 12 noon check-in to 12 noon check-out, clearly marked as ideas, with on-request extras (campfire, cake and decoration) labelled.
- Guest reviews from Google and Tripadvisor, and a to-scale distance guide to nearby places.

### Rooms
- 6 room types (7 rooms) with photo galleries, a full-screen photo viewer, beds, guest limits, views, amenities and prices from ₹2,350 to ₹5,050 a night.
- Each room page has its own booking box and suggestions for other rooms.

### Gallery
- 38 captioned photos in a packed grid that adapts to wide and tall photos.
- Filters by category (Garden & property, Rooms, Dining, Evenings) with photo counts, and a full-screen viewer with keyboard and swipe navigation.

### Explore Yelagiri
- 16 nearby places as cards, each with distance, category, description, best time of day, time needed, who it suits, location and a tip.
- **Get directions** button on each card opens Google Maps with the route from the resort.
- Filters by category and by time of day (morning, afternoon, evening).
- Four places marked **★ Must visit** (Swamymalai trek, Fundera Park, Nilavoor View Point, Nature Park & fountain show), shown first, with their own filter.
- Facts researched from travel sources and checked with the owner.

### Booking and contact
- Every Book and Check availability button leads to one enquiry form: calendar date pickers, a guest counter, a room choice and a message.
- The form sends a ready-written WhatsApp message to the resort, so it works with no server or database.
- Built so the channel manager's booking page can be switched on later by pasting one link into the content file.

### Policies, legal and SEO
- Policies & FAQ page (check-in and check-out times, 50% advance, 3-day free cancellation, breakfast hours, child age, ID).
- Terms, Privacy and Cancellation & Refund pages, which payment gateways such as Razorpay require before they approve an account.
- Google-friendly setup: a unique title and description for every page, structured data (schema.org `Hotel` and `HotelRoom`), a sitemap, robots.txt, canonical links and alt text on every image.
- Old page addresses redirect to their new pages, so existing Google links keep working.

### Search and AI visibility (30 October 2026)
- Audited the old live site and the new build for how well Google and AI assistants (ChatGPT, Perplexity, Gemini, Claude) can read, quote and recommend the resort, then closed the gaps.
- Structured data on every page: schema.org `Hotel` (address, map coordinates, amenities, check-in time, room count, pet policy, links to Google, Booking.com, Agoda, Tripadvisor and Instagram), `HotelRoom` with price, GST, size and capacity for each room type, `FAQPage`, `BreadcrumbList`, and a list of nearby attractions.
- New FAQ page with 16 short, factual answers, and two driving guides (from Bangalore, 167 km, and from Chennai, 255 km) with the route, stops, ghat road tips, the last turn to the resort and options without a car.
- A plain HTML room comparison table (beds, guests, size, view, price including GST), the same name, address and phone wording in every footer, a booking call-to-action on every page, and a Google Maps embed on the contact page.
- Five real Booking.com guest reviews on the home and About pages, copied word for word with name, country and month of stay, plus a "Review us on Google" link.
- `robots.txt` that names and welcomes the AI search crawlers, and an `llms.txt` summary of the resort written for AI assistants.
- A fact-safety rule: nothing is invented. Missing facts show as yellow TODO marks, stay out of the structured data, and the build lists every one left, so nothing unconfirmed goes live. Facts were checked with the owner, which caught a pool the old site implied but the resort doesn't have, and corrected the trek distance from 500 m to 100 m.

### Performance
- Photos cut from about 300 KB each (old gallery, all loaded at once) to about 57 KB on average for the phone size, with lazy loading.
- Browser-cache busting, so visitors always get the latest design after an update.

### Research and planning
- Compared channel managers for small Indian properties (AxisRooms, eZee/Yanolja, Djubo, STAAH) on OTA sync, booking-engine embedding, Razorpay/UPI support and monthly cost.
- Defined the payment model: 50% advance online, balance at check-in, free cancellation up to 3 days before arrival.
- Set up a free public preview on GitHub Pages that updates automatically.

## Planned (scheduled next)

1. **Channel manager:** book demos with AxisRooms and eZee, compare quotes, and choose one so availability syncs with Booking.com and Agoda.
2. **Online booking and payments:** connect Razorpay (UPI and cards) to the booking engine, take a 50% advance, then switch the site's Book buttons from the enquiry form to the live booking page.
3. **Razorpay account:** apply once the site is live (needs PAN, bank details and the legal pages above).
4. **Go-live on sapphirestayss.in:** fix the GoDaddy renewal payment, check where the domain's DNS points, back up the old site and upload the new one to cPanel.
5. **Photos:** replace WhatsApp-compressed photos with full-quality originals, including a daytime exterior shot and a photo of the Swamymalai trek.
6. **About page:** add the owner's own story, the hosts' names, the year hosting started and a photo (the last TODOs on the site).
7. **Weekday and weekend pricing:** set different weekend and holiday rates in the channel manager.
8. **After launch:** update the Google Business Profile and Booking.com listing (AC in every room, correct guest numbers, the same cancellation rule, 12 noon check-in, no pool, no pets) and ask 10+ guests for detailed Google reviews. Submit the sitemap to Google Search Console and Bing Webmaster Tools, and check that Cloudflare isn't blocking AI crawlers.

## Resume bullet ideas

- Led the end-to-end redesign of a resort website, from requirements and content to design reviews and launch planning, using an AI coding assistant to build a 20-page static site.
- Designed a booking-enquiry flow (date pickers, guest counter, prefilled WhatsApp message) that captures direct bookings with no server cost, ready to switch to a live booking engine.
- Researched and compared hotel channel managers and payment options, and defined a 50% advance and 3-day cancellation model to reduce no-shows.
- Built an interactive local guide with filters, must-visit highlights and one-tap Google Maps directions for 16 attractions.
- Improved search visibility and speed with per-page metadata, schema.org markup, a sitemap, redirects from old URLs, and photos made about 80% smaller.
- Set up version control and automatic publishing to GitHub Pages for free, shareable previews on any device.
- Made a small resort's website easy for AI search assistants and Google to understand and quote: schema.org Hotel, room, FAQ and breadcrumb markup, an llms.txt summary, AI-crawler-friendly robots.txt, and factual FAQ and route pages, with a build check that keeps unconfirmed facts off the live site.
