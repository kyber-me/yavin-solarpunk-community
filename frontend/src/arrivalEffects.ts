import type { RefObject } from 'react';

// One transparent frame is shared by the scene, magnifier and 3D eyepiece.
export type AmbientSource = { canvas: RefObject<HTMLCanvasElement | null>; listeners: Set<() => void> };

const pond = new Path2D('M340 721 C412 699 524 692 601 681 C651 673 697 659 731 655 L739 701 C729 721 712 736 690 742 C667 751 659 771 653 794 C640 815 615 825 595 817 C553 813 508 801 472 804 C429 806 391 798 356 791 L328 766 Z');
const cascade = new Path2D('M729 693 Q746 689 764 695 L763 750 Q756 756 728 753 Z');
const roof = new Path2D([
  'M1210 483 L1289 449 L1298 448 L1235 484 Z',
  'M1241 484 L1304 448 L1318 447 L1282 484 Z',
  'M1288 484 L1323 447 L1339 447 L1318 484 Z',
  'M1325 484 L1342 447 L1353 447 L1359 484 Z',
  'M1365 484 L1358 447 L1371 448 L1404 484 Z',
  'M1410 484 L1376 448 L1393 449 L1448 484 Z',
  'M1455 484 L1399 450 L1403 450 L1486 484 Z',
  'M1178 500 L1217 497 L1195 513 L1155 513 Z',
  'M1223 497 L1257 497 L1242 513 L1202 513 Z',
  'M1263 497 L1293 497 L1284 513 L1249 513 Z',
  'M1300 497 L1330 497 L1327 513 L1291 513 Z',
  'M1337 497 L1366 497 L1370 513 L1334 513 Z',
  'M1373 497 L1404 497 L1415 513 L1377 513 Z',
  'M1411 497 L1441 497 L1462 513 L1422 513 Z',
  'M1448 497 L1485 497 L1525 513 L1469 513 Z',
].join(' '));

function wave(time: number, period: number) { return (1 - Math.cos(time * Math.PI * 2 / period)) / 2; }

export function paintArrivalEffects(canvas: HTMLCanvasElement, time: number) {
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  ctx.setTransform(canvas.width / 2048, 0, 0, canvas.height / 1152, 0, 0);
  ctx.clearRect(0, 0, 2048, 1152);

  ctx.save();
  ctx.translate(1232 + wave(time, 48000) * 56, 550);
  ctx.scale(750, 460);
  const sun = ctx.createRadialGradient(0, 0, 0, 0, 0, 1);
  sun.addColorStop(0, 'rgba(255,242,181,.75)');
  sun.addColorStop(.52, 'rgba(248,219,143,.32)');
  sun.addColorStop(1, 'rgba(248,219,143,0)');
  ctx.globalAlpha = .02 + wave(time, 48000) * .07;
  ctx.fillStyle = sun;
  ctx.fillRect(-1, -1, 2, 2);
  ctx.restore();

  ctx.save();
  ctx.clip(pond);
  ctx.lineCap = 'round';
  ctx.filter = 'blur(1.4px)';
  const lines = [
    [375,729,418],[490,714,530],[575,695,605],[455,751,492],[550,738,599],
    [633,723,669],[395,772,434],[515,786,557],[602,773,639],[434,721,460],
    [545,706,578],[627,690,659],[375,749,407],[508,731,541],[595,751,632],
    [446,782,480],[558,800,590],[636,758,668],
  ];
  lines.forEach(([x, y, end], index) => {
    const phase = index < 9 ? wave(time, 10000) : 1 - wave(time, 13000);
    const move = (phase - .5) * 8;
    const glow = ctx.createLinearGradient(x + move, y, end + move, y);
    glow.addColorStop(0, 'rgba(255,244,194,0)');
    glow.addColorStop(.5, 'rgba(255,240,173,.75)');
    glow.addColorStop(1, 'rgba(255,244,194,0)');
    ctx.strokeStyle = glow;
    ctx.globalAlpha = .14 + phase * .65;
    ctx.lineWidth = index < 9 ? 4 : 3.5;
    ctx.beginPath();
    ctx.moveTo(x + move, y);
    ctx.quadraticCurveTo((x + end) / 2 + move, y - 2, end + move, y - 1);
    ctx.stroke();
  });
  ctx.restore();

  ctx.save();
  ctx.clip(cascade);
  const offset = (time % 2800) / 2800 * 52 - 26;
  ctx.translate(0, offset);
  [685, 737].forEach(y => {
    const fall = ctx.createLinearGradient(0, y, 0, y + 24);
    fall.addColorStop(0, 'rgba(233,243,215,0)');
    fall.addColorStop(.5, 'rgba(236,244,216,.55)');
    fall.addColorStop(1, 'rgba(233,243,215,0)');
    ctx.fillStyle = fall;
    ctx.fillRect(730, y, 31, 24);
  });
  ctx.restore();

  // Soft, angled glints are confined to the separate glass panes.
  ctx.save();
  ctx.clip(roof);
  const pass = (time % 11000) / 11000;
  const position = 1160 + pass * 410;
  const intensity = Math.sin(Math.PI * pass) ** 2;
  const glass = ctx.createLinearGradient(position - 60, 0, position + 60, 0);
  glass.addColorStop(0, 'rgba(255,239,190,0)');
  glass.addColorStop(.35, 'rgba(255,238,187,.12)');
  glass.addColorStop(.5, 'rgba(255,252,223,.72)');
  glass.addColorStop(.65, 'rgba(255,238,187,.12)');
  glass.addColorStop(1, 'rgba(255,239,190,0)');
  ctx.globalAlpha = intensity * .8;
  ctx.fillStyle = glass;
  ctx.fillRect(1120, 440, 440, 80);
  ctx.restore();
}
