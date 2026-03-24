import puppeteer from 'puppeteer';

const SLIDES = [
  {
    name: '01_cover',
    html: `<div style="
      width:1080px; height:1080px;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      display:flex; flex-direction:column; justify-content:center; align-items:center;
      text-align:center; padding:80px; font-family:'Pretendard',sans-serif;
    ">
      <div style="background:#e94560; color:#fff; font-size:28px; font-weight:700;
        padding:12px 32px; border-radius:40px; margin-bottom:48px; letter-spacing:2px;">
        WORK FROM HOME</div>
      <div style="color:#fff; font-size:72px; font-weight:800; line-height:1.3; margin-bottom:32px;">
        집에서 일하는데<br>왜 더 바쁠까?</div>
      <div style="color:rgba(255,255,255,0.7); font-size:32px; font-weight:400; line-height:1.6;">
        재택근무 생산성을 2배로 올리는<br>5가지 검증된 방법</div>
    </div>`
  },
  ...['공간을 분리하세요|침대에서 노트북 펴지 마세요.<br><br><b>전용 작업 공간</b>이 있는 사람은<br>생산성이 <b>32% 더 높습니다.</b><br><br>작은 책상 하나라도 괜찮아요.',
    '출근 루틴을 만드세요|잠옷 차림으로 일 시작하면<br>뇌가 <b>"아직 쉬는 시간"</b>이라 인식합니다.<br><br>옷 갈아입기, 커피 한 잔, 10분 산책.<br><b>작은 루틴이 스위치를 켭니다.</b>',
    '시간을 블록으로 나누세요|<b>90분 집중 + 15분 휴식</b><br>이 사이클이 가장 효과적입니다.<br><br>타이머를 설정하고,<br>휴식 시간엔 반드시 <b>화면에서 눈을 떼세요.</b>',
    '알림을 꺼두세요|슬랙, 이메일, 카톡 알림은<br>집중력의 <b>최대 적</b>입니다.<br><br><b>오전/오후 각 1회</b> 확인 시간을 정하고<br>나머지 시간은 알림을 끄세요.',
    '퇴근 시간을 지키세요|재택근무의 가장 큰 함정은<br><b>"항상 일하는 상태"</b>입니다.<br><br>정해진 시간에 노트북을 닫고<br><b>작업 공간을 떠나세요.</b>'
  ].map((content, i) => {
    const [title, body] = content.split('|');
    const num = i + 1;
    const color = num % 2 === 1 ? '#e94560' : '#0f3460';
    return {
      name: `${String(i + 2).padStart(2, '0')}_body`,
      html: `<div style="
        width:1080px; height:1080px; position:relative;
        background:#fff; font-family:'Pretendard',sans-serif;
      ">
        <div style="height:8px; background:${color};"></div>
        <div style="position:absolute; top:56px; left:72px; width:80px; height:80px; border-radius:50%;
          background:${color}; display:flex; align-items:center; justify-content:center;
          font-size:36px; font-weight:800; color:#fff;">${num}</div>
        <div style="padding:56px 72px; padding-top:68px; display:flex; flex-direction:column; justify-content:center; height:calc(100% - 8px);">
          <div style="font-size:52px; font-weight:800; line-height:1.4; margin-bottom:40px;
            margin-left:100px; color:#1a1a2e;">${title}</div>
          <div style="font-size:34px; font-weight:400; line-height:1.8; color:#444;
            margin-left:100px; padding-right:40px;">${body}</div>
        </div>
        <div style="position:absolute; bottom:56px; left:72px; right:72px; height:1px; background:#e0e0e0;"></div>
        <div style="position:absolute; bottom:24px; right:72px; font-size:24px; color:#bbb;">${i + 2} / 7</div>
      </div>`
    };
  }),
  {
    name: '07_closing',
    html: `<div style="
      width:1080px; height:1080px;
      background: linear-gradient(135deg, #0f3460 0%, #1a1a2e 100%);
      display:flex; flex-direction:column; justify-content:center; align-items:center;
      text-align:center; padding:80px; font-family:'Pretendard',sans-serif;
    ">
      <div style="color:#fff; font-size:60px; font-weight:800; line-height:1.4; margin-bottom:48px;">
        오늘부터<br>하나만 시작하세요</div>
      <div style="color:rgba(255,255,255,0.6); font-size:30px; font-weight:400; line-height:1.6; margin-bottom:64px;">
        5가지 중 가장 쉬운 것 하나.<br>작은 변화가 큰 차이를 만듭니다.</div>
      <div style="background:#e94560; color:#fff; font-size:32px; font-weight:700;
        padding:24px 64px; border-radius:60px;">저장하고 실천하기</div>
    </div>`
  }
];

async function capture() {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewport({ width: 1080, height: 1080, deviceScaleFactor: 2 });

  // Load font once
  const fontPage = `<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css">
    <style>*{margin:0;padding:0;box-sizing:border-box;} b{font-weight:700;color:#1a1a2e;}</style>
    </head><body><p style="font-family:Pretendard">Loading fonts 가나다라마바사</p></body></html>`;

  await page.setContent(fontPage, { waitUntil: 'networkidle2', timeout: 60000 });
  await page.evaluateHandle('document.fonts.ready');
  console.log('Fonts loaded.');

  for (const slide of SLIDES) {
    // Inject slide HTML without reloading stylesheets
    await page.evaluate((html) => {
      document.body.innerHTML = html;
    }, slide.html);
    await new Promise(r => setTimeout(r, 300));

    await page.screenshot({
      path: `${slide.name}.png`,
      type: 'png',
      clip: { x: 0, y: 0, width: 1080, height: 1080 },
    });
    console.log(`Captured: ${slide.name}.png`);
  }

  await browser.close();
  console.log('\nDone! 7 card news images (2160x2160px @2x)');
}

capture().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
