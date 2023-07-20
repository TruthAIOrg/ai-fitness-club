from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# 在视频中添加水印
def add_watermark(input_path, output_path, watermark_text="真AI健身\nfit.truthai.fun"):
    print(f"[add_watermark] input_path={input_path}, output_path={output_path}")

    # 加载视频
    video = VideoFileClip(input_path)

    # 创建水印
    watermark = (TextClip(watermark_text, fontsize=66, color='white', font="/System/Library/Fonts/PingFang.ttc")
                 .set_duration(video.duration)
                 .set_pos(lambda clip: ("right", "bottom"))
                 .margin(right=10, bottom=10, opacity=0)  # 设置右边和底部的间距
                 .set_opacity(0.5))

    # # 将水印添加到视频上
    final_clip = CompositeVideoClip([video, watermark])

    # 将水印添加到视频上：这样没有内容显示
    # final_clip = CompositeVideoClip([watermark, video])  # 这里把顺序互换了

    # 输出到文件
    final_clip.write_videofile(output_path, codec='libx264')

if __name__ == '__main__':
    input_path = 'https://planfit-images.s3.ap-northeast-2.amazonaws.com/training-videos/1001.mp4'
    output_path = './watermark_test_output_1001.mp4'
    add_watermark(input_path, output_path)

# import cv2
# from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# def add_watermark(input_path, output_path, watermark_text="AI Fitness"):
#     print(f"[add_watermark] input_path={input_path}, output_path={output_path}")

#     # 加载视频
#     video = VideoFileClip(input_path)

#     # 创建水印
#     watermark = (TextClip(watermark_text, fontsize=70, color='gray')
#                  .set_duration(video.duration)
#                  .set_position('center'))

#     # 将水印转换为图片，并设置透明度
#     watermark_img = watermark.img
#     print(watermark_img.shape)
#     watermark_img = cv2.cvtColor(watermark_img, cv2.COLOR_RGB2RGBA)

#     watermark_img[..., 3] = 128
#     watermark = watermark.set_duration(video.duration)

#     # 将水印添加到视频的底部
#     final_clip = CompositeVideoClip([video, watermark])

#     # 输出到文件
#     final_clip.write_videofile(output_path, codec='libx264')

# if __name__ == '__main__':
#     input_path = 'https://planfit-images.s3.ap-northeast-2.amazonaws.com/training-videos/1006.mp4'
#     output_path = './watermark_test_output_1006.mp4'
#     add_watermark(input_path, output_path)