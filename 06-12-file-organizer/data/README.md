# 연습용 샘플 폴더

`sample-downloads/` 는 어질러진 내려받기 폴더를 흉내 낸 **가상의 빈 파일 모음**입니다. 모든 파일의 내용은 한 줄짜리 안내문이며, 실제 사진·문서가 아닙니다.

일부러 까다로운 경우를 섞어 두었습니다.

| 파일 | 확인할 것 |
| :--- | :--- |
| `보고서.pdf` 와 `문서/보고서.pdf` | 이름 충돌 — 덮어쓰지 않고 제자리에 둡니다 |
| `회의록` | 확장자 없음 — `_확장자없음/` |
| `환경설정.conf`, `드라마자막.srt` | 목록에 없는 확장자 — `_기타/` |
| `DSC_0042.JPG` | 파일 이름에 날짜가 없음 — `--by date` 에서 수정 시각을 씁니다 |
| `IMG_20260312_101500.jpg`, `2026-04-02 가족사진.png` | 파일 이름의 날짜가 우선입니다 |
| `문서/` | 하위 폴더 — 건드리지 않습니다 |
| `.download-history` | 숨김 파일 — 건드리지 않습니다 |

시험해 볼 때는 **이 폴더를 다른 곳으로 복사한 뒤** 복사본에 대고 실행하세요. `sample-downloads/` 자체를 정리하면 샘플이 흐트러집니다.

```
cp -r data/sample-downloads /tmp/연습
python scripts/organize_files.py /tmp/연습
python scripts/organize_files.py /tmp/연습 --apply --log /tmp/이동로그.csv
python scripts/organize_files.py --undo /tmp/이동로그.csv
```

`--by date` 로 `_날짜모름/` 이 나오는 것을 보려면 파일의 수정 시각을 지워야 합니다. git 은 수정 시각을 보관하지 않으므로 내려받은 직후에는 모든 파일이 같은 달로 묶입니다.

```
python -c "import os; os.utime('/tmp/연습/DSC_0042.JPG', (0, 0))"
```
