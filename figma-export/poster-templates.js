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
    if (value !== null) poster.querySelector(`[data-field="${key}"]`).innerText = value;
  });
  const photo = exportParams.get('photo');
  if (picker.value === 'anniversary' && photo) poster.querySelector('[data-photo]').src = photo;
}

applyExportParameters();

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
