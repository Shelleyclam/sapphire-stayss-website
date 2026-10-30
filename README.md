# Sapphire Stayss website

The website for Sapphire Stayss, Yelagiri: https://sapphirestayss.in

## What's in this folder

| Folder / file | What it is |
|---|---|
| `public/` | **The finished website.** This is what gets uploaded to the hosting. |
| `content/site.json` | All the facts the pages use: rooms, prices, phone numbers, policies, attractions, reviews, gallery captions. |
| `build.py` | Turns `content/site.json` into the HTML pages in `public/`. |
| `public/css/style.css` | The look of the site (colours, fonts, spacing). |
| `public/js/main.js` | Menu, booking buttons, gallery viewer, enquiry form. |
| `public/img/` | Photos, already resized for the web (two sizes each). |
| `public/.htaccess` | Hosting settings: https, old-page redirects, caching. |

## Pages

Home, About, Rooms, one page per room (6), Gallery, Things to do in Yelagiri, Policies & FAQ (`faq.html`),
How to reach Yelagiri from Bangalore, How to reach Yelagiri from Chennai, Contact, Terms, Privacy,
Cancellation & Refund Policy, and a "page not found" page. `policies.html` is the old FAQ address and
forwards to `faq.html`.

The build also writes `sitemap.xml`, `robots.txt` (welcomes Google, Bing and the AI search crawlers)
and `llms.txt` (a plain-text summary of the resort for AI assistants). Every page carries schema.org
data: `Hotel` on every page, `HotelRoom` with prices on the room pages, `FAQPage`, `BreadcrumbList`
and a list of attractions on the Explore page.

## Facts still to fill in (TODOs)

Where a fact is missing, the page shows a yellow **TODO** mark and the fact is left out of the
schema and `llms.txt`. Fill the empty fields in `content/site.json` (`business`, `business.about`,
`reviews`, `travel`), run `python3 build.py`, and it prints every TODO that is left.
Don't go live until that list is empty.

## Viewing the site on your computer

1. On the GitHub page, click the green **Code** button, then **Download ZIP**.
2. Unzip it, open the `public` folder and double-click `index.html`. The site opens in your browser.

Or, to view it at `http://localhost:8000` (needs Python): open a terminal in the `public` folder,
run `python3 -m http.server 8000`, then open http://localhost:8000 in your browser.

## Making a change

1. Edit `content/site.json` (for prices, phone numbers, room details and so on), or the page text in `build.py`.
2. Run `python3 build.py`. It rewrites the HTML files in `public/`.
3. Upload `public/` to the hosting (see below).

Don't edit the `.html` files in `public/` by hand. The next build overwrites them.

## Turning on online booking

While `booking.url` in `content/site.json` is empty, every **Book** and **Check availability**
button opens WhatsApp with the guest's dates filled in.

When the channel manager's booking page is ready, paste its link into `booking.url` and run
`python3 build.py`. From then on, every booking button opens the booking page.

## Uploading to GoDaddy (cPanel)

1. Log in to GoDaddy, open **Web Hosting → cPanel Admin → File Manager**.
2. Open the `public_html` folder. Back up the old site first (select all → Compress → download the zip).
3. Upload the **contents** of `public/` (not the folder itself) into `public_html`.
   Turn on "Show hidden files" in File Manager settings so `.htaccess` uploads too.
4. Check that https://sapphirestayss.in opens the new site.

Before go-live, check where the domain's DNS points. If it points to GoDaddy's
"Websites + Marketing" builder rather than the cPanel hosting, the DNS "A" record must be changed
to the cPanel hosting's IP address.

## Still to confirm with the owner

- The "14 hairpin bends", "highest point in Yelagiri" and boating lines.
- Replacement photos: daytime exterior, garden, views, and the Swamymalai trek.
