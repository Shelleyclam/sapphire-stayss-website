# Working notes (for picking up where we left off)

Short handover for a new session or after the chat is compacted. The full history of what was built
and what is planned is in `docs/PROJECT_LOG.md`. Facts about the business live in `content/site.json`.

## Where things stand (25 November 2026)

- **Live:** https://sapphirestayss.in is on GoDaddy cPanel hosting, behind Cloudflare. Went live on 24 November 2026.
- **Preview:** https://shelleyclam.github.io/sapphire-stayss-website/ (GitHub Pages; canonical tags point to the live domain).
- **Repo:** github.com/Shelleyclam/sapphire-stayss-website. It is public. The default and working branch is `new-website`.
- **Google Analytics:** tag G-V32SGMJZLN on every page (`business.google_analytics_id`), linked for Google Ads. The privacy page mentions it.
- **Google Search Console:** verified with the HTML tag (in `business.google_site_verification`). `sitemap.xml` was submitted: Success, 18 pages. Indexing was requested for the home page and the key pages.

## How changes go live

1. Edit `content/site.json` or `build.py`, or `public/css/style.css` / `public/js/main.js`.
2. Run `python3 build.py`, then commit and push to `new-website`.
3. Two workflows run on every push:
   - **Deploy to GoDaddy** (`.github/workflows/deploy-godaddy.yml`) uploads `public/` over FTPS (strict TLS).
     It uses the secrets `FTP_SERVER` = `sg2plzcpnl508259.prod.sin2.secureserver.net`, `FTP_USERNAME` = `deploy@sapphirestayss.in` and `FTP_PASSWORD`.
     `ftp.sapphirestayss.in` does not resolve, because DNS is on Cloudflare.
     The FTP account's directory is `public_html`, which is the document root.
   - **Preview on GitHub Pages** often fails with "No artifacts named github-pages". This is a GitHub-side glitch; re-run it with `gh run rerun <id>` and it usually passes on the second try.
4. Check the live site: `curl -sS https://sapphirestayss.in/...`. Cloudflare may cache images; CSS, JS and the hero image carry `?v=<hash>`.

## Hosting details

- cPanel server name: sg2plzcpnl508259 (Singapore). Shared IP: 118.139.178.200. Hosting package: Starter.
- `.htaccess`: the https redirect uses `X-Forwarded-Proto` (`%{HTTPS}` would loop behind Cloudflare). Old URLs, such as `/html pages/...` and `/policies.html` → `/faq.html`, redirect with 301 to absolute https URLs.
- Leave cPanel's "Force HTTPS Redirect" Off.
- The old site's files are still in `public_html`. They are harmless and the redirects cover them. The owner has the backup zip.
- Never ask for passwords in chat. Secrets go in GitHub repository secrets, which the owner adds.

## Owner's decisions and preferences

- **Tone:** plain, non-technical, short replies. The owner reviews on the live or preview link and sends screenshots.
- **Design:** light, minimal, sapphire ink on off-white. Headings in Marcellus, body text in Jost. Not too much white space; logo enlarged.
- **Removed from the site, do not re-add:**
  - smoking and pet rules, and any mention of alcohol
  - room sizes, child counts on rooms, and the ₹200 extra-mattress price
  - the "Ask us to book" trek button
  - dinner in the home campfire section
  - the Hosts line on the About page
  - the bird parks (Aqua Fountain, Yelagiri Birds Park)
  - tips on temple cards
- **Campfire:** on request, extra charge. Dinner ordering is still mentioned elsewhere (FAQ, About).
- **Booking:** every Book and Check availability button goes to the enquiry form (`contact.html#enquiry`), which sends a WhatsApp message to +91 93639 41162. The date pickers default to today and tomorrow. When a channel manager is chosen, paste its booking URL into `booking.url`.
- **Payments plan:** 50% advance through Razorpay in the channel manager's booking engine; free cancellation up to 3 days before arrival.
- **Explore page:** cards with filters (category, time of day, ★ Must visit). The must-visit places are the Swamymalai trek (the trail starts 100 m from the gate), Fundera Park, Nilavoor View Point, and the Nature Park & fountain show.
- **Photos:** WhatsApp shrinks them, so ask for originals sent as a document or through Drive.
  - The hero is the Swamymalai view (`home/hero-swamymalai*`).
  - Family Room cover: `family-room-garden-view-8`.
  - Deluxe Family Suite photos: 8 (sitting room, cover), 10, 6 and 9 only.

## Rooms (prices per night, breakfast included, GST included, same rate every day)

| Room | Price | Max adults | Units |
|---|---|---|---|
| Deluxe Villa | ₹5,050 | 4 | 1 |
| Deluxe Family Suite | ₹5,050 | 4 | 1 |
| Family Room with Garden View | ₹3,950 | 4 | 1 |
| Double or Twin Room with Mountain View | ₹2,850 | 3 | 1 |
| Double Room with Mountain View | ₹2,750 | 2 | 2 |
| King Room with Mountain View | ₹2,550 | 2 | 1 |

Check-in and check-out are both at 12 noon. Breakfast is 8:30 to 10 AM. Children are guests under 6. There is no pool. Hosting since 2022.

## Still to do (owner)

1. Fix the payment issue on the GoDaddy renewal (the domain renews 2 April 2027).
2. Channel manager demos (AxisRooms and eZee), then Razorpay with a 50% advance, then switch the Book buttons to the booking engine.
3. Google Business Profile: set the website to https://sapphirestayss.in. Bing Webmaster Tools: import from Search Console.
4. Update Booking.com and Agoda: King Room at ₹2,550, AC in every room, the same cancellation rule.
5. Send full-quality photos when available.
