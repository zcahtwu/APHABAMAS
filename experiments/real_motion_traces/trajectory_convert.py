"""Convert BrainMRIMotionDB tracking data to piecewise trajectories."""

import json
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation
from tqdm import tqdm


HERE = Path(__file__).resolve().parent
INPUT_DIRECTORY = HERE / "tracking_json"
OUTPUT_DIRECTORY = HERE / "piecewise_trajectories"
NUMBER_OF_TIME_POINTS = 256
TR = 2.3
TOTAL_TIME = TR * NUMBER_OF_TIME_POINTS


def to_seconds(timestamp):
    hour, minute, second = timestamp.split(":")
    return int(hour) * 3600 + int(minute) * 60 + float(second)


def convert_tracking_data(data):
    """Convert one tracking record without changing its sampling logic."""
    motion = data["MotionData"][0]
    start = to_seconds(motion["TimeStamp"][0])
    recorded_times = np.array([
        to_seconds(timestamp) - start for timestamp in motion["TimeStamp"]
    ])
    time_points = np.linspace(
        0, TOTAL_TIME, NUMBER_OF_TIME_POINTS, endpoint=False
    )
    translation = np.zeros((NUMBER_OF_TIME_POINTS, 3))
    rotation = np.zeros((NUMBER_OF_TIME_POINTS, 3))

    for index in range(1, NUMBER_OF_TIME_POINTS):
        source = np.argmin(np.abs(recorded_times - time_points[index]))
        matrix = np.array([
            [motion[f"M{row}{column}"][source] for column in range(1, 5)]
            for row in range(1, 4)
        ])
        translation[index] = matrix[:, 3]
        rotation[index] = Rotation.from_matrix(matrix[:, :3]).as_euler(
            "xyz", degrees=True
        )

    return {
        "time_points": np.hstack((time_points / TOTAL_TIME, 1)).tolist(),
        "translation": translation.tolist(),
        "rotation": rotation.tolist(),
    }


def convert_file(input_path, output_directory=OUTPUT_DIRECTORY):
    with Path(input_path).open() as file:
        trajectory = convert_tracking_data(json.load(file))
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    with (output_directory / Path(input_path).name).open("w") as file:
        json.dump(trajectory, file, indent=4)
    return trajectory


def main():
    for input_path in tqdm(sorted(INPUT_DIRECTORY.glob("*.json"))):
        convert_file(input_path)


if __name__ == "__main__":
    main()
