import sys
import json

def main():
    if len(sys.argv) < 2:
        print("Usage: python search_market.py <keyword>")
        sys.exit(1)
    
    keyword = sys.argv[1]
    # 실제 환경에서는 검색 API(예: SerpApi, Bing Search API)를 호출합니다.
    # 여기서는 사이드카 스크립트 연동을 보여주기 위한 모의 데이터를 반환합니다.
    results = {
        "keyword": keyword,
        "market_trend": f"{keyword} 시장은 최근 생성형 AI 기술 도입으로 업무 효율화 및 자동화 수요가 증가하며 급격히 성장 중입니다.",
        "competitors": [
            {"name": "A사", "activity": "최근 100억 투자 유치 및 신규 클라우드 솔루션 출시"},
            {"name": "B사", "activity": "아시아 태평양 지역으로의 글로벌 시장 진출 선언"}
        ],
        "sources": [
            "https://example.com/news/1",
            "https://example.com/news/2"
        ]
    }
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
