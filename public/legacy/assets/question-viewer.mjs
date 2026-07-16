import { getDocument, GlobalWorkerOptions } from "./pdf.min.mjs";

GlobalWorkerOptions.workerSrc = "/legacy/assets/pdf.worker.min.mjs";

const metadataPromise = fetch("/legacy/api/question-regions.json").then((response) => {
  if (!response.ok) throw new Error("Metadados das questões indisponíveis.");
  return response.json();
});

const pdfPromise = getDocument({
  url: "/legacy/assets/naturezas-ppl.pdf",
  rangeChunkSize: 262144,
  disableAutoFetch: true,
}).promise;

let renderVersion = 0;

async function renderQuestion(number) {
  const version = ++renderVersion;
  const root = document.querySelector("#question-document");
  if (!root) return;

  root.classList.remove("is-ready", "has-error");
  root.setAttribute("aria-busy", "true");

  try {
    const [metadata, pdf] = await Promise.all([metadataPromise, pdfPromise]);
    const region = metadata.questions[String(number)];
    if (!region) throw new Error("Recorte da questão não encontrado.");

    const page = await pdf.getPage(region.page);
    const [x, y, width, height] = region.rect;
    root.classList.toggle("full-width-source", width > 400);
    const availableWidth = Math.max(320, root.clientWidth - 2);
    const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
    const scale = Math.min(6, Math.max(2.5, availableWidth / width) * pixelRatio);
    const viewport = page.getViewport({ scale });

    const canvas = root.querySelector("canvas");
    const context = canvas.getContext("2d", { alpha: false });
    canvas.width = Math.ceil(width * scale);
    canvas.height = Math.ceil(height * scale);
    canvas.style.aspectRatio = `${width} / ${height}`;

    context.save();
    context.fillStyle = "#ffffff";
    context.fillRect(0, 0, canvas.width, canvas.height);
    context.restore();

    await page.render({
      canvasContext: context,
      viewport,
      transform: [1, 0, 0, 1, -x * scale, -y * scale],
    }).promise;

    if (version !== renderVersion) return;
    root.classList.add("is-ready");
    root.setAttribute("aria-busy", "false");
  } catch (error) {
    console.error(error);
    root.classList.add("has-error");
    root.setAttribute("aria-busy", "false");
    const message = root.querySelector(".question-loading");
    if (message) message.textContent = "A página original desta questão não pôde ser carregada.";
  }
}

document.addEventListener("enem:question-ready", (event) => {
  renderQuestion(event.detail.number);
});

const initial = document.querySelector("#question-document");
if (initial?.dataset.question) renderQuestion(Number(initial.dataset.question));
