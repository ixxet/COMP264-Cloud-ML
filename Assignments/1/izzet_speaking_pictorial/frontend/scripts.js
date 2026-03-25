"use strict";

const serverUrl = "http://127.0.0.1:8000";
const statusEl = document.getElementById("status");
const translatedEl = document.getElementById("translated");
const playerEl = document.getElementById("player");
const imageEl = document.getElementById("image");

document.getElementById("runBtn").addEventListener("click", uploadTranslateSpeak);

async function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(String(reader.result).replace(/^data:(.*,)?/, ""));
    reader.onerror = reject;
  });
}

async function uploadTranslateSpeak() {
  const file = document.getElementById("file").files[0];
  if (!file) {
    alert("Select an image first.");
    return;
  }

  statusEl.textContent = "Uploading image...";
  translatedEl.textContent = "";
  playerEl.src = "";

  const filebytes = await fileToBase64(file);

  const uploadRes = await fetch(`${serverUrl}/images`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ filename: file.name, filebytes }),
  });
  const uploadData = await uploadRes.json();
  imageEl.src = uploadData.fileUrl;

  statusEl.textContent = "Translating and synthesizing speech...";
  const speakRes = await fetch(`${serverUrl}/images/${uploadData.fileId}/speak-text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fromLang: "auto", toLang: "en", voiceId: "Joanna" }),
  });
  const speakData = await speakRes.json();

  translatedEl.textContent = speakData.translatedText || "(No text detected)";
  if (speakData.audioFileUrl) {
    playerEl.src = speakData.audioFileUrl;
  }
  statusEl.textContent = "Done";
}
