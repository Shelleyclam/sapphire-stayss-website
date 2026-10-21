# Sapphire Stayss website: project log

A running record of what has been built and what is planned, kept for updating a resume or portfolio.
Last updated: 21 October 2026.

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
- **17 pages:** Home, About, Rooms, 6 room pages, Gallery, Explore Yelagiri, Policies & FAQ, Contact,
  Terms, Privacy, Cancellation & Refund Policy, and a "page not found" page.
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
6. **About page:** add the owner's own story, the hosts' names and a photo.
7. **Weekday and weekend pricing:** set different weekend and holiday rates in the channel manager.
8. **After launch:** update the Google Business Profile and Booking.com listing (AC in every room, correct guest numbers, the same cancellation rule), and submit the sitemap to Google Search Console.

## Resume bullet ideas

- Led the end-to-end redesign of a resort website, from requirements and content to design reviews and launch planning, using an AI coding assistant to build a 17-page static site.
- Designed a booking-enquiry flow (date pickers, guest counter, prefilled WhatsApp message) that captures direct bookings with no server cost, ready to switch to a live booking engine.
- Researched and compared hotel channel managers and payment options, and defined a 50% advance and 3-day cancellation model to reduce no-shows.
- Built an interactive local guide with filters, must-visit highlights and one-tap Google Maps directions for 16 attractions.
- Improved search visibility and speed with per-page metadata, schema.org markup, a sitemap, redirects from old URLs, and photos made about 80% smaller.
- Set up version control and automatic publishing to GitHub Pages for free, shareable previews on any device.
