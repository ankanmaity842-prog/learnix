from pathlib import Path

import cv2


def extract_frames(
    video_path: str,
    output_dir: str,
    interval_seconds: float = 10.0,
    max_frames: int = 30,
) -> list[str]:

    video = cv2.VideoCapture(video_path)

    if not video.isOpened():
        raise ValueError(
            f"Unable to open video: {video_path}"
        )

    output_path = Path(output_dir)
    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    fps = video.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 30.0

    total_frames = int(
        video.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    duration = (
        total_frames / fps
        if total_frames > 0
        else 0.0
    )

    if duration <= 0:
        video.release()
        return []

    timestamps = []
    current_time = 0.0

    while current_time < duration:
        timestamps.append(current_time)
        current_time += max(
            interval_seconds,
            1.0,
        )

    if len(timestamps) > max_frames:
        step = len(timestamps) / max_frames

        timestamps = [
            timestamps[
                min(
                    int(index * step),
                    len(timestamps) - 1,
                )
            ]
            for index in range(max_frames)
        ]

    frame_paths = []

    for index, timestamp in enumerate(
        timestamps
    ):
        video.set(
            cv2.CAP_PROP_POS_MSEC,
            timestamp * 1000,
        )

        success, frame = video.read()

        if not success:
            continue

        frame_path = (
            output_path
            / f"frame_{index:05d}.jpg"
        )

        saved = cv2.imwrite(
            str(frame_path),
            frame,
        )

        if saved:
            frame_paths.append(
                str(frame_path)
            )

    video.release()

    return frame_paths