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

Home, Rooms, one page per room (6), Gallery, Explore Yelagiri, Policies & FAQ, Contact,
Terms, Privacy, Cancellation & Refund Policy, and a "page not found" page.

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

- Breakfast time (the home page says 8:00).
- The age limit for children.
- Whether alcohol is allowed on the property.
- The "14 hairpin bends", "highest point in Yelagiri" and boating lines.
- Replacement photos: daytime exterior, garden, views, and the Swamymalai trek.
