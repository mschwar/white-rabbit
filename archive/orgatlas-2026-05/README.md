# Archive: OrgAtlas (2026-05)

**Status:** Historical archive only. Not product source. Not an active working tree.

Folded into `mschwar/white-rabbit` on **2026-09-16** from the standalone Developer checkout `/Users/mschwar/Developer/orgatlas` (remote `https://github.com/mschwar/orgatlas.git`). That GitHub remote remains as cold backup; the Mac Developer folder is retired as an active surface after this import.

OrgAtlas here is early parent-brand / voice-memo material adjacent to White Rabbit (wordmark concepts + Monroe St NE meeting transcripts), not a separate shipping product.

## Provenance

| Field | Value |
| --- | --- |
| Source remote | `https://github.com/mschwar/orgatlas.git` |
| Source local path (retired) | `/Users/mschwar/Developer/orgatlas` |
| Approx. content date | 2026-04 / 2026-05 voice memos + May brand notes; transcripts refreshed through 2026-06 |
| Fold date | 2026-09-16 |
| Kind | Brand concepts + meeting audio transcripts / diarization output |

## What is in git

- `brand/` — OrgAtlas wordmark concepts (markdown + SVG)
- `output/transcribe/` — transcript markdown, minutes, executive summaries, action items, and diarized JSON
- **No** root `.m4a`, chunk audio, or speaker-ref WAV/M4A (those are on `/central`)

## Heavy media (not in git)

White Rabbit does not use Git LFS. ~120MB of meeting audio lives on ai-server:

```text
/central/archive/white-rabbit-media-2026-09-16/orgatlas/
```

### Root voice memos

| File | Size (approx) | SHA256 |
| --- | --- | --- |
| `Monroe St NE 7.m4a` | 21MB | `efe09bd913d15e73f468a8f85b19890c6c6e01e0295e5615d50209ae633292f2` |
| `Monroe St NE 14.m4a` | 37MB | `6effab7288315586de566e0445187492a1fe43cf73d6a7f2e6c72e8b51ffc194` |

### Derived audio

Chunk M4As and speaker-reference M4A/WAV under:

```text
/central/archive/white-rabbit-media-2026-09-16/orgatlas/output/transcribe/
```

Full manifest (42 files): [`CENTRAL-MEDIA.SHA256SUMS`](./CENTRAL-MEDIA.SHA256SUMS) and [`docs/archive/white-rabbit-media-2026-09-16.SHA256SUMS`](../../docs/archive/white-rabbit-media-2026-09-16.SHA256SUMS). Verified `OK=42 FAIL=0` on ai-server after upload.

## Related

- Text mirror of these transcripts also landed under [`archive/wr-v3-brainstorm-2026-06/orgatlas-transcripts-audio/`](../wr-v3-brainstorm-2026-06/orgatlas-transcripts-audio/) (WR-v3 had exported a local copy).
- A subset of Monroe St NE 8 notes already exists in-product at [`docs/meeting-notes/`](../../docs/meeting-notes/).
