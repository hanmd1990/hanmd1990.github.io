/* Apple MapKit JS enhancement; keep the campus map if authorization/search fails. */
(() => {
  'use strict';
  const config = window.HMD_APPLE_MAPS;
  const canvas = document.getElementById('contact-apple-map');
  if (!canvas || !config || !config.token) return;
  const figure = document.getElementById('contact-map');
  const fallback = figure.querySelector('.lab-contact-map-fallback');
  const caption = document.getElementById('contact-map-caption');
  let map;
  let finished = false;
  const restore = () => {
    finished = true;
    if (map) { map.destroy(); map = null; }
    canvas.hidden = true;
    fallback.hidden = false;
    caption.textContent = 'Campus map · Click to enlarge';
  };
  const timeout = window.setTimeout(restore, 15000);
  const script = document.createElement('script');
  script.src = 'https://cdn.apple-mapkit.com/mk/5.x.x/mapkit.js';
  script.onerror = () => { window.clearTimeout(timeout); restore(); };
  script.onload = () => {
    if (finished) return;
    try {
      mapkit.init({ authorizationCallback: done => done(config.token), language: 'zh-CN' });
      new mapkit.Search({ language: 'zh-CN' }).search(config.query, (error, data) => {
        if (finished) return;
        window.clearTimeout(timeout);
        // Never substitute the university entrance or an unverified guessed pin.
        const place = !error && data && data.places.find(item =>
          /新奥工学/.test(item.name) && item.coordinate &&
          item.coordinate.latitude > 39.9 && item.coordinate.latitude < 40.1 &&
          item.coordinate.longitude > 116.2 && item.coordinate.longitude < 116.4);
        if (!place) { restore(); return; }
        try {
          canvas.hidden = false;
          map = new mapkit.Map(canvas, {
            isScrollEnabled: true, isZoomEnabled: true, showsZoomControl: true,
            region: new mapkit.CoordinateRegion(place.coordinate, new mapkit.CoordinateSpan(0.006, 0.006))
          });
          map.addAnnotation(new mapkit.MarkerAnnotation(place.coordinate, {
            title: '北京大学新奥工学大楼', subtitle: 'Peking University', color: '#142B55'
          }));
          fallback.hidden = true;
          caption.textContent = '北京大学新奥工学大楼 · Drag to explore, scroll to zoom';
          finished = true;
        } catch (failure) { restore(); }
      });
    } catch (failure) { window.clearTimeout(timeout); restore(); }
  };
  document.head.append(script);
})();
