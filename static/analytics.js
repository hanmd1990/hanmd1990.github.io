/* HMD Lab GA4: automatic measurement on the official production host. */
(() => {
  'use strict';
  if (location.hostname !== 'hanmd1990.github.io') return;
  const id = 'G-WPKN8C626L';
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
