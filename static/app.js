const state = {
  topic: "",
  genre: "정보형",
  duration_sec: 60,
  title: "",
  scenes: [],
  visual_prompts: [],
  metadata: {},
};

const $ = (id) => document.getElementById(id);

async function api(path, body) {
  const res = await fetch(path, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(body || {})
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function renderScript(data) {
  state.title = data.title || "";
  state.scenes = data.scenes || [];
  $("title").value = state.title;
  $("scriptPreview").value = [
    `Hook: ${data.hook || ""}`,
    "",
    ...state.scenes.map(s => `Scene ${s.no}\n나레이션: ${s.narration}\n시각화: ${s.visual}\n`),
    `CTA: ${data.cta || ""}`
  ].join("\n");
}

function renderPrompts(items) {
  state.visual_prompts = items;
  $("promptPreview").value = items.map(p =>
    `Scene ${p.no}\nPrompt: ${p.prompt}\nNegative: ${p.negative}`
  ).join("\n\n");
}

function renderMetadata(data) {
  state.metadata = data;
  $("metaPreview").value = JSON.stringify(data, null, 2);
}

async function loadSettings() {
  const res = await fetch("/api/settings");
  const s = await res.json();
  $("apiBase").value = s.api_base_url || "";
  $("apiKey").value = s.api_key || "";
  $("model").value = s.model || "";
}

$("generateScript").onclick = async () => {
  state.topic = $("topic").value.trim();
  state.genre = $("genre").value;
  state.duration_sec = Number($("duration").value || 60);
  const data = await api("/api/script", state);
  renderScript(data);
};

$("generatePrompts").onclick = async () => {
  const data = await api("/api/prompts", {
    scenes: state.scenes,
    style: $("style").value,
    ratio: $("ratio").value
  });
  renderPrompts(data.visual_prompts || []);
};

$("generateMeta").onclick = async () => {
  const data = await api("/api/metadata", {
    title: $("title").value,
    topic: $("topic").value,
    scenes: state.scenes
  });
  renderMetadata(data);
};

$("saveBtn").onclick = async () => {
  const payload = {
    topic: $("topic").value,
    genre: $("genre").value,
    duration_sec: Number($("duration").value || 60),
    title: $("title").value,
    scenes: state.scenes,
    visual_prompts: state.visual_prompts,
    metadata: state.metadata
  };
  const res = await api("/api/save", payload);
  alert(`저장 완료: ${res.project._path}`);
};

$("exportMd").onclick = async () => {
  const res = await api("/api/export/markdown", {
    topic: $("topic").value,
    genre: $("genre").value,
    title: $("title").value,
    scenes: state.scenes,
    visual_prompts: state.visual_prompts,
    metadata: state.metadata
  });
  alert(`내보내기 완료: ${res.path}`);
};

$("exportSrt").onclick = async () => {
  const res = await fetch("/api/export/srt", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({ scenes: state.scenes, duration_sec: Number($("duration").value || 60) })
  });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "subtitles.srt";
  a.click();
  URL.revokeObjectURL(url);
};

$("saveSettings").onclick = async () => {
  await api("/api/settings", {
    api_base_url: $("apiBase").value,
    api_key: $("apiKey").value,
    model: $("model").value
  });
  alert("설정을 저장했습니다.");
  loadSettings();
};

loadSettings();
