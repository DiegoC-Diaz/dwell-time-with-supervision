import cv2
import os
import argparse

def load_frames_from_video(video_path):
    frames = []
    cap = cv2.VideoCapture(video_path)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    return frames




def load_frames_from_folder(folder):
    frames = []
    for filename in sorted(os.listdir(folder)):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            img = cv2.imread(os.path.join(folder, filename))
            if img is not None:
                frames.append(img)
                if len(frames)>100:
                    break
                
    return frames

def show_video(frames, fps=24):
    if not frames:
        print("No frames to display.")
        return
    cv2.namedWindow('Frame Viewer', cv2.WINDOW_NORMAL)
    idx = 0
    playing = True

    while True :
        if playing:
            cv2.imshow('Frame Viewer', frames[idx])
            idx = (idx + 1) % len(frames)
        key = cv2.waitKey(int(1000 / fps))
        if key == ord('q'):
            break
        elif key == ord('p'):
            playing = not playing
    cv2.destroyAllWindows()

if __name__ == "__main__":
    parser=argparse.ArgumentParser("Testing the video Loader")

    parser.add_argument(
        "--path",
        type=str,
        required=True,
        help="frames-folder"
    )


    args=parser.parse_args()
    frames = load_frames_from_folder(args.path)

    show_video(frames,5)