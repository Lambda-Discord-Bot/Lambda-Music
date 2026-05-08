# Lambda Music Bot

`discord.py` 기반의 음악 봇입니다.

## 실행 방법
1. Python 설치
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
