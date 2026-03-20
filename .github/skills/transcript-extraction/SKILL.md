---
name: transcript-extraction
description: Encodes the protocol for extracting and cleaning transcripts from video sources (primarily YouTube) during research sessions. USE FOR: pulling closed captions or auto-generated transcripts when a video is a primary research source; cleaning timestamps and speaker markers for better LLM readability; populating .cache/transcripts/ before a synthesis phase. DO NOT USE FOR: general web scraping (use source-caching); downloading video/audio files; real-time transcription of live streams.
issue: 397
governance: Endogenous-First
---

# SKILL: Transcript Extraction

This skill governs the extraction and cleaning of transcripts from video sources to support the **Endogenous-First** axiom ([MANIFESTO.md § 1](../../../MANIFESTO.md#1-endogenous-first)) by ensuring all source signals—even non-textual ones—are distilled into searchable, readable Markdown/text artifacts. It operates under the global constraints of [AGENTS.md](../../../AGENTS.md) regarding file-writing and local compute.

## Beliefs & Context

1. **Information Density**: Video sources often contain unique practitioner insights (demos, conference talks) not found in written docs. Distilling them into text allows for local semantic search and cross-referencing.
2. **LCF Adherence**: By caching transcripts in `.cache/transcripts/`, we avoid repeated network hits and high-token external model reads of video URLs.
3. **Artifact Integrity**: Transcripts must be cleaned of redundant timestamps and repetitive filler to preserve context window space.

## Workflow & Intentions

### 1. Identify Video Source
Extract the Video ID from the URL (e.g., `J5KTpq7hVn4` from `https://youtu.be/J5KTpq7hVn4`).

### 2. Verify Cache First
Check if the transcript already exists in the local cache before attempting extraction.
```bash
ls .cache/transcripts/video_<VIDEO_ID>.txt
```

### 3. Extraction Protocol
Use the designated internal script to pull the transcript. Prefer manually created English transcripts over auto-generated versions when available.

```bash
uv run python scripts/pull_yt_transcript.py <VIDEO_ID> .cache/transcripts/video_<VIDEO_ID>.txt
```

### 4. Verification Check
Confirm the file is non-empty and contains readable text.
```bash
test -s .cache/transcripts/video_<VIDEO_ID>.txt && head -n 5 .cache/transcripts/video_<VIDEO_ID>.txt
```

## Constraints

- **UTF-8 Only**: All extracted transcripts must be stored as UTF-8 encoded plain text.
- **Privacy**: Only pull transcripts for public videos.
- **Minimal Metadata**: Focus on the spoke word; omit frame data or visual descriptions unless critical to the research question.
- **Pathing**: Always store the output in `.cache/transcripts/` to ensure it is gitignored but available for the current session.

## Output Examples

### Successful Extraction Log
```markdown
## Transcript Extraction — video_J5KTpq7hVn4
- **Source**: https://youtu.be/J5KTpq7hVn4
- **Status**: Captured to `.cache/transcripts/video_J5KTpq7hVn4.txt`
- **Signal**: Clean text, English (manual)
```
