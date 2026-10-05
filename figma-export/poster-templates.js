const templates = {
  birthday: [
    ['kicker', 'Kicker'], ['title', 'Title'], ['name', 'Person name'], ['message', 'Message', 'textarea']
  ],
  hiring: [
    ['title', 'Title', 'textarea'], ['role', 'Role'], ['experience', 'Experience'], ['mode', 'Work mode'], ['message', 'Call to action', 'textarea']
  ],
  anniversary: [
    ['kicker', 'Kicker'], ['title', 'Title'], ['name', 'Person name'], ['years', 'Milestone'], ['message', 'Message', 'textarea']
  ],
  festival: [
    ['kicker', 'Kicker'], ['title', 'Title'], ['name', 'Person name'], ['message', 'Message', 'textarea']
  ],
  company: [
    ['kicker', 'Kicker'], ['title', 'Title'], ['name', 'Subtitle'], ['message', 'Message', 'textarea']
  ]
};

const picker = document.querySelector('#poster-picker');
const sizePicker = document.querySelector('#size-picker');
const fields = document.querySelector('#editor-fields');
const photoField = document.querySelector('.file-field');
const status = document.querySelector('#export-status');
const requestedPoster = new URLSearchParams(window.location.search).get('poster');
const exportParams = new URLSearchParams(window.location.search);

if (templates[requestedPoster]) picker.value = requestedPoster;

function selectedPoster() {
  return document.querySelector(`[data-poster="${picker.value}"]`);
}

function buildEditor() {
  document.querySelectorAll('.poster').forEach(poster => poster.classList.toggle('is-selected', poster.dataset.poster === picker.value));
  fields.replaceChildren();
  const poster = selectedPoster();
  templates[picker.value].forEach(([key, label, type = 'input']) => {
    const wrapper = document.createElement('label');
    wrapper.textContent = label;
    const control = document.createElement(type);
    const target = poster.querySelector(`[data-field="${key}"]`);
    control.value = target.innerText.replace(/\n/g, ' ').trim();
    control.addEventListener('input', () => target.innerText = control.value);
    wrapper.append(control);
    fields.append(wrapper);
  });
  photoField.classList.toggle('is-hidden', picker.value !== 'anniversary');
}

picker.addEventListener('change', buildEditor);
document.querySelector('#print-poster').addEventListener('click', () => window.print());
document.querySelector('#download-poster').addEventListener('click', downloadPoster);
document.querySelector('#photo-input').addEventListener('change', event => {
  const [file] = event.target.files;
  if (!file) return;
  const reader = new FileReader();
  reader.addEventListener('load', () => document.querySelector('[data-photo]').src = reader.result);
  reader.readAsDataURL(file);
});

buildEditor();

function applyExportParameters() {
  if (exportParams.get('export') !== 'png') return;
  document.body.classList.add('export-mode');
  document.documentElement.style.setProperty('--export-width', `${Number(exportParams.get('width')) || 1080}px`);
  document.documentElement.style.setProperty('--export-height', `${Number(exportParams.get('height')) || 1350}px`);

  const poster = selectedPoster();
  templates[picker.value].forEach(([key]) => {
    const value = exportParams.get(key);
    if (value !== null) {
      const target = poster.querySelector(`[data-field="${key}"]`);
      target.innerText = value;
      if (key === 'years' && value.trim() === '') target.style.display = 'none';
    }
  });
  const photo = exportParams.get('photo');
  if (picker.value === 'anniversary' && photo) poster.querySelector('[data-photo]').src = photo;
}

applyExportParameters();

/* ============================================================
   Celebration animation injection (GSAP)
   Builds confetti, balloons, and glitters inside each poster's
   .celebration layer and animates them with GSAP timelines.

   - Balloons float up slowly and naturally (gentle sway, ease).
   - Birthday confetti falls gently.
   - Anniversary confetti "pops" and blasts from both top corners.
   - Glitters twinkle.

   Determinism: element layout uses a seeded PRNG so every headless
   frame render produces identical positions; only the GSAP timeline
   progress differs. The GIF renderer passes ?frame=0..1 and we seek
   the timeline to that progress, freezing a smooth, natural frame.

   The static PNG export hides the layer (plain professional poster).
   ============================================================ */

// Seeded PRNG so all GIF frames share identical element layout.
function mulberry32(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6D2B79F5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rand = mulberry32(20260812);

const CELEBRATION = {
  birthday: {
    confetti: 0,      // no confetti on birthday — balloons + glitters only
    balloons: 5,
    glitters: 14,
    colors: ['#ef3829', '#fdb917', '#0076be', '#00a95c', '#f04b13'],
  },
  anniversary: {
    confetti: 24,
    balloons: 0,      // no balloons on work anniversary — confetti pop + glitters only
    glitters: 12,
    colors: ['#0076be', '#fdb917', '#ef3829', '#00a95c', '#f04b13'],
  },
};

function randomBetween(min, max) {
  return min + rand() * (max - min);
}

function buildCelebration(poster) {
  const layer = poster.querySelector('[data-celebration]');
  if (!layer) return;
  const config = CELEBRATION[poster.dataset.poster];
  if (!config) return;
  const isAnniversary = poster.dataset.poster === 'anniversary';
  const fragment = document.createDocumentFragment();
  const confetti = [];
  const balloons = [];
  const glitters = [];

  // Confetti
  for (let i = 0; i < config.confetti; i++) {
    const piece = document.createElement('i');
    piece.className = 'confetti-piece';
    const size = randomBetween(6, 11);
    if (isAnniversary) {
      // Start at one of the two top corners for the pop/blast effect.
      const leftCorner = i % 2 === 0;
      piece.style.left = leftCorner ? '0px' : '540px';
      piece.style.top = '0px';
      piece.style.marginLeft = `${-size / 2}px`;
      piece.style.marginTop = `${-size / 2}px`;
    } else {
      piece.style.left = `${randomBetween(0, 100)}%`;
      piece.style.top = '-24px';
    }
    piece.style.width = `${size}px`;
    piece.style.height = `${size * randomBetween(0.5, 0.9)}px`;
    piece.style.background = config.colors[i % config.colors.length];
    fragment.append(piece);
    confetti.push(piece);
  }

  // Balloons — spread evenly across the full poster width so they never
  // bunch together in the centre. Each gets its own horizontal lane.
  for (let i = 0; i < config.balloons; i++) {
    const balloon = document.createElement('i');
    balloon.className = 'balloon';
    // Evenly distribute across 6%..94% with a little jitter per balloon.
    const lane = 6 + (i / Math.max(1, config.balloons - 1)) * 88;
    balloon.style.left = `${lane + randomBetween(-3, 3)}%`;
    balloon.style.setProperty('--balloon-color', config.colors[(i + 2) % config.colors.length]);
    fragment.append(balloon);
    balloons.push(balloon);
  }

  // Glitters
  for (let i = 0; i < config.glitters; i++) {
    const glitter = document.createElement('i');
    glitter.className = 'glitter';
    glitter.style.left = `${randomBetween(2, 96)}%`;
    glitter.style.top = `${randomBetween(5, 90)}%`;
    fragment.append(glitter);
    glitters.push(glitter);
  }

  layer.replaceChildren(fragment);

  // Build the GSAP timeline.
  if (!window.gsap) return;
  const tl = gsap.timeline({ repeat: -1, defaults: { ease: 'none' } });
  // Frame capture compresses progress 0..1 into a short GIF. Use an 8s loop
  // so exported motion is slower and closer to on-screen pacing.
  const capture = exportParams.get('frame') !== null;
  const loopSeconds = 8;

  // Balloons: very slow, natural float with gentle sway. Each balloon has
  // its own duration and start offset so they drift independently instead of
  // moving together. They rise from the bottom to the top over a long time.
  balloons.forEach((b, i) => {
    const dur = capture ? loopSeconds : randomBetween(20, 25);
    const start = capture
      ? (i / Math.max(1, balloons.length)) * loopSeconds
      : i * randomBetween(2.5, 4);
    const sway = randomBetween(-40, 40);        // wider, natural horizontal drift
    tl.fromTo(b, { y: 0, opacity: 0 }, { y: -980, opacity: 1, duration: dur, ease: 'power1.inOut' }, start);
    tl.to(b, { x: sway, duration: dur / 2, ease: 'sine.inOut', yoyo: true, repeat: 1 }, start);
  });

  if (isAnniversary) {
    // Keep both cards centered and completely static.
    const blueCard = poster.querySelector('.photo-stack .blue-card');
    const photoCard = poster.querySelector('.photo-stack figure');
    if (blueCard && photoCard) {
      gsap.set([blueCard, photoCard], { transformOrigin: '50% 0%', opacity: 1 });
      tl.set(blueCard, { x: 0, y: 0, rotation: -7, scale: 1 }, 0);
      tl.set(photoCard, { x: 0, y: 0, rotation: 0, scale: 1 }, 0);
    }
    // Confetti begins halfway through the card movement, then falls
    // continuously from both top corners without a burst or pause.
    const confettiStart = 1.1;
    confetti.forEach((c, i) => {
      const leftCorner = i % 2 === 0;
      // The right-side pieces are anchored at x=540 in CSS, so their GSAP
      // offset must be negative to keep them inside the poster at launch.
      const startX = leftCorner ? randomBetween(8, 110) : randomBetween(-110, -8);
      const drift = leftCorner ? randomBetween(-55, 80) : randomBetween(-80, 55);
      const fallDuration = capture ? randomBetween(4.2, 5) : randomBetween(5, 7);
      const start = confettiStart + i * (capture ? 0.08 : 0.14);
      tl.fromTo(c, { x: startX, y: -24, scale: 1, opacity: 0 },
        { x: startX + drift, y: 760, scale: 1, opacity: 0.95,
          rotation: randomBetween(360, 720), duration: fallDuration, ease: 'none' }, start);
      tl.to(c, { opacity: 0, duration: 0.35, ease: 'power1.out' }, start + fallDuration - 0.35);
    });
  } else {
    // Birthday footer: gently morph the top edge and drift the pattern
    // horizontally so the yellow section feels like a visible calm sea wave.
    const wavePath = poster.querySelector('.birthday-footer clipPath path');
    if (wavePath) {
      const calmWave = 'M0 78C28 100 48 58 78 62C110 66 126 102 158 76C186 54 194 34 220 42C250 50 258 104 290 88C326 70 340 48 366 56C396 64 408 108 440 84C474 58 494 68 540 70V285H0Z';
      const deeperWave = 'M0 108C30 124 52 72 82 76C114 80 132 116 164 90C194 66 202 48 228 56C258 64 268 118 300 102C338 82 350 62 378 70C408 78 420 122 450 98C482 76 500 86 540 88V285H0Z';
      const waveDur = capture ? loopSeconds / 4 : 2.8;
      tl.to(wavePath, { attr: { d: calmWave }, duration: waveDur, ease: 'sine.inOut' }, 0);
      tl.to(wavePath, { attr: { d: deeperWave }, duration: waveDur, ease: 'sine.inOut' }, waveDur);
      tl.to(wavePath, { attr: { d: calmWave }, duration: waveDur, ease: 'sine.inOut' }, waveDur * 2);
      tl.to(wavePath, { attr: { d: 'M0 92C25 98 42 72 72 68C105 63 119 86 151 74C178 65 184 42 207 38C238 32 248 84 283 88C323 94 330 67 354 58C382 47 395 91 431 89C463 87 481 70 540 77V285H0Z' }, duration: waveDur, ease: 'sine.inOut' }, waveDur * 3);
      gsap.set(poster.querySelector('.birthday-copy'), { x: 0, y: 0, rotation: 0 });
    }

    // Birthday confetti: gentle fall with rotation.
    confetti.forEach((c, i) => {
      const dur = capture ? randomBetween(4, 5) : randomBetween(3.5, 5);
      const start = i * (capture ? 0.12 : 0.2);
      tl.fromTo(c, { y: -30, opacity: 0.5 }, { y: 720, opacity: 0.95, duration: dur, ease: 'power1.in' }, start);
      tl.to(c, { rotation: randomBetween(360, 720), duration: dur, ease: 'none' }, start);
    });
  }

  // Glitters: twinkle.
  glitters.forEach((g, i) => {
    tl.fromTo(g, { scale: 0.4, opacity: 0.1 },
      { scale: 1.35, opacity: 1, duration: capture ? 1 : 1.2, ease: 'sine.inOut', yoyo: true, repeat: 1 }, i * (capture ? 0.18 : 0.3));
  });

  if (capture) tl.duration(loopSeconds);

  poster._celebrationTimeline = tl;
}

document.querySelectorAll('.poster').forEach(buildCelebration);

/* GIF frame capture: seek the GSAP timeline to the requested frame.
   frame is a 0..1 progress value; the renderer freezes the animation
   at that point in the loop. */
const frameParam = exportParams.get('frame');
if (frameParam !== null) {
  const progress = Math.min(1, Math.max(0, Number(frameParam) || 0));
  document.body.classList.add('frame-mode');
  const poster = selectedPoster();
  const tl = poster && poster._celebrationTimeline;
  if (tl) tl.progress(progress).pause();
}

function showStatus(message) {
  status.textContent = message;
  status.classList.add('is-visible');
  clearTimeout(showStatus.timer);
  showStatus.timer = setTimeout(() => status.classList.remove('is-visible'), 3500);
}

function fileToDataUrl(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

async function inlineImages(node) {
  const images = [...node.querySelectorAll('img')];
  await Promise.all(images.map(async image => {
    if (!image.src || image.src.startsWith('data:')) return;
    const response = await fetch(image.src);
    if (!response.ok) throw new Error(`Could not load ${image.src}`);
    image.src = await fileToDataUrl(await response.blob());
  }));

  const svgImages = [...node.querySelectorAll('svg image[href]')];
  await Promise.all(svgImages.map(async image => {
    const source = image.getAttribute('href');
    if (!source || source.startsWith('data:')) return;
    const response = await fetch(new URL(source, document.baseURI));
    if (!response.ok) throw new Error(`Could not load ${source}`);
    image.setAttribute('href', await fileToDataUrl(await response.blob()));
  }));
}

function safeFilename(value) {
  return value.toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'poster';
}

function shouldCropToFill(type, width, height) {
  return (type === 'birthday' && width / height !== 4 / 5) ||
    (type === 'anniversary' && height > width && width / height !== 4 / 5);
}

function drawGridBackground(context, width, height, step, originX, originY) {
  context.fillStyle = '#fff';
  context.fillRect(0, 0, width, height);
  context.strokeStyle = 'rgb(237, 246, 251)';
  context.lineWidth = 2;
  context.beginPath();
  for (let x = originX % step; x < width; x += step) {
    context.moveTo(x, 0); context.lineTo(x, height);
  }
  for (let y = originY % step; y < height; y += step) {
    context.moveTo(0, y); context.lineTo(width, y);
  }
  context.stroke();
}

async function posterDataUrl(poster) {
  const clone = poster.cloneNode(true);
  clone.classList.add('is-selected');
  clone.style.cssText = 'display:block;width:540px;height:675px;box-shadow:none;margin:0;';
  await inlineImages(clone);

  const css = await fetch('poster-templates.css').then(response => response.text());
  const markup = new XMLSerializer().serializeToString(clone);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="540" height="675" viewBox="0 0 540 675"><foreignObject width="540" height="675"><div xmlns="http://www.w3.org/1999/xhtml"><style>${css}</style>${markup}</div></foreignObject></svg>`;
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svg)}`;
}

function loadImage(source) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error('The poster could not be rendered.'));
    image.src = source;
  });
}

async function downloadPoster() {
  const button = document.querySelector('#download-poster');
  button.disabled = true;
  button.textContent = 'Preparing…';
  showStatus('Preparing your PNG…');

  try {
    await document.fonts.ready;
    const [width, height] = sizePicker.value.split('x').map(Number);
    const poster = selectedPoster();
    const renderedPoster = await loadImage(await posterDataUrl(poster));
    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const context = canvas.getContext('2d');
    const ratios = [width / 540, height / 675];
    const fillsCanvas = shouldCropToFill(picker.value, width, height);
    const scale = fillsCanvas ? Math.max(...ratios) : Math.min(...ratios);
    const drawWidth = 540 * scale;
    const drawHeight = 675 * scale;
    const drawTop = width === height ? 0 : (height - drawHeight) / 2;
    const drawLeft = (width - drawWidth) / 2;
    drawGridBackground(context, width, height, 36 * scale, drawLeft, drawTop);
    context.drawImage(renderedPoster, drawLeft, drawTop, drawWidth, drawHeight);

    const identifyingField = poster.querySelector('[data-field="name"], [data-field="role"]');
    const filename = `${picker.value}-${safeFilename(identifyingField?.textContent || '')}-${width}x${height}.png`;
    const link = document.createElement('a');
    link.download = filename;
    link.href = canvas.toDataURL('image/png', 1);
    link.click();
    showStatus(`Saved ${filename}`);
  } catch (error) {
    console.error(error);
    showStatus('Export failed. Open this page through a local web server and try again.');
  } finally {
    button.disabled = false;
    button.textContent = 'Save as PNG';
  }
}
