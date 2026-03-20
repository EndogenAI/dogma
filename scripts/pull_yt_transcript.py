import sys

from youtube_transcript_api import YouTubeTranscriptApi


def download_transcript(video_id, output_path):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        # Try to get manually created transcript first, fall back to auto-generated
        try:
            transcript = transcript_list.find_manually_created_transcript(["en"])
        except Exception:
            transcript = transcript_list.find_generated_transcript(["en"])

        data = transcript.fetch()

        # Clean transcript: join text with spaces
        full_text = " ".join([t["text"] for t in data])

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_text)

        print(f"Successfully downloaded transcript to {output_path}")
        return True
    except Exception as e:
        print(f"Error downloading transcript: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python pull_yt_transcript.py <video_id> <output_path>")
        sys.exit(1)

    try:
        from youtube_transcript_api import YouTubeTranscriptApi

        api = YouTubeTranscriptApi()
        transcripts = api.list(sys.argv[1])
        # Try for English manually created transcript, fall back to auto-generated
        try:
            transcript = transcripts.find_manually_created_transcript(["en"])
        except Exception:
            transcript = transcripts.find_generated_transcript(["en"])

        data = transcript.fetch()
        # Access .text attribute from each snippet
        full_text = " ".join([t.text for t in data])

        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(full_text)
        print(f"Successfully downloaded transcript to {sys.argv[2]}")
    except Exception as e:
        print(f"Error downloading transcript: {e}")
        sys.exit(1)
