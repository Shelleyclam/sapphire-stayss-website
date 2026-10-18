// Sapphire Stayss site behaviour. No libraries.
// Booking settings come from <body data-booking-url="" data-whatsapp="...">, written by build.py.
(function () {
  'use strict';

  var body = document.body;
  var BOOKING_URL = body.getAttribute('data-booking-url') || '';
  var WHATSAPP = body.getAttribute('data-whatsapp') || '';

  function whatsappLink(text) {
    return 'https://wa.me/' + WHATSAPP + '?text=' + encodeURIComponent(text);
  }

  function iso(d) {
    var m = String(d.getMonth() + 1).padStart(2, '0');
    var day = String(d.getDate()).padStart(2, '0');
    return d.getFullYear() + '-' + m + '-' + day;
  }

  function niceDate(value) {
    if (!value) return '';
    var p = value.split('-');
    var d = new Date(+p[0], +p[1] - 1, +p[2]);
    return d.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
  }

  // Mobile menu
  var menuBtn = document.getElementById('menu-btn');
  var nav = document.getElementById('site-nav');
  if (menuBtn && nav) {
    menuBtn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Date pairs: sensible defaults, and check-out always after check-in
  function setupDates(inEl, outEl, fromIn, fromOut) {
    var start = new Date(); start.setDate(start.getDate() + 7);
    var end = new Date(start); end.setDate(end.getDate() + 1);
    inEl.value = fromIn || iso(start);
    outEl.value = fromOut || iso(end);
    inEl.min = iso(new Date());
    outEl.min = iso(new Date(Date.now() + 864e5));
    inEl.addEventListener('change', function () {
      var p = inEl.value.split('-');
      var next = new Date(+p[0], +p[1] - 1, +p[2] + 1);
      outEl.min = iso(next);
      if (outEl.value <= inEl.value) outEl.value = iso(next);
    });
  }

  // Availability forms go to the booking page, or to the enquiry form with the details filled in
  document.querySelectorAll('form[data-availability]').forEach(function (form) {
    setupDates(form.querySelector('[name="checkin"]'), form.querySelector('[name="checkout"]'));
    form.addEventListener('submit', function (e) {
      if (BOOKING_URL) {
        e.preventDefault();
        window.open(BOOKING_URL, '_blank', 'noopener');
      }
    });
  });

  // Room strip arrows
  var strip = document.getElementById('strip');
  if (strip) {
    var step = function (dir) {
      var card = strip.querySelector('.room-card');
      strip.scrollBy({ left: dir * (card.offsetWidth + 28), behavior: 'smooth' });
    };
    var prev = document.getElementById('strip-prev');
    var next = document.getElementById('strip-next');
    if (prev) prev.addEventListener('click', function () { step(-1); });
    if (next) next.addEventListener('click', function () { step(1); });
  }

  // Gallery filters
  var filters = document.querySelectorAll('.filters [data-filter]');
  filters.forEach(function (btn) {
    btn.addEventListener('click', function () {
      var cat = btn.getAttribute('data-filter');
      filters.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
      document.querySelectorAll('.masonry figure').forEach(function (fig) {
        fig.hidden = cat !== 'all' && fig.getAttribute('data-cat') !== cat;
      });
    });
  });

  // Lightbox for any [data-lightbox] group of buttons
  var box = document.getElementById('lightbox');
  if (box) {
    var img = box.querySelector('img');
    var caption = box.querySelector('.lightbox-caption');
    var items = [];
    var index = 0;
    var lastFocus = null;

    var show = function (i) {
      index = (i + items.length) % items.length;
      var it = items[index];
      img.src = it.getAttribute('data-full');
      img.alt = it.querySelector('img').alt;
      caption.textContent = it.querySelector('img').alt + '  ·  ' + (index + 1) + ' / ' + items.length;
    };
    var close = function () {
      box.hidden = true;
      body.style.overflow = '';
      if (lastFocus) lastFocus.focus();
    };

    document.querySelectorAll('[data-lightbox]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        items = Array.prototype.filter.call(
          document.querySelectorAll('[data-lightbox="' + btn.getAttribute('data-lightbox') + '"]'),
          function (el) { return !el.closest('[hidden]'); }
        );
        lastFocus = btn;
        show(items.indexOf(btn));
        box.hidden = false;
        body.style.overflow = 'hidden';
        box.querySelector('[data-close]').focus();
      });
    });
    box.querySelector('[data-close]').addEventListener('click', close);
    box.querySelector('[data-prev]').addEventListener('click', function () { show(index - 1); });
    box.querySelector('[data-next]').addEventListener('click', function () { show(index + 1); });
    box.addEventListener('click', function (e) { if (e.target.classList.contains('lightbox-stage')) close(); });
    document.addEventListener('keydown', function (e) {
      if (box.hidden) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') show(index - 1);
      if (e.key === 'ArrowRight') show(index + 1);
    });
  }

  // Enquiry form: filled in from the availability form, sent as a WhatsApp message
  var enquiry = document.getElementById('enquiry-form');
  if (enquiry) {
    var f = enquiry.elements;
    var params = new URLSearchParams(window.location.search);
    setupDates(f.checkin, f.checkout, params.get('checkin'), params.get('checkout'));
    if (params.get('guests')) f.guests.value = params.get('guests');
    if (params.get('room')) f.room.value = params.get('room');

    enquiry.querySelectorAll('[data-step]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var n = (parseInt(f.guests.value, 10) || 1) + parseInt(btn.getAttribute('data-step'), 10);
        f.guests.value = Math.max(1, Math.min(20, n));
      });
    });

    enquiry.addEventListener('submit', function (e) {
      e.preventDefault();
      var room = f.room.value ? f.room.options[f.room.selectedIndex].text : 'Any room';
      var lines = [
        'Hello Sapphire Stayss, I would like to book.',
        'Name: ' + f.name.value,
        'Check-in: ' + niceDate(f.checkin.value),
        'Check-out: ' + niceDate(f.checkout.value),
        'Guests: ' + f.guests.value,
        'Room: ' + room
      ];
      if (f.phone.value) lines.splice(2, 0, 'Phone: ' + f.phone.value);
      if (f.message.value) lines.push('', f.message.value);
      window.open(whatsappLink(lines.join('\n')), '_blank', 'noopener');
    });
  }
  // Explore: filter places by category and time of day
  var placeGrid = document.getElementById('place-grid');
  if (placeGrid) {
    var cat = 'all';
    var time = 'any';
    var count = document.getElementById('place-count');
    var empty = document.getElementById('place-empty');
    var apply = function () {
      var shown = 0;
      placeGrid.querySelectorAll('.place').forEach(function (card) {
        var ok = (cat === 'all' || card.getAttribute('data-cat') === cat) &&
                 (time === 'any' || card.getAttribute('data-times').split(' ').indexOf(time) !== -1);
        card.hidden = !ok;
        if (ok) shown++;
      });
      count.textContent = shown + (shown === 1 ? ' place' : ' places');
      empty.hidden = shown !== 0;
    };
    var wire = function (attr, set) {
      var btns = document.querySelectorAll('[' + attr + ']');
      btns.forEach(function (btn) {
        btn.addEventListener('click', function () {
          btns.forEach(function (b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
          set(btn.getAttribute(attr));
          apply();
        });
      });
    };
    wire('data-place-cat', function (v) { cat = v; });
    wire('data-place-time', function (v) { time = v; });
  }
})();
