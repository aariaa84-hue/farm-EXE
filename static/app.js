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

function showError(error) {
  const message = error instanceof Error ? error.message : String(error);
  alert(`처리 중 문제가 생겼습니다.\n${message}`);
}

function renderScript(data) {
  state.title = data.title || "";
  state.scenes = data.scenes || [];
  $("title").value = state.title;
  $("scriptPreview").value = [
    `Hook: ${data.hook || ""}`,
    "",
    ...state.scenes.map(s => `Scene ${s.no}\n나레이션: ${s.narration}\n시각화: ${s.visual}\n`),
    `CTA: ${data.cta || ""}`,
    data.note ? `\nNote: ${data.note}` : ""
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
  const settings = await res.json();
  $("elevenlabsApiKey").value = settings.elevenlabs_api_key || "";
  await refreshTtsStatus();
}

async function refreshTtsStatus() {
  const res = await fetch("/api/tts/status");
  const status = await res.json();
  $("ttsStatus").textContent = status.message || "";
  $("ttsBtn").disabled = !status.enabled;
}

$("generateScript").onclick = async () => {
  try {
    state.topic = $("topic").value.trim();
    state.genre = $("genre").value;
    state.duration_sec = Number($("duration").value || 60);
    const data = await api("/api/script", state);
    renderScript(data);
  } catch (error) {
    showError(error);
  }
};

$("generatePrompts").onclick = async () => {
  try {
    const data = await api("/api/prompts", {
      scenes: state.scenes,
      style: $("style").value,
      ratio: $("ratio").value
    });
    renderPrompts(data.visual_prompts || []);
  } catch (error) {
    showError(error);
  }
};

$("generateMeta").onclick = async () => {
  try {
    const data = await api("/api/metadata", {
      title: $("title").value,
      topic: $("topic").value,
      scenes: state.scenes
    });
    renderMetadata(data);
  } catch (error) {
    showError(error);
  }
};

$("saveBtn").onclick = async () => {
  try {
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
  } catch (error) {
    showError(error);
  }
};

$("exportMd").onclick = async () => {
  try {
    const res = await api("/api/export/markdown", {
      topic: $("topic").value,
      genre: $("genre").value,
      title: $("title").value,
      scenes: state.scenes,
      visual_prompts: state.visual_prompts,
      metadata: state.metadata
    });
    alert(`내보내기 완료: ${res.path}`);
  } catch (error) {
    showError(error);
  }
};

$("exportSrt").onclick = async () => {
  try {
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
  } catch (error) {
    showError(error);
  }
};

$("ttsBtn").onclick = async () => {
  try {
    const res = await api("/api/tts", {
      title: $("title").value,
      scenes: state.scenes
    });
    alert(res.message);
  } catch (error) {
    showError(error);
  }
};

$("saveSettings").onclick = async () => {
  try {
    await api("/api/settings", {
      elevenlabs_api_key: $("elevenlabsApiKey").value
    });
    alert("설정을 저장했습니다.");
    await loadSettings();
  } catch (error) {
    showError(error);
  }
};

loadSettings();
