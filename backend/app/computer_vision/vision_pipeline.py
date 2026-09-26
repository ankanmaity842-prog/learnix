from pathlib import Path
import tempfile

from .code_detector import detect_code
from .diagram_detector import detect_diagrams
from .frame_extractor import extract_frames
from .scene_detector import detect_scene_changes
from .slide_detector import detect_slides
from .text_detector import detect_text
from .visual_complexity import calculate_visual_complexity


def analyze_video(
    video_path: str,
    interval_seconds: float = 10.0,
    max_frames: int = 30,
) -> dict:

    video_name = Path(video_path).stem

    with tempfile.TemporaryDirectory(
        prefix=f"vision_{video_name}_"
    ) as frame_directory:

        frames = extract_frames(
            video_path=video_path,
            output_dir=frame_directory,
            interval_seconds=interval_seconds,
            max_frames=max_frames,
        )

        if not frames:
            return {
                "video_path": video_path,
                "frame_count": 0,
                "scene_change_count": 0,
                "slide_count": 0,
                "code_frame_count": 0,
                "diagram_frame_count": 0,
                "text_frame_count": 0,
                "average_visual_complexity": 1.0,
                "visual_complexity": 1.0,
                "visual_simplicity": 0.0,
                "frames": [],
            }

        scene_changes = detect_scene_changes(
            frames
        )

        slides = detect_slides(
            frames
        )

        frame_analysis = []

        for frame_path in frames:

            text = detect_text(
                frame_path
            )

            diagram = detect_diagrams(
                frame_path
            )

            code = detect_code(
                frame_path
            )

            complexity = calculate_visual_complexity(
                frame_path
            )

            frame_analysis.append(
                {
                    "frame_path": frame_path,
                    "text": text,
                    "diagram": diagram,
                    "code": code,
                    "complexity": complexity,
                }
            )

        slide_count = sum(
            1
            for item in slides
            if item.get(
                "is_slide",
                False,
            )
        )

        code_frame_count = sum(
            1
            for item in frame_analysis
            if item["code"].get(
                "is_code",
                False,
            )
        )

        diagram_frame_count = sum(
            1
            for item in frame_analysis
            if item["diagram"].get(
                "has_diagram",
                False,
            )
        )

        text_frame_count = sum(
            1
            for item in frame_analysis
            if item["text"].get(
                "has_text",
                False,
            )
        )

        complexities = [
            item["complexity"].get(
                "complexity_score",
                0.0,
            )
            for item in frame_analysis
        ]

        simplicities = [
            item["complexity"].get(
                "visual_simplicity",
                0.0,
            )
            for item in frame_analysis
        ]

        average_complexity = (
            sum(complexities)
            / len(complexities)
        )

        average_simplicity = (
            sum(simplicities)
            / len(simplicities)
        )

        return {
            "video_path": video_path,
            "frame_count": len(frames),
            "scene_change_count": len(
                scene_changes
            ),
            "scene_changes": scene_changes,
            "slide_count": slide_count,
            "code_frame_count": code_frame_count,
            "diagram_frame_count": (
                diagram_frame_count
            ),
            "text_frame_count": (
                text_frame_count
            ),
            "average_visual_complexity": round(
                average_complexity,
                4,
            ),
            "visual_complexity": round(
                average_complexity,
                4,
            ),
            "visual_simplicity": round(
                average_simplicity,
                4,
            ),
            "frames": frame_analysis,
        }