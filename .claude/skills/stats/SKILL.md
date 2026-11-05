---
name: stats
description: 홈리빙클럽 릴스 성과를 Meta Business Suite 에서 읽어 reels/stats.csv 에 누적하고 짧게 분석해요. 사용자가 /stats 를 입력했을 때만 실행해요.
disable-model-invocation: true
---

# 릴스 성과 기록

1. Claude in Chrome 으로 https://business.facebook.com/latest/insights/content 를 열어요 (로그인은 사용자 몫).
2. JS 로 `[role=row]` 의 셀을 읽어 릴스별 조회수, 좋아요, 저장, 팔로우, "동영상 평균 재생 시간"을 가져와요.
   - Business Suite 평균 재생은 앱보다 약 1초 높게 나와요. 같은 출처끼리만 비교해요.
3. `reels/stats.csv` 에 행을 추가하거나 같은 num 의 값을 최신으로 갱신해요 (UTF-8, 헤더 유지).
   - ig_code 는 캡션/메모리의 릴스 코드, length_s 는 영상 길이.
4. 보고: 최신 릴스 vs 직전 3개 평균(조회, 평균 재생), 형식별 비교, 한 줄 결론.
   - 판단 기준: 새 형식(한 장면 연속, reels/shower 이후)이 평균 재생 2초를 넘는지.
5. 진행정리 md(`C:/path/to/file`)가 있으면 성과 표도 맞춰 고쳐요.
