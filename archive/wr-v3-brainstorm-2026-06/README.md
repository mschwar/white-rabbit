# Archive: WR-v3 brainstorm (2026-06)

**Status:** Historical archive only. Not product source. Not an active working tree.

Folded into `mschwar/white-rabbit` on **2026-09-16** from the standalone Developer checkout `/Users/mschwar/Developer/WR-v3` (remote `https://github.com/mschwar/WR-v3.git`). That GitHub remote remains as cold backup; the Mac Developer folder is retired as an active surface after this import.

## Provenance

| Field | Value |
| --- | --- |
| Source remote | `https://github.com/mschwar/WR-v3.git` |
| Source local path (retired) | `/Users/mschwar/Developer/WR-v3` |
| Approx. content date | 2026-06 brainstorm photos + transcripts; emails Apr–May 2026 |
| Fold date | 2026-09-16 |
| Kind | Pre-product handwritten lead-gen brainstorm media + transcripts + Lee lead-gen email export |

Original source README preserved as [`SOURCE-README.md`](./SOURCE-README.md).

## What is in git

- Six brainstorm markdown transcripts (`01`–`06`) — **required**; companion HEIC photos are **not** in git
- `combined-source.txt` — raw combined transcription paste
- `emails/lee-lead-gen/` — email markdown + small CSV/XLSX/DOCX attachments
- `orgatlas-transcripts-audio/` — **text/JSON only** (transcripts, minutes, diarized JSON). Audio was a local copy of orgatlas material (see below)

## Heavy media (not in git)

White Rabbit does not use Git LFS. HEIC brainstorm photos (~8MB) live on ai-server:

```text
/central/archive/white-rabbit-media-2026-09-16/wr-v3/
```

| File | SHA256 |
| --- | --- |
| `01-targeting-dimensions.heic` | `8acc15c026acb1de96964d843692fe25575fcccecdd530c1be99f4711cde3061` |
| `02-coherent-segment-request.heic` | `50a7c60dc620f1198d1f3635215d4ce62fc7d5463b6a5cd204fa598bf9269286` |
| `03-data-sources.heic` | `5abb299ac132dad3cca09eb15691eff92d0a69d4bc96a18c781732ab13dc5969` |
| `04-request-formula.heic` | `dab468b6c5f9d9c3b5f4e496120611ce85951dad5b89ffcc9d35d2331693f55b` |
| `05-brain-dump-requests.heic` | `caa6fe675985035a7db52842cba646c73401eb496ca91234844269385500be3c` |
| `06-original-workflow.heic` | `437df30d1d3a8b6147276e9b4b3eed110beb7c0ded881741bc8d6c0ebc07ac14` |

Full media manifest: [`CENTRAL-MEDIA.SHA256SUMS`](./CENTRAL-MEDIA.SHA256SUMS) and [`docs/archive/white-rabbit-media-2026-09-16.SHA256SUMS`](../../docs/archive/white-rabbit-media-2026-09-16.SHA256SUMS).

### OrgAtlas audio nested under WR-v3

`orgatlas-transcripts-audio/` originally held private meeting audio that was **byte-identical** to the orgatlas checkout originals (verified 2026-09-16):

| File | SHA256 |
| --- | --- |
| `Monroe St NE 7.m4a` | `efe09bd913d15e73f468a8f85b19890c6c6e01e0295e5615d50209ae633292f2` |
| `Monroe St NE 14.m4a` | `6effab7288315586de566e0445187492a1fe43cf73d6a7f2e6c72e8b51ffc194` |

Canonical audio + chunk/speaker-ref media for those meetings is stored once under:

```text
/central/archive/white-rabbit-media-2026-09-16/orgatlas/
```

See also [`archive/orgatlas-2026-05/`](../orgatlas-2026-05/).

## Related in-repo notes

White Rabbit already kept a subset of Monroe St NE 8 notes under [`docs/meeting-notes/`](../../docs/meeting-notes/). This archive is the broader pre-product dump, not a replacement for that path.
