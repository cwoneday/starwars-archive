# assets — 은하 지도 배경 이미지

`galaxy-map.html` · `galaxy-map-3d.html`은 이 폴더의 **`galaxy.jpg`**를 우주 배경으로 사용합니다.
파일이 없으면 자체 제작 나선팔로 자동 폴백되므로 비워둬도 사이트는 정상 동작합니다.

## NASA 공개 이미지 넣는 법
1. [images.nasa.gov](https://images.nasa.gov)에서 `spiral galaxy` 또는 `Milky Way` 검색
   - 예: Pinwheel Galaxy (M101), Andromeda (M31), 은하수 파노라마
2. 가로로 넓은 고해상도(1920×1080 이상) JPG를 받아 **`assets/galaxy.jpg`**로 저장
3. NASA 이미지는 대부분 퍼블릭 도메인입니다(출처 표기 권장: *Image: NASA*).

> `.png`를 쓰려면 두 HTML의 `src="assets/galaxy.jpg"`를 `.png`로 바꾸세요.
