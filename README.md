# Discord Lambda Music Bot

`discord.py` 기반의 구조화된 음악 봇입니다.

## 핵심 기능
- `/람다음악패널 [채널]`: 지정 채널에 음악 제어 패널 임베드 설치
- 패널 버튼: 재생, 일시정지, 다시재생, 스킵, 정지, 대기열, 반복, 셔플, 나가기
- 재생 버튼은 모달 입력으로 유튜브 링크/검색어를 받아 재생

## 실행 준비
1. Python 3.11+ 설치
2. FFmpeg 설치 후 PATH 등록
3. 프로젝트 폴더에서 아래 실행

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

`.env`의 `DISCORD_TOKEN` 값을 실제 봇 토큰으로 변경하세요.

## 실행
```bash
python main.py
```

## 폴더 구조
```text
Discord Lambda Music Bot/
  main.py
  bot/
    app.py
    config.py
    logging_config.py
    cogs/
      panel_cog.py
    music/
      manager.py
      models.py
      player.py
      queue.py
      ytdl_source.py
    ui/
      embeds.py
      modals.py
      views.py
```
