/* HMD Lab GA4: load only after consent, on the official production host. */
(() => {
  'use strict';
  if (location.hostname !== 'hanmd1990.github.io') return;
  const id = 'G-WPKN8C626L', key = 'hmd-analytics-consent-v1';
  let started = false;
  const disabled = navigator.globalPrivacyControl === true || navigator.doNotTrack === '1';
  const read = () => { try { return localStorage.getItem(key); } catch { return null; } };
  const remember = value => { try { localStorage.setItem(key, value); } catch { /* Current page only. */ } };
  window.dataLayer = window.dataLayer || [];
  const gtag = function () { window.dataLayer.push(arguments); };
  gtag('consent', 'default', { analytics_storage: 'denied', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
  function start() {
    if (started || disabled) return;
    started = true;
    window['ga-disable-' + id] = false;
    gtag('consent', 'update', { analytics_storage: 'granted' });
    gtag('js', new Date());
    gtag('config', id, {
      allow_google_signals: false,
      allow_ad_personalization_signals: false,
      page_location: location.origin + location.pathname,
      page_referrer: document.referrer ? document.referrer.split(/[?#]/)[0] : ''
    });
    const script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
    document.head.append(script);
  }
  const style = document.createElement('style');
  style.textContent = '.hmd-consent{position:fixed;bottom:16px;left:16px;right:16px;z-index:10000;max-width:620px;margin:auto;padding:16px 18px;background:#fff;color:#24364b;border:1px solid #d8dfe5;border-radius:8px;box-shadow:0 4px 24px #102d4814;font:14px/1.5 Arial,sans-serif}.hmd-consent[hidden]{display:none}.hmd-consent p{margin:0 0 10px}.hmd-consent-actions{display:flex;flex-wrap:wrap;gap:8px}.hmd-consent button{font:inherit;color:#24364b;background:#f1f3f5;border:1px solid #c9d1d9;border-radius:4px;padding:6px 12px;cursor:pointer}.hmd-consent button:hover{background:#e4e9ee}.hmd-consent button:focus-visible,.hmd-privacy:focus-visible{outline:2px solid #335d80;outline-offset:3px}.hmd-consent a{color:#335d80;text-decoration:underline}.hmd-privacy{display:block;margin:20px auto;padding:4px 8px;border:0;background:transparent;color:#657485;font:12px Arial,sans-serif;cursor:pointer}.hmd-consent-note{font-size:12px;color:#657485}';
  document.head.append(style);
  const panel = document.createElement('section');
  panel.className = 'hmd-consent'; panel.setAttribute('aria-label', 'Website analytics preferences');
  panel.innerHTML = '<p>May we use Google Analytics to understand visits, popular pages and approximate country, region and city? Analytics cookies are optional.</p><p class="hmd-consent-note">Reports are restricted to the site owner. Google Analytics does not store individual IP addresses. <a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener noreferrer">How Google uses data</a>. You can change your choice below at any time.</p><div class="hmd-consent-actions"><button type="button" data-choice="accepted">Accept analytics</button><button type="button" data-choice="declined">Decline analytics</button><button type="button" data-close hidden>Close</button></div>';
  const settings = document.createElement('button');
  settings.type = 'button'; settings.className = 'hmd-privacy'; settings.textContent = 'Privacy & analytics';
  const close = panel.querySelector('[data-close]');
  panel.addEventListener('click', event => {
    const button = event.target.closest('button');
    if (!button) return;
    if (button.hasAttribute('data-close')) { panel.hidden = true; settings.focus(); return; }
    const value = button.dataset.choice;
    remember(value);
    if (value === 'accepted' && !disabled) start();
    else {
      window['ga-disable-' + id] = true;
      gtag('consent', 'update', { analytics_storage: 'denied' });
      // Remove this site's GA cookies when consent is withdrawn.
      for (const cookie of document.cookie.split(';')) {
        const name = cookie.trim().split('=')[0];
        if (!/^_ga(?:_|$)/.test(name)) continue;
        for (const domain of ['', ';domain=hanmd1990.github.io', ';domain=.hanmd1990.github.io'])
          document.cookie = name + '=; Max-Age=0; path=/' + domain + '; SameSite=Lax; Secure';
      }
      if (started) { location.reload(); return; }
    }
    panel.hidden = true; settings.focus();
  });
  settings.addEventListener('click', () => { panel.hidden = false; close.hidden = false; panel.querySelector('button').focus(); });
  document.body.append(settings, panel);
  const saved = read();
  panel.hidden = saved !== null || disabled;
  if (disabled) {
    panel.querySelector('p').textContent = 'Analytics is disabled because your browser sends a privacy preference. No Google Analytics script is loaded.';
    panel.querySelector('[data-choice="accepted"]').disabled = true;
  } else if (saved === 'accepted') start();
})();
