---
name: analyze-voc-and-reviews
description: "고객 리뷰 데이터의 감성과 주요 키워드를 분석하여 구조화된 리포트로 추출합니다."
author: "AI Agent"
version: "1.0.0"
---

# 고객 리뷰·VOC 감성 분석

이 스킬은 `data/reviews.csv`에 저장된 고객 리뷰를 읽어 감성(긍정/부정/중립)과 핵심 키워드를 추출한 뒤, `report.json`으로 저장합니다.

## 실행 절차

1. `<지시사항>`을 읽고 분석 대상 파일을 확인합니다.
2. `scripts/analyze_voc.py` 스크립트를 실행하여 리뷰 데이터를 구조화합니다.
3. 분석 결과를 요약하여 보고합니다.

<지시사항>
- 분석 대상: `data/reviews.csv`
- 실행 스크립트: `python scripts/analyze_voc.py`
- 스크립트는 입력 파일을 읽어 각 리뷰에 대해 감성 분석 프롬프트를 호출(또는 시뮬레이션)한 뒤, `report.json`에 결과를 저장해야 합니다.
- 스크립트 실행이 완료되면 생성된 `report.json`의 통계를 간략히 출력하세요.
</지시사항>
