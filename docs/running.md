# 실행 안내

2022년 Colab 프로젝트를 읽고 실험할 수 있도록 정리한 공개본입니다. 당시 전체 환경의 버전 고정 파일은 남아 있지 않습니다. 현재 환경에서 원본 가중치 복원을 검증한 버전으로 간주하지 마세요.

## 준비

Colab에서 셀을 위에서 아래로 실행합니다. Python 패키지는 TensorFlow, NumPy, pandas, matplotlib, mido, MIDIUtil입니다. Colab 기본 패키지 외에 필요한 패키지는 설치 셀을 포함했습니다. 오디오 미리듣기는 midi2audio, FluidSynth와 General MIDI 사운드폰트가 추가로 필요합니다.

01과 02는 업로드 창을 사용합니다. 03–05의 BASE 기본값은 `/content/project`입니다.

```text
/content/project/
├── data/
│   ├── midi/                 # 직접 만든 단일 트랙 MIDI
│   └── data_set_64.npy       # 03 출력 → 04 입력
├── checkpoints/
│   ├── ckpt-80.index        # 배포본 기본 번호 예시
│   └── ckpt-80.data-00000-of-00001
└── outputs/                 # 생성 MIDI, 선택적 WAV, 학습 이미지
```

Colab 임시 저장소는 런타임 종료 시 사라질 수 있습니다. 장시간 학습에는 Drive를 마운트한 뒤 BASE를 영구 저장 폴더로 설정하세요.

```python
from google.colab import drive
drive.mount('/content/drive')
# 각 노트북의 BASE를 원하는 Drive 폴더로 변경합니다.
```

## 가중치로 생성만 하기

05에서 같은 체크포인트의 index와 data 파일을 준비하고 번호·경로를 맞춥니다. 기본 ckpt는 80입니다. 복원 후 4마디 MIDI를 다운로드합니다. 생성 셀부터 다시 실행하면 새 소재를 만듭니다. 파일이 없거나 기존 모델 객체의 복원 상태가 일치하지 않으면 중단합니다. 랜덤 초기화 모델을 학습된 모델로 오인하지 않도록 복원 상태를 먼저 확인하세요.

## 데이터부터 학습하기

03 입력 폴더에 직접 만든 MIDI를 넣고 배열을 저장합니다. 04의 경로를 맞추고 GPU 런타임을 선택합니다. 원본 설정값은 20,000 epoch이며 RUN_TRAINING=True로 시작합니다. 원본의 주기 저장은 10,000 epoch 이후부터이고 공개본은 정상 종료 시에도 저장합니다. 짧은 실험은 EPOCHS를 줄여 진행할 수 있습니다.

새로 저장된 체크포인트 번호를 05에 지정합니다. 새 모델이 반드시 ckpt-80일 필요는 없습니다. 데이터와 초기화가 달라지면 결과도 달라집니다. 데이터와 가중치는 공개 저장소에 포함하지 않습니다.

[검증 기록](validation.md)에서 확인 범위를 참고하세요. archive의 모든 실험 셀을 순서대로 실행하는 대신 상위 폴더의 01–05를 사용하세요.
