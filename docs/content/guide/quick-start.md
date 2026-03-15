# Quick Start

## Prerequisites

| Tool          | Purpose               | Install                                                           |
|---------------|-----------------------|-------------------------------------------------------------------|
| Rust (stable) | Core crate + CLI      | `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \| sh` |
| uv            | Python env management | `curl -LsSf https://astral.sh/uv/install.sh \| sh`                |
| protoc        | Proto compilation     | `brew install protobuf`                                           |
| ffmpeg        | Audio conversion      | `brew install ffmpeg`                                             |

## 1. Clone and build

```bash
git clone https://github.com/lnivva/vetta
cd vetta
cargo build
```

## 2. Start the STT service

```bash
cd services/stt/local
uv sync
uv run python main.py --config config.toml
```

On first run the service downloads `whisper-large-v3` (~3GB). Subsequent starts load from cache.
You will see the ready line when it is accepting connections:

```
[whisper] ready on /tmp/whisper.sock
```

## 3. Generating a test audio file (macOS Only)

::: tip Platform Support
The `say` command below is macOS-specific. Linux/Windows users should instead pass their MP3 using the
`--file /path/to/file.mp3` flag.  
:::

```bash
# Speaker 1 (Samantha)  
say -v Samantha "Good morning everyone and welcome to the Q3 2024 earnings call. We are pleased to report \
 record revenue of 4.2 billion dollars. This represents a 15 percent increase year over year. I will now hand it \ 
 over to our CFO for the financial details." -o /tmp/speaker1.aiff  
  
# Speaker 2 (Daniel)  
say -v Daniel "Thank you. As mentioned, total revenue came in at 4.2 billion. Operating expenses were 2.1 billion,\ 
 resulting in a healthy margin. We also saw strong growth in our cloud division, which contributed 1.8 billion in \
  recurring revenue." -o /tmp/speaker2.aiff  
  
# Speaker 1 again (Samantha)  
say -v Samantha "Thank you for that overview. Let me now open the floor for questions. We have several analysts \
 on the line today." -o /tmp/speaker3.aiff  
  
# Combine with ffmpeg - convert to 16kHz mono WAV  
ffmpeg -y -i /tmp/speaker1.aiff -i /tmp/speaker2.aiff -i /tmp/speaker3.aiff \
 -filter_complex "[0:a][1:a][2:a]concat=n=3:v=0:a=1[out]" -map "[out]" -ar 16000 -ac 1 /tmp/test.wav  
```

## 4. Process test audio file

```bash
cargo run -- earnings process \
  --file /tmp/test.wav \
  --ticker XXXX \
  --year 2024 \
  --quarter q3
```

The pipeline prints live progress as transcript chunks stream back:

```
   VETTA FINANCIAL ENGINE
   ======================

   TARGET:    XXXX Q3 2024
   INPUT:     /tmp/test.mp3

   ✔ VALIDATION PASSED
   Format:    audio/mpeg

   Processing Pipeline:
   1. [✔] Validation
   2. [RUNNING] Transcription (Whisper)
   [0.0s → 3.5s] Good morning and welcome to the Q3 2024 earnings call...
   2. [✔] Transcription (142 segments)
   3. [WAITING] Vector Embedding
```
