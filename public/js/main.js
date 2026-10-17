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

  // Every element marked data-book opens the booking page, or WhatsApp until one is set up
  document.querySelectorAll('[data-book]').forEach(function (el) {
    var room = el.getAttribute('data-room');
    if (BOOKING_URL) {
      el.setAttribute('href', BOOKING_URL);
    } else {
      el.setAttribute('href', whatsappLink(
        'Hello Sapphire Stayss, I would like to book' + (room ? ' the ' + room : ' a room') + '. My dates are: '
      ));
    }
    el.setAttribute('target', '_blank');
    el.setAttribute('rel', 'noopener');
  });

  // Availability forms
  document.querySelectorAll('form[data-availability]').forEach(function (form) {
    var inEl = form.querySelector('[name="checkin"]');
    var outEl = form.querySelector('[name="checkout"]');
    var guestsEl = form.querySelector('[name="guests"]');
    var room = form.getAttribute('data-room');

    var start = new Date(); start.setDate(start.getDate() + 7);
    var end = new Date(start); end.setDate(end.getDate() + 1);
    inEl.value = iso(start);
    outEl.value = iso(end);
    inEl.min = iso(new Date());
    outEl.min = iso(new Date(Date.now() + 864e5));

    inEl.addEventListener('change', function () {
      var p = inEl.value.split('-');
      var next = new Date(+p[0], +p[1] - 1, +p[2] + 1);
      outEl.min = iso(next);
      if (outEl.value <= inEl.value) outEl.value = iso(next);
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (BOOKING_URL) {
        window.open(BOOKING_URL, '_blank', 'noopener');
        return;
      }
      var text = 'Hello Sapphire Stayss, is ' + (room ? 'the ' + room : 'a room') + ' available?\n' +
        'Check-in: ' + niceDate(inEl.value) + '\n' +
        'Check-out: ' + niceDate(outEl.value) + '\n' +
        'Guests: ' + guestsEl.value;
      window.open(whatsappLink(text), '_blank', 'noopener');
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
  var filters = document.querySelectorAll('.filters button');
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

  // Enquiry form: sends the details as a WhatsApp message
  var enquiry = document.getElementById('enquiry-form');
  if (enquiry) {
    enquiry.addEventListener('submit', function (e) {
      e.preventDefault();
      var f = enquiry.elements;
      var lines = ['Hello Sapphire Stayss, I have an enquiry.', 'Name: ' + f.name.value];
      if (f.phone.value) lines.push('Phone: ' + f.phone.value);
      if (f.dates.value) lines.push('Dates: ' + f.dates.value);
      if (f.guests.value) lines.push('Guests: ' + f.guests.value);
      lines.push('', f.message.value);
      window.open(whatsappLink(lines.join('\n')), '_blank', 'noopener');
    });
  }
})();
