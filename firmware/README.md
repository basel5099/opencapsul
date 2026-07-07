# Firmware — TX ("capsule"), RX (receiver), and host viewer

## Toolchain

- **TI Code Composer Studio** (CCS 12+) or `ticlang` command line
- **SimpleLink CC13x0 SDK** (CC1310 is CC13x0 family — *not* the newer CC13x2 SDK)
- Starting examples in the SDK: `rfPacketTx` / `rfPacketRx` (Proprietary RF, EasyLink)
- Flash/debug: on-board XDS110; for Phase 3 custom boards, 2-wire cJTAG from the
  LaunchPad's XDS110 header (TMSC/TCKC + GND + 3V3 sense)

## Radio profile

Start with the SDK's **50 kbps 2-GFSK** at your regional frequency (868.0 MHz EU /
915.0 MHz US), TX power **0 dBm**. It is robust and legal-friendly. Once the pipeline
works, experiment with higher PHY rates and watch reliability vs. power trade-offs —
that trade *is* the lesson. (The CC1310 tops out at 4 Mbps; the real capsule's SPI
feed is rate-matched to exactly that.)

## TX application — the capsule state machine

```
        ┌────────────────────────────────────────────────────────┐
        ▼                                                        │
  [STANDBY 0.6 µA] --RTC tick (1/fps)--> [WAKE]                  │
                                            │                    │
                                    [trigger Arducam capture]    │
                                            │                    │
                                    [poll capture done]          │
                                            │                    │
                              [read JPEG length, stream over     │
                               SPI with µDMA into RAM buffer]    │
                                            │                    │
                                  [chunk + CRC + RF burst(s)]────┘
```

Implementation notes:

- **µDMA on SSI0**: configure ping-pong descriptors so SPI readout never blocks the CPU.
- **RF core queue**: hand chunks to the RF driver back-to-back; the radio sleeps
  automatically between commands.
- **Frame pacing**: RTC compare interrupt at the frame rate (start at 0.5–2 fps).
- **Power hygiene checklist**: unused DIOs to a defined state, camera held in its
  lowest-power mode between frames (or power-gated via a load switch — measure both!),
  no floating inputs, LED flash (Phase 3) fired only during exposure.
- **Telemetry**: append battery voltage (CC1310 built-in battery monitor, AON) and a
  temperature reading to every Nth frame header — free realism, the real capsule does this.

## Packet format (keep it dumb, keep it debuggable)

Radio payload ≤ 128 B works everywhere. Suggested layout:

```c
typedef struct __attribute__((packed)) {
    uint16_t magic;      // 0xCA75
    uint16_t frame_id;   // increments per JPEG
    uint16_t chunk_id;   // 0..n_chunks-1
    uint16_t n_chunks;   // total for this frame
    uint8_t  flags;      // bit0: last chunk; bit1: telemetry present
    uint8_t  len;        // payload bytes in this chunk
    uint8_t  data[110];  // JPEG bytes (and telemetry TLV if flagged)
    uint16_t crc16;      // CCITT over header+data
} cap_chunk_t;           // = 122 bytes
```

Loss strategy for the learning build: **none — tolerate it.** JPEG restart markers or
simply dropping incomplete frames keeps TX-side complexity at capsule-realistic levels
(real capsules are also fire-and-forget with a robust PHY; some add light FEC — a
great Phase 4 contribution).

## RX application

`rfPacketRx` + UART bridge: validate CRC, prepend a 4-byte sync word, forward raw
chunks to the PC at 921600 baud. Keep the RX LaunchPad dumb; all reassembly happens
on the host where you can iterate quickly.

## Host viewer (Python)

```python
# viewer.py — reassemble cap_chunk_t stream from serial, display JPEGs
# pip install pyserial pillow
import serial, struct, io
from PIL import Image

MAGIC = 0xCA75
port = serial.Serial("COM5", 921600, timeout=1)   # adjust port
frames = {}   # frame_id -> {chunk_id: bytes}

def crc16_ccitt(data, crc=0xFFFF):
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021 if crc & 0x8000 else crc << 1) & 0xFFFF
    return crc

buf = b""
while True:
    buf += port.read(4096)
    while len(buf) >= 122:
        if buf[:2] != b"\x75\xCA":          # find sync (little-endian magic)
            buf = buf[1:]; continue
        pkt, buf = buf[:122], buf[122:]
        magic, frame, chunk, total, flags, ln = struct.unpack_from("<HHHHBB", pkt)
        data, crc = pkt[10:10+110], struct.unpack_from("<H", pkt, 120)[0]
        if crc != crc16_ccitt(pkt[:120]):
            continue                        # count these! link-quality metric
        frames.setdefault(frame, {})[chunk] = data[:ln]
        got = frames[frame]
        if len(got) == total:               # frame complete
            jpeg = b"".join(got[i] for i in range(total))
            Image.open(io.BytesIO(jpeg)).show()
            del frames[frame]
```

(Replace `.show()` with an OpenCV window for live video; add a chunk-loss counter and
plot it — instant link-quality lab.)

## Camera pipelines (Phase 3)

Two color variants share this TX architecture — only the "capture" stage differs:

- **Variant A** (HM01B0 + sequential RGB flash + fusion): capture FSM and fusion math
  in [docs/camera-variant-A-hm01b0-rgb-fusion.md](../docs/camera-variant-A-hm01b0-rgb-fusion.md);
  prototype the fusion on the PC first with [tools/rgb_fusion.py](../tools/rgb_fusion.py).
- **Variant B** (HM0360 Bayer): strip-based demosaic → JPEG pipeline in
  [docs/camera-variant-B-hm0360-color.md](../docs/camera-variant-B-hm0360-color.md).

Both emit identical `cap_chunk_t` streams — RX firmware and the viewer are variant-agnostic.

## Milestone checklist

- [ ] M1: `rfPacketTx/Rx` unmodified, LEDs blink across the room
- [ ] M2: Arducam JPEG lands on PC over *wire* (SPI → UART, no radio)
- [ ] M3: full chain — camera → radio → viewer shows a photo
- [ ] M4: duty-cycled build; PPK2 trace shows < 10 mA average at 1 fps
- [ ] M5: chunk-loss statistics vs. distance/obstacles; write it up in `docs/`
- [ ] M6 (Phase 4): the same link through a saline phantom — publish the attenuation curve
- [ ] M7 (Variant A): three UART-dumped mono frames fused on PC via `rgb_fusion.py`, then on-target
- [ ] M8 (Variant B): mono-module bring-up → Bayer part on custom board, strip demosaic on-target
