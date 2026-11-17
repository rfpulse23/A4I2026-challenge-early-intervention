import subprocess
from pathlib import Path

VIDEO_DIR = Path("/config/A4I2026-challenge-early-intervention/demo_video")
input_video = VIDEO_DIR / "first_milestones_3min_pitch_demo.mp4"
output_video = VIDEO_DIR / "first_milestones_3min_pitch_official.mp4"

# Speed up video and audio by 1.68x: 294s / 1.68 = 175s (~2m 55s, strictly <= 3:00)
# video filter: setpts=PTS/1.68
# audio filter: atempo=1.68
cmd = [
    "ffmpeg", "-y",
    "-i", str(input_video),
    "-filter_complex", "[0:v]setpts=PTS/1.68[v];[0:a]atempo=1.68[a]",
    "-map", "[v]",
    "-map", "[a]",
    "-c:v", "libx264",
    "-c:a", "aac",
    "-pix_fmt", "yuv420p",
    str(output_video)
]
subprocess.run(cmd, check=True)

res = subprocess.run([
    "ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1", str(output_video)
], capture_output=True, text=True)
dur = float(res.stdout.strip())
print(f"Official Submission Video Duration: {int(dur // 60)}m {int(dur % 60)}s ({dur:.1f} seconds - Strictly <= 3:00 SLA)")
