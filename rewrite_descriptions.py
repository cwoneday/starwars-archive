#!/usr/bin/env python3
"""캐시된 영문 description을 헌법 제6조-A 화법으로 한국어 재구성.

실행 환경: 회원님 로컬 (ANTHROPIC_API_KEY 환경변수 필요, pip install anthropic)
입력:  cache/databank_descriptions/{char_id}.txt
출력:  cache/rewritten_ko/{char_id}.md   ← 자동 머지 금지, 100% 수동 검수 후 반영

검수 기준(제6조): 원문 문장·구문 구조의 복제 흔적이 보이면 폐기 후 재생성.
"""
import os, glob, sys

SYSTEM = """당신은 스타워즈 매니아 아카이브의 기록자다. 영문 공식 소개문이 주어지면,
그 안의 '사실'만 추출해 한국어로 완전히 새로 쓴다. 규칙:
1) 원문 문장·구문 구조를 절대 복제하지 않는다. 사실만 가져오고 화법은 아래를 따른다.
2) 화법: 좌표 먼저(종족/소속/시대), 단정형 종결, 정보 밀도 높게, 2~4문장.
3) 마지막에 가능하면 의의·평가 한 문장(작품 내 위치, 팬덤에서의 인상).
4) 출력은 본문만. 머리말·꼬리말·따옴표 금지."""

def main():
    try:
        import anthropic
    except ImportError:
        sys.exit("pip install anthropic 후 실행하세요.")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY 환경변수를 설정하세요.")
    client = anthropic.Anthropic()
    os.makedirs("cache/rewritten_ko", exist_ok=True)
    files = sorted(glob.glob("cache/databank_descriptions/*.txt"))
    if not files:
        sys.exit("입력 없음 — enrich_characters.py 먼저 실행")
    for path in files:
        cid = os.path.splitext(os.path.basename(path))[0]
        out = f"cache/rewritten_ko/{cid}.md"
        if os.path.exists(out):
            print(f"건너뜀(이미 있음): {cid}")
            continue
        src = open(path, encoding="utf-8").read()
        msg = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=600,
            system=SYSTEM,
            messages=[{"role": "user", "content": f"다음 영문 소개의 사실만으로 재구성:\n\n{src}"}],
        )
        text = msg.content[0].text.strip()
        with open(out, "w", encoding="utf-8") as f:
            f.write(f"<!-- 검수 전 초안 — characters.json 자동 머지 금지 -->\n{text}\n")
        print(f"✓ {cid}")
    print("\n전부 생성됨. cache/rewritten_ko/ 를 검수한 뒤 수동으로 반영하세요.")

if __name__ == "__main__":
    main()
