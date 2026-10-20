/* HMD Lab GA4: automatic measurement on the official production host. */
(() => {
  'use strict';
  if (location.hostname !== 'hanmd1990.github.io') return;
  const id = 'G-WPKN8C626L';
  const style = document.createElement('style');
  style.textContent = '.hmd-analytics-notice{margin:20px auto;padding:4px 18px;max-width:900px;text-align:center;color:#657485;font:11px/1.5 Arial,sans-serif}.hmd-analytics-notice a{color:inherit;text-decoration:underline}';
  document.head.append(style);
  const notice = document.createElement('p');
  notice.className = 'hmd-analytics-notice';
  notice.innerHTML = 'This site uses Google Analytics to measure visits and approximate location. <a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener noreferrer">How Google uses data</a>.';
  document.body.append(notice);
  let previouslyDeclined = false;
  try { previouslyDeclined = localStorage.getItem('hmd-analytics-consent-v1') === 'declined'; } catch { /* No stored preference available. */ }
  if (navigator.globalPrivacyControl === true || navigator.doNotTrack === '1' || previouslyDeclined) {
    window['ga-disable-' + id] = true;
    return;
  }
  if (document.querySelector('script[data-hmd-ga-tag]')) return;
  window.dataLayer = window.dataLayer || [];
  const gtag = function () { window.dataLayer.push(arguments); };
  gtag('js', new Date());
  gtag('config', id, {
    allow_google_signals: false,
    allow_ad_personalization_signals: false,
    page_location: location.origin + location.pathname,
    page_referrer: document.referrer ? document.referrer.split(/[?#]/)[0] : ''
  });
  const script = document.createElement('script');
  script.async = true;
  script.dataset.hmdGaTag = 'true';
  script.src = 'https://www.googletagmanager.com/gtag/js?id=' + id;
  document.head.append(script);
})();
