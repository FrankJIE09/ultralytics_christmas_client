from pydub import AudioSegment
from pydub.playback import play
import os


def split_mp3(file_path, output_dir, split_time):
    """
    将一个 MP3 文件分割成两段。

    :param file_path: 输入的 MP3 文件路径
    :param output_dir: 输出文件夹
    :param split_time: 分割时间（以毫秒为单位）
    """
    try:
        # 加载 MP3 文件
        audio = AudioSegment.from_file(file_path)

        # 检查输出目录是否存在，不存在则创建
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 分割音频
        first_part = audio[:split_time]
        second_part = audio[split_time:]

        # 输出文件路径
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_file1 = os.path.join(output_dir, f"{base_name}_part1.mp3")
        output_file2 = os.path.join(output_dir, f"{base_name}_part2.mp3")

        # 导出分割后的音频
        first_part.export(output_file1, format="mp3")
        second_part.export(output_file2, format="mp3")

        print(f"文件已成功分割为：\n{output_file1}\n{output_file2}")
    except Exception as e:
        print(f"发生错误：{e}")


# 使用示例
if __name__ == "__main__":
    input_file = "santa-claus-a-reading-christmas-story-17777.mp3"  # 输入的 MP3 文件
    output_folder = "output_segments"  # 输出目录
    split_duration = 5000  # 分割时间，单位为毫秒（30秒）

    split_mp3(input_file, output_folder, split_duration)
