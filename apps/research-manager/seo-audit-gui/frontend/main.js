const runSingle = document.getElementById("runSingle");
const runBatch = document.getElementById("runBatch");
const payload = document.getElementById("payload");
const batchPayload = document.getElementById("batchPayload");
const out = document.getElementById("out");

function setExampleSingle() {
  payload.value = JSON.stringify(
    {
      pagePath: "D:/GitHub/faiththruphysics-site-data/one-page-stories/truth-and-pushback/testing-the-unmeasurable/index.md",
      canonicalUrl: "https://faiththruphysics.com/one-page-stories/truth-and-pushback/testing-the-unmeasurable",
      series: "Truth and Pushback",
      pageTitle: "Testing the Unmeasurable",
      schemaType: "Article",
      media: [
        { type: "video", kind: "Explainer" },
        { type: "audio", kind: "Debate" }
      ]
    },
    null,
    2
  );
}

function setExampleBatch() {
  batchPayload.value = JSON.stringify(
    [
      {
        pagePath: "D:/GitHub/faiththruphysics-site-data/one-page-stories/truth-and-pushback/testing-the-unmeasurable/index.md",
        series: "Truth and Pushback",
        pageTitle: "Testing the Unmeasurable",
        schemaType: "Article"
      },
      {
        pagePath: "D:/GitHub/faiththruphysics-site-data/one-page-stories/truth-and-pushback/repair-and-order/index.md",
        series: "Truth and Pushback",
        pageTitle: "Repair and Order",
        schemaType: "Article"
      }
    ],
    null,
    2
  );
}

setExampleSingle();
setExampleBatch();

async function callApi(url, bodyObj) {
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(bodyObj),
  });
  const text = await r.text();
  out.textContent = text;
}

runSingle.addEventListener("click", () => {
  const body = JSON.parse(payload.value || "{}");
  callApi("http://127.0.0.1:8080/api/audit/page", body);
});

runBatch.addEventListener("click", () => {
  const body = JSON.parse(batchPayload.value || "[]");
  callApi("http://127.0.0.1:8080/api/audit/batch", body);
});
