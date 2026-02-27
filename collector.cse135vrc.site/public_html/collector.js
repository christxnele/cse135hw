/**
 * collector.js — CSE 135 HW3 Analytics Collector
 * Served from collector.cse135vrc.site
 * Collects static, performance, and activity data from the host page.
 */
(function () {
  'use strict';

  // CONSTANTS

  const SESSION_KEY        = '_cse135_sid';
  const IDLE_THRESHOLD     = 2000;   // ms of no activity before marking idle
  const FLUSH_INTERVAL     = 5000;   // ms between periodic activity flushes
  const MOUSEMOVE_THROTTLE = 100;    // ms between recorded mousemove positions
  const DEFAULT_ENDPOINT   = 'https://collector.cse135vrc.site/collect';

  // STATE

  let config          = { endpoint: DEFAULT_ENDPOINT, debug: false };
  let sessionId       = null;
  const activityBuffer  = [];
  let idleStartTime     = null;
  let idleTimer         = null;
  let lastMouseMoveTime = 0;
  const pageEnterTime   = new Date().toISOString();

  // Web Vitals accumulators
  let lcpValue = 0;
  let clsValue = 0;
  let inpValue = 0;
  const inpInteractions = [];

  // DEBUG LOGGING

  function log(...args) {
    if (config.debug) console.log('[Collector]', ...args);
  }


  // SESSION MANAGEMENT

  function getOrCreateSessionId() {
    let sid = sessionStorage.getItem(SESSION_KEY);
    if (!sid) {
      sid = Math.random().toString(36).substring(2) + Date.now().toString(36);
      sessionStorage.setItem(SESSION_KEY, sid);
    }
    // also set as a first-party cookie on the host page's domain so that server-side 
    // Apache/Nginx logs will record it, enabling log correlation.
    try {
      document.cookie = SESSION_KEY + '=' + sid + '; path=/; SameSite=Lax';
    } catch (e) { /* ignore cookie errors */ }
    return sid;
  }


  // TRANSPORT

  function send(payload) {
    payload.session = sessionId;
    if (config.debug) {
      console.log('[Collector] Would send:', payload);
      return;
    }
    const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
    let sent = false;
    if (navigator.sendBeacon) {
      sent = navigator.sendBeacon(config.endpoint, blob);
    }
    if (!sent) {
      fetch(config.endpoint, {
        method: 'POST',
        body: blob,
        keepalive: true
      }).catch(function (err) {
        log('send failed:', err.message);
      });
    }
  }

  function flushActivity() {
    if (!activityBuffer.length) return;
    send({
      type: 'activity',
      url: window.location.href,
      timestamp: new Date().toISOString(),
      events: activityBuffer.splice(0)
    });
  }


  // FEATURE DETECTION

  function detectImages() {
    return new Promise(function (resolve) {
      const img = new Image();
      img.onload  = function () { resolve(true); };
      img.onerror = function () { resolve(false); };
      // smallest valid GIF (1×1 transparent)
      img.src = 'data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==';
    });
  }

  function detectCSS() {
    try {
      const el = document.createElement('div');
      el.style.cssText = 'display:none;color:rgb(1,2,3)';
      document.body.appendChild(el);
      const computed = window.getComputedStyle(el).color;
      document.body.removeChild(el);
      return computed === 'rgb(1, 2, 3)';
    } catch (e) {
      return false;
    }
  }


  // STATIC DATA

  async function collectStaticData() {
    let networkInfo = {};
    if ('connection' in navigator) {
      const conn = navigator.connection;
      networkInfo = {
        effectiveType: conn.effectiveType,
        downlink:      conn.downlink,
        rtt:           conn.rtt,
        saveData:      conn.saveData
      };
    }

    const imagesEnabled = await detectImages();

    return {
      userAgent:        navigator.userAgent,
      language:         navigator.language,
      cookiesEnabled:   navigator.cookieEnabled,
      javascriptEnabled: true, 
      imagesEnabled:    imagesEnabled,
      cssEnabled:       detectCSS(),
      screenWidth:      window.screen.width,
      screenHeight:     window.screen.height,
      windowWidth:      window.innerWidth,
      windowHeight:     window.innerHeight,
      network:          networkInfo
    };
  }


  // PERFORMANCE DATA

  function collectPerformanceData() {
    const entries = performance.getEntriesByType('navigation');
    if (!entries.length) return {};

    const nav = entries[0];
    const origin = performance.timeOrigin;


    function round(n) { return Math.round(n * 100) / 100; }

    return {
      timingObject:    nav.toJSON ? nav.toJSON() : {},
      pageStarted:     new Date(origin + nav.fetchStart).toISOString(),
      pageEnded:       new Date(origin + nav.loadEventEnd).toISOString(),
      totalLoadTimeMs: Math.round(nav.loadEventEnd - nav.fetchStart),
      breakdown: {
        dnsLookup:     round(nav.domainLookupEnd   - nav.domainLookupStart),
        tcpConnect:    round(nav.connectEnd         - nav.connectStart),
        tlsHandshake:  nav.secureConnectionStart > 0
                         ? round(nav.connectEnd - nav.secureConnectionStart) : 0,
        ttfb:          round(nav.responseStart      - nav.requestStart),
        download:      round(nav.responseEnd        - nav.responseStart),
        domInteractive: round(nav.domInteractive    - nav.fetchStart),
        domComplete:   round(nav.domComplete        - nav.fetchStart),
        loadEvent:     round(nav.loadEventEnd       - nav.fetchStart)
      }
    };
  }


  // ERROR TRACKING  

  function setupErrorTracking() {
    // JS runtime errors
    window.addEventListener('error', function (event) {
      if (event instanceof ErrorEvent) {
        activityBuffer.push({
          type:      'js-error',
          timestamp: new Date().toISOString(),
          message:   event.message,
          source:    event.filename,
          line:      event.lineno,
          column:    event.colno,
          stack:     event.error ? event.error.stack : ''
        });
      }
    });

    // Unhandled promise rejections
    window.addEventListener('unhandledrejection', function (event) {
      const reason = event.reason;
      activityBuffer.push({
        type:      'promise-rejection',
        timestamp: new Date().toISOString(),
        message:   reason instanceof Error ? reason.message : String(reason),
        stack:     reason instanceof Error ? reason.stack : ''
      });
    });

    // Resource load failures (IMG, SCRIPT, LINK) — must use capture phase
    window.addEventListener('error', function (event) {
      if (!(event instanceof ErrorEvent)) {
        const target = event.target;
        if (target && (target.tagName === 'IMG' ||
                       target.tagName === 'SCRIPT' ||
                       target.tagName === 'LINK')) {
          activityBuffer.push({
            type:      'resource-error',
            timestamp: new Date().toISOString(),
            tagName:   target.tagName,
            src:       target.src || target.href || ''
          });
        }
      }
    }, true /* capture phase */);
  }


  // IDLE DETECTION

  function onActivity() {
    const now = Date.now();

    // If user is idle, record the idle period
    if (idleStartTime !== null) {
      activityBuffer.push({
        type:        'idle',
        idleEndedAt: new Date().toISOString(),
        durationMs:  now - idleStartTime
      });
      idleStartTime = null;
    }

    clearTimeout(idleTimer);
    idleTimer = setTimeout(function () {
      idleStartTime = Date.now();
    }, IDLE_THRESHOLD);
  }


  // ACTIVITY TRACKING  

  function setupActivityTracking() {
    // mousemovent
    document.addEventListener('mousemove', function (e) {
      onActivity();
      const now = Date.now();
      if (now - lastMouseMoveTime >= MOUSEMOVE_THROTTLE) {
        lastMouseMoveTime = now;
        activityBuffer.push({
          type:      'mousemove',
          timestamp: new Date().toISOString(),
          x:         e.clientX,
          y:         e.clientY
        });
      }
    }, { passive: true });

    // click — record which button
    document.addEventListener('click', function (e) {
      onActivity();
      activityBuffer.push({
        type:      'click',
        timestamp: new Date().toISOString(),
        x:         e.clientX,
        y:         e.clientY,
        button:    e.button
      });
    });

    // scroll — record scroll coordinates
    window.addEventListener('scroll', function () {
      onActivity();
      activityBuffer.push({
        type:      'scroll',
        timestamp: new Date().toISOString(),
        scrollX:   window.scrollX,
        scrollY:   window.scrollY
      });
    }, { passive: true });

    // keydown
    document.addEventListener('keydown', function (e) {
      onActivity();
      activityBuffer.push({
        type:      'keydown',
        timestamp: new Date().toISOString(),
        key:       e.key,
        code:      e.code
      });
    });

    // keyup
    document.addEventListener('keyup', function (e) {
      onActivity();
      activityBuffer.push({
        type:      'keyup',
        timestamp: new Date().toISOString(),
        key:       e.key,
        code:      e.code
      });
    });

    // kick off the initial idle timer
    idleTimer = setTimeout(function () {
      idleStartTime = Date.now();
    }, IDLE_THRESHOLD);
  }


  // WEB VITALS  

  function setupVitalsObservers() {
    if (typeof PerformanceObserver === 'undefined') return;

    // LCP 
    try {
      new PerformanceObserver(function (list) {
        const entries = list.getEntries();
        const last    = entries[entries.length - 1];
        lcpValue      = last.renderTime || last.loadTime;
      }).observe({ type: 'largest-contentful-paint', buffered: true });
    } catch (e) { /* unsupported */ }

    // CLS
    try {
      new PerformanceObserver(function (list) {
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) clsValue += entry.value;
        }
      }).observe({ type: 'layout-shift', buffered: true });
    } catch (e) { /* unsupported */ }

    // INP
    try {
      new PerformanceObserver(function (list) {
        for (const entry of list.getEntries()) {
          if (entry.interactionId) inpInteractions.push(entry.duration);
        }
        if (inpInteractions.length) {
          inpInteractions.sort(function (a, b) { return b - a; });
          inpValue = inpInteractions[0];
        }
      }).observe({ type: 'event', buffered: true, durationThreshold: 16 });
    } catch (e) { /* unsupported */ }
  }

  function getVitalsScore(metric, value) {
    const thresholds = { lcp: [2500, 4000], cls: [0.1, 0.25], inp: [200, 500] };
    const t = thresholds[metric];
    if (!t) return null;
    if (value <= t[0]) return 'good';
    if (value <= t[1]) return 'needsImprovement';
    return 'poor';
  }

  function sendVitals() {
    function r(n) { return Math.round(n * 100) / 100; }
    send({
      type:      'vitals',
      url:       window.location.href,
      timestamp: new Date().toISOString(),
      vitals: {
        lcp: { value: r(lcpValue),              score: getVitalsScore('lcp', lcpValue) },
        cls: { value: r(clsValue * 1000) / 1000, score: getVitalsScore('cls', clsValue) },
        inp: { value: r(inpValue),              score: getVitalsScore('inp', inpValue) }
      }
    });
  }


  // PAGE LIFECYCLE

  function setupPageLifecycle() {
    document.addEventListener('visibilitychange', function () {
      if (document.visibilityState === 'hidden') {
        activityBuffer.push({
          type:      'page-exit',
          timestamp: new Date().toISOString(),
          url:       window.location.href
        });
        flushActivity();
        sendVitals();
      } else {
        activityBuffer.push({
          type:      'page-enter',
          timestamp: new Date().toISOString(),
          url:       window.location.href
        });
      }
    });

    // pagehide covers bfcache navigation
    window.addEventListener('pagehide', function () {
      activityBuffer.push({
        type:      'page-hide',
        timestamp: new Date().toISOString(),
        url:       window.location.href
      });
      flushActivity();
    });
  }

  // MAIN INITIALIZATION

  async function init(options) {
    // Merge any provided options into config
    if (options) {
      if (options.endpoint) config.endpoint = options.endpoint;
      if (options.debug !== undefined) config.debug = options.debug;
    }

    sessionId = getOrCreateSessionId();

    // set up tracking immediately before page load
    setupErrorTracking();
    setupActivityTracking();
    setupVitalsObservers();
    setupPageLifecycle();

    // Record the initial page-enter event
    activityBuffer.push({
      type:      'page-enter',
      timestamp: pageEnterTime,
      url:       window.location.href
    });

    // Flush activity data periodically
    setInterval(flushActivity, FLUSH_INTERVAL);

    // Send the main pageview beacon after the page fully loads
    if (document.readyState === 'complete') {
      sendPageview();
    } else {
      window.addEventListener('load', function () {
        // Small delay to ensure loadEventEnd is populated in Navigation Timing
        setTimeout(sendPageview, 0);
      });
    }

    log('Collector initialized', config);
  }

  async function sendPageview() {
    const staticData = await collectStaticData();
    const perfData   = collectPerformanceData();

    send({
      type:        'pageview',
      url:         window.location.href,
      title:       document.title,
      referrer:    document.referrer,
      timestamp:   new Date().toISOString(),
      static:      staticData,
      performance: perfData
    });
  }


  // COMMAND QUEUE  


  function processQueue() {
    const queue = window._cq || [];
    if (Array.isArray(queue)) {
      for (const args of queue) {
        const method = args[0];
        const params = args.slice(1);
        if (method === 'init')    init(params[0]);
        else if (method === 'set') {
          if (params[0] && params[1] !== undefined) config[params[0]] = params[1];
        }
      }
    }

    // Replace the array with a live proxy so future pushes execute immediately
    window._cq = {
      push: function (args) {
        const method = args[0];
        const params = args.slice(1);
        if (method === 'init') init(params[0]);
        else if (method === 'set' && params[0]) config[params[0]] = params[1];
      }
    };
  }


  // ENTRY POINT

  // If the page pre-configured a command queue, process it (and let it call init).
  // Otherwise auto-initialize with defaults.
  if (window._cq && Array.isArray(window._cq) && window._cq.length) {
    processQueue();
  } else {
    processQueue(); // still replace _cq with live proxy
    init();
  }

})();
