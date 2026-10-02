const {spawnSync} = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const python = path.join(root, 'qwen3-tts', '.venv', 'Scripts', 'python.exe');
const channelId = 'UCOgtkPoyC0VXhCs7Xk3jvjQ';
const excludedPlaylistIds = new Set([
  'PLUU7_j2ihric', // 게임 디자인 · Planning & Game Design & Tech (사용자 추가 제외)
  'PLWKwcHKTXy5RSvmpWyWAG9kWMEqI2AYjn', // C++ 기초 문법
  'PLWKwcHKTXy5QXZEw5dJ6ubggsBhLtTsBa', // C++ 자료구조 및 기초 알고리즘
]);

const playlists = [
  ['PLUU7_j2ihric', 'Planning & Game Design & Tech', 'public'],
  ['PLGhSWT5jo2TE', '제작할 영상 컨텐츠', 'private'],
  ['PLWKwcHKTXy5T9P4uAQGAe5vsSzx-G2ihN', '어려운 컴퓨터 그래픽스를 쉽게 설명해주는 논문 리뷰', 'public'],
  ['PLWKwcHKTXy5SKMSjoO1c7kdk5oK55M_8o', '도움이 되는 게임 개발 이야기', 'public'],
  ['PLWKwcHKTXy5Tw0Yk7arNvsJSr2pJqTRxS', 'Raytracing on the weekends (레이트레이싱 한주 만에 끝내기) with CUDA(쿠다)', 'public'],
  ['PLWKwcHKTXy5RhB8b42CjnfFL-4uRvHDyU', 'Physically Based Rendering (PBR) 물리 기반 렌더링', 'public'],
  ['PLWKwcHKTXy5QEySaSo3JWoQXG9mk1DgVV', '프로그래밍 잡담 및 고민 상담', 'public'],
  ['PLWKwcHKTXy5SJsZ3HD3TAkDv_ollFeSnL', 'Directx12 강의 (그래픽스, 자체엔진) PART2', 'public'],
  ['PLWKwcHKTXy5Soue4YKXa-dsXMV71BVGRk', '게임 수학(Game Math) PART 2', 'public'],
  ['PLWKwcHKTXy5Su5ZimPTNsZYRAsHrW290R', '포트폴리오', 'public'],
  ['PLWKwcHKTXy5SVKTzTpgiZLcuCJkiMxcbb', '게임 프로그래밍 팁', 'public'],
  ['PLWKwcHKTXy5QnZCqnrARipotYlkLU4m5-', '언리얼 엔진5 게임 개발 강의', 'public'],
  ['PLWKwcHKTXy5T5v_qSsvUnjFZG85pDOZPq', 'Directx 11 강의 ( 그래픽스, 자체엔진 강의 ) - PART1', 'public'],
  ['PLWKwcHKTXy5Rm2vE8gUmQnEdxoX-r4KTT', '얌얌이', 'public'],
  ['PLWKwcHKTXy5RSvmpWyWAG9kWMEqI2AYjn', 'C++ 기초 문법', 'public'],
  ['PLWKwcHKTXy5QPd_uY3tNxm7hJi830d-g-', '수업 결과물', 'public'],
  ['PLWKwcHKTXy5RvBWvlUn72WZWKs8hLrnTz', 'WindowsAPI 자체엔진 제작 ( 리뷰 강의 - 유니티 클론코딩 ))', 'public'],
  ['PLWKwcHKTXy5RK3F26-HPTtbSXEnMguTFs', '게임 수학 (Part1)', 'public'],
  ['PLWKwcHKTXy5SDbr6YuHIXpXeoybLCwX1e', 'C++ 고급 알고리즘/자료구조', 'public'],
  ['PLWKwcHKTXy5SaeuiYkJdc8juhwHKK2q-5', '게임 프로그래밍 패턴(디자인 패턴)', 'public'],
  ['PLWKwcHKTXy5R3EqAZuOyGkB1JSRwwj7zF', '게임 프로그래머 취업 준비', 'public'],
  ['PLWKwcHKTXy5RSkINElI7wZOwn9z4RcJff', 'C++을 활용해 유니티처럼 엔진 만들기( 자체 게임 엔진 제작 강의 )', 'public'],
  ['PLWKwcHKTXy5Smp6yIxm0i_krwYVvQJ4Ze', 'Solved.ac, Leet code 알고리즘 문제풀이', 'public'],
  ['PLWKwcHKTXy5SUZZ04yUYx_2yO3mkxDzR1', '게임 엔진 제작 강의 (라이브 코딩)', 'public'],
  ['PLWKwcHKTXy5QXZEw5dJ6ubggsBhLtTsBa', 'C++ 자료구조 및 기초 알고리즘', 'public'],
];

const uploadsResult = spawnSync(
  python,
  [
    '-X', 'utf8', '-m', 'yt_dlp', '--flat-playlist', '--dump-single-json', '--no-warnings',
    '--extractor-args', 'youtube:lang=ko', `https://www.youtube.com/channel/${channelId}/videos`,
  ],
  {cwd: root, encoding: 'utf8', windowsHide: true, maxBuffer: 64 * 1024 * 1024},
);
if (uploadsResult.status !== 0) {
  throw new Error(`Failed to read channel uploads: ${(uploadsResult.stderr || uploadsResult.stdout).trim()}`);
}
const uploadEntries = JSON.parse(uploadsResult.stdout).entries || [];
const channelUploadIds = new Set(uploadEntries.map((entry) => entry?.id).filter(Boolean));

const inventory = new Map();
const playlistResults = [];

for (const [id, title, visibility] of playlists) {
  if (visibility === 'private') {
    playlistResults.push({id, title, visibility, skipped: true, reason: 'private planning/reference playlist'});
    continue;
  }
  const result = spawnSync(
    python,
    [
      '-X', 'utf8', '-m', 'yt_dlp', '--flat-playlist', '--dump-single-json', '--no-warnings',
      '--extractor-args', 'youtube:lang=ko', `https://www.youtube.com/playlist?list=${id}`,
    ],
    {cwd: root, encoding: 'utf8', windowsHide: true, maxBuffer: 64 * 1024 * 1024},
  );
  if (result.status !== 0) {
    playlistResults.push({id, title, visibility, error: (result.stderr || result.stdout).trim()});
    continue;
  }
  const data = JSON.parse(result.stdout);
  const entries = data.entries || [];
  playlistResults.push({id, title, visibility, excluded: excludedPlaylistIds.has(id), entryCount: entries.length});
  for (const [entryIndex, entry] of entries.entries()) {
    if (!entry?.id) continue;
    const video = inventory.get(entry.id) || {
      id: entry.id,
      title: entry.title || '',
      channelId: entry.channel_id || '',
      uploader: entry.uploader || '',
      url: `https://www.youtube.com/watch?v=${entry.id}`,
      playlists: [],
    };
    video.playlists.push({id, title, excluded: excludedPlaylistIds.has(id), position: entryIndex + 1});
    if (!video.title && entry.title) video.title = entry.title;
    if (!video.channelId && entry.channel_id) video.channelId = entry.channel_id;
    if (!video.uploader && entry.uploader) video.uploader = entry.uploader;
    inventory.set(entry.id, video);
  }
}

const videos = [...inventory.values()].map((video) => {
  const ownedByChannel = video.channelId === channelId || channelUploadIds.has(video.id);
  const inExcludedPlaylist = video.playlists.some((playlist) => playlist.excluded);
  const inIncludedPlaylist = video.playlists.some((playlist) => !playlist.excluded);
  return {
    ...video,
    ownedByChannel,
    inExcludedPlaylist,
    target: ownedByChannel && inIncludedPlaylist && !inExcludedPlaylist,
  };
}).sort((a, b) => a.title.localeCompare(b.title, 'ko'));

const report = {
  generatedAt: new Date().toISOString(),
  channelId,
  policy: {
    include: 'channel-owned videos in at least one public non-excluded playlist',
    exclude: [...excludedPlaylistIds],
    overlap: 'exclude a video if it appears in any excluded playlist, even when it also appears elsewhere',
    privatePlanningPlaylist: 'not a target source',
  },
  counts: {
    playlists: playlists.length,
    publicPlaylistsRead: playlistResults.filter((playlist) => !playlist.skipped && !playlist.error).length,
    publicChannelUploadsRead: channelUploadIds.size,
    uniquePlaylistVideos: videos.length,
    uniqueChannelOwnedVideos: videos.filter((video) => video.ownedByChannel).length,
    targetVideos: videos.filter((video) => video.target).length,
    excludedByPlaylistMembership: videos.filter((video) => video.ownedByChannel && video.inExcludedPlaylist).length,
    externalOrUnknownOwner: videos.filter((video) => !video.ownedByChannel).length,
  },
  playlists: playlistResults,
  videos,
};

const outputDir = path.join(root, 'output', 'youtube-library-refresh');
fs.mkdirSync(outputDir, {recursive: true});
const outputPath = path.join(outputDir, 'inventory.json');
fs.writeFileSync(outputPath, `${JSON.stringify(report, null, 2)}\n`, 'utf8');
console.log(JSON.stringify({outputPath, counts: report.counts}, null, 2));
