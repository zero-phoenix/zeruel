// Manual local review only. Never call from an observer or send the result to runtime/storage.
let busy = false;
let library;
async function loadLibrary() {
  if (globalThis.Tesseract) return globalThis.Tesseract;
  library ||= new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = chrome.runtime.getURL('vendor/tesseract.min.js');
    script.onload = () => resolve(globalThis.Tesseract);
    script.onerror = () => { library = undefined; reject(new Error('Faltan los archivos OCR locales. Ejecuta tools/prepare_local_ocr.py.')); };
    document.head.append(script);
  });
  return library;
}
export async function extractLocalImage(file, {onProgress = () => {}} = {}) {
  if (busy) throw new Error('Solo se procesa una imagen a la vez.');
  if (!(file instanceof Blob) || !['image/png', 'image/jpeg', 'image/webp'].includes(file.type) || file.size > 8 * 1024 * 1024) {
    throw new Error('Selecciona PNG, JPEG o WebP de hasta 8 MB.');
  }
  busy = true;
  let worker;
  let bitmap;
  try {
    bitmap = await createImageBitmap(file);
    if (bitmap.width * bitmap.height > 4000000) throw new Error('La imagen excede 4 megapíxeles; recorta localmente antes de procesar.');
    const api = await loadLibrary();
    if (!api?.createWorker) throw new Error('Motor OCR local no disponible.');
    const base = chrome.runtime.getURL('vendor/');
    worker = await api.createWorker('spa', 1, {
      workerPath: `${base}worker.min.js`, workerBlobURL: false,
      corePath: `${base}tesseract-core-lstm.wasm.js`, langPath: base,
      gzip: false, cacheMethod: 'none',
      logger: event => { if (typeof event.progress === 'number') onProgress(Math.max(0, Math.min(1, event.progress))); },
      errorHandler: () => {},
    });
    const result = await worker.recognize(file);
    if (typeof result?.data?.text !== 'string') throw new Error('No se pudo extraer texto.');
    // Recognition is a proposal, including handwriting. Confidence never authorizes export.
    return {text: result.data.text, confidence: Number(result.data.confidence) || 0};
  } finally {
    bitmap?.close();
    try { await worker?.terminate(); } finally { busy = false; }
  }
}
