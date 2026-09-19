import csv
import json
import os
import sys

def mock_analyze_sentiment(text):
    """
    텍스트 기반 모의 감성 분석 함수.
    실제 구현 시 OpenAI API 등을 활용하여 분석을 수행합니다.
    """
    if "좋" in text or "만족" in text or "최고" in text:
        return "긍정", ["만족도", "품질"]
    elif "나쁘" in text or "별로" in text or "불만" in text or "최악" in text:
        return "부정", ["불만족", "개선필요"]
    else:
        return "중립", ["일반"]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_file = os.path.join(base_dir, "data", "reviews.csv")
    output_file = os.path.join(base_dir, "report.json")
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} 파일을 찾을 수 없습니다.")
        sys.exit(1)
        
    results = []
    stats = {"긍정": 0, "부정": 0, "중립": 0}
    
    with open(input_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            review = row.get("review", "")
            sentiment, keywords = mock_analyze_sentiment(review)
            stats[sentiment] += 1
            
            results.append({
                "id": row.get("id"),
                "review": review,
                "sentiment": sentiment,
                "keywords": keywords
            })
            
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({"statistics": stats, "details": results}, f, ensure_ascii=False, indent=2)
        
    print(f"분석 완료: 총 {len(results)}건의 리뷰 처리")
    print(f"결과 저장됨: {output_file}")
    for k, v in stats.items():
        print(f" - {k}: {v}건")

if __name__ == "__main__":
    main()
