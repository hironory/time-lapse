import gradio as gr
import cv2
import os
import moviepy.editor as mp
from pathlib import Path
import numpy as np

# タイムラプス動画作成機能
def create_timelapse(input_video, frame_rate, alpha_decay, output_dir):
    try:
        # 動画の読み込み
        cap = cv2.VideoCapture(input_video)
        # フレーム情報を取得
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        input_video_frame_rate = int(cap.get(cv2.CAP_PROP_FPS))
        input_video_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        frames = []
        count = 0

        # 過去フレームの保存用
        blend_frame = np.zeros((frame_height, frame_width, 3), dtype=np.float32)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if count % int(frame_rate) == 0:
                frame = frame.astype(np.float32) / 255.0
                blend_frame = blend_frame * (1 - alpha_decay) + frame * alpha_decay
                blended_frame = (blend_frame * 255).astype(np.uint8)    

                frames.append(blended_frame)
            count += 1

        cap.release()
        
        # フレームの保存
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        for i, frame in enumerate(frames):
            cv2.imwrite(f"{output_dir}/frame_{i:04d}.jpg", frame)

        # タイムラプス動画の作成
        FPS=30
        clip = mp.ImageSequenceClip([f"{output_dir}/frame_{i:04d}.jpg" for i in range(len(frames))], fps=FPS)
        output_video_path = os.path.join(output_dir, "timelapse.mp4")
        clip.write_videofile(output_video_path, codec="libx264")

        input_video_info = f"""
            入力動画情報: フレーム数: {input_video_frame_count}, 
            フレームレート: {input_video_frame_rate},
            総フレーム数: {input_video_frame_count}"""
        output_video_info = f"""
            出力動画情報: フレーム数: {len(frames)}, 
            フレームレート: {FPS}, 
            alpha decay: {alpha_decay}"""
        output_message = f"タイムラプス動画が作成されました！保存先: {output_video_path}"

        return output_message, input_video_info+output_video_info
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

def process(input_video, frame_rate, alpha_decay, output_dir):
    if input_video is None:
        return "エラー：動画ファイルをアップロードしてください。"
    if not output_dir:
        return "エラー：保存先ディレクトリを指定してください。"
    if not frame_rate or frame_rate <= 0:
        return "エラー：正しいフレーム間隔を指定してください。"
    if not alpha_decay or alpha_decay <= 0:
        return "エラー：正しいalpha decayを指定してください。"  
    return create_timelapse(input_video.name, frame_rate, alpha_decay, output_dir)

# Gradioインターフェースの構築
with gr.Blocks() as demo:
    gr.Markdown("## タイムラプス動画作成ツール")
    gr.Markdown("動画ファイルをアップロードし、フレーム間隔と保存先を指定してください。")

    video_input = gr.File(
        label="動画ファイルを選択 (MTS, MP4, AVI)",
        file_types=["video"]  # 動画ファイルのみを許可
    )
    frame_rate = gr.Number(
        label="フレーム間隔 (例: 5)",
        value=5,
        minimum=1
    )
    alpha_decay = gr.Number(
        label="alpha decay: 古いフレームほど透明度を減少させる割合 (例: 0.5)",
        value=0.5,
        minimum=0,
        maximum=1
    )

    output_dir = gr.Textbox(
        label="保存先ディレクトリを指定",
        placeholder="例: /app/output",
        value="/app/output"  # デフォルト値を設定
    )
    output_video_info = gr.Textbox(label="動画情報", interactive=False)
    output_message = gr.Textbox(label="出力結果", interactive=False)

    submit_button = gr.Button("タイムラプスを作成")
    submit_button.click(
        process,
        inputs=[video_input, frame_rate, alpha_decay, output_dir],
        outputs=[output_message, output_video_info]
    )

# 起動
demo.launch(server_name="0.0.0.0", share=False)
