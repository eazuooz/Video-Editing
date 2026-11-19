async function downloadRoomData() {
  const parts = LOFI_BUILD.dataParts;
  const total = parts.reduce((sum, part) => sum + part.bytes, 0);
  let loaded = 0;
  const blobs = await Promise.all(parts.map(async ({url, bytes}) => {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Could not download ${url}: ${response.status}`);
    const blob = await response.blob();
    if (blob.size !== bytes) throw new Error(`Incomplete game data: ${url}`);
    loaded += blob.size;
    $('#progress').value = 0.65 * loaded / total;
    $('#loading').textContent = '게임 데이터 받는 중 · ' + Math.floor(100 * loaded / total) + '%';
    return blob;
  }));
  const compressed = new Blob(blobs, {type: 'application/octet-stream'});
  return URL.createObjectURL(compressed);
}

function showLoadFailure(message) {
  $('#loading').textContent = message;
  $('#retry').hidden = false;
}

const script = document.createElement('script');
script.src = LOFI_BUILD.loader;
script.onload = async () => {
  let dataUrl;
  try {
    dataUrl = await downloadRoomData();
    resize();
    unity = await createUnityInstance($('#unity-canvas'), {
      ...LOFI_BUILD.config,
      dataUrl,
      devicePixelRatio: 1,
      cacheControl: url => url === dataUrl ? 'no-store' : 'must-revalidate',
      showBanner: (_message, type) => {
        if (type === 'error') showLoadFailure('불러오기에 실패했어요. 다시 시도해 주세요.');
      },
    }, progress => {
      $('#progress').value = 0.65 + 0.35 * progress;
      $('#loading').textContent = '방 준비 중 · ' + Math.round(progress * 100) + '%';
    });
    $('#loading').textContent = '방이 준비됐어요.';
    $('#enter').textContent = '음악과 함께 들어가기';
    $('#enter').disabled = false;
  } catch (error) {
    showLoadFailure('방을 불러오지 못했어요. 다시 시도해 주세요.');
    console.error(error);
  } finally {
    if (dataUrl) URL.revokeObjectURL(dataUrl);
  }
};
script.onerror = () => showLoadFailure('게임 파일을 받지 못했어요. 다시 시도해 주세요.');
document.body.appendChild(script);
