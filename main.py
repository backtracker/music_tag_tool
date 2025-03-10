#!/usr/bin/env /usr/local/bin/python3.10
import click
import os
from openai import OpenAI
from typing import List
from typing import Optional
from collections import OrderedDict
from config import *
from cleaner.flac_cleaner import FlacCleaner
from cleaner.dsf_cleaner import DsfCleaner
from cleaner.mp3_cleaner import Mp3Cleaner
from cleaner.m4a_cleaner import M4aCleaner
from cleaner.cleaner import MusicCleaner

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)


def unique_artists(artists):
    list_artist = artists.split('/')
    # 使用OrderedDict保存顺序
    ordered_dict = OrderedDict.fromkeys(list_artist)
    new_artists = '/'.join(ordered_dict.keys())
    return new_artists


def create_music_cleaner(music_file, target_dir, is_cc_convert, is_delete_src, is_move_file) -> Optional[MusicCleaner]:
    # 定义文件扩展名到清理器类的映射
    cleaner_mapping = {
        ".flac": FlacCleaner,
        ".dsf": DsfCleaner,
        ".mp3": Mp3Cleaner,
        ".m4a": M4aCleaner
    }
    # 获取文件扩展名
    file_extension = os.path.splitext(music_file.lower())[1]
    # 根据扩展名查找对应的清理器类
    cleaner_class = cleaner_mapping.get(file_extension)
    if cleaner_class:
        return cleaner_class(music_file, target_dir, is_cc_convert, is_delete_src, is_move_file)
    return None


def call_ai(prompt) -> Optional[str]:
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt},
            ],
            stream=False
        )
        r = response.choices[0].message.content
        print("AI返回：{}".format(r.strip()))
        return r.strip() if r != "未知" else None
    except Exception as e:
        print(f"调用AI接口时出错: {e}")
        return None


# 处理歌手信息中包含&的清空进行清理，返回匹配的歌手和剩余文本
def clean_artists(text, target_artists):
    # 预处理：生成标准化键到原始名称的映射
    original_map = {}
    for artist in target_artists:
        # 移除空格并转为小写作为匹配键
        key = artist.replace(" ", "").lower()
        original_map[key] = artist  # 记录原始名称

    words = text.split()
    n = len(words)
    remove_ranges = []
    matched_artists = []  # 存储匹配到的原始艺术家名称

    i = 0
    while i < n:
        max_length = 0
        found_key = None

        # 从当前位置i开始，尝试匹配最长可能的连续单词组合
        for j in range(i + 1, min(i + 5, n + 1)):  # 假设艺术家名称最多4个单词
            candidate = " ".join(words[i:j])
            normalized = candidate.replace(" ", "").lower()

            # 如果标准化后的候选值在目标列表中
            if normalized in original_map:
                # 优先选择更长的匹配（例如防止"南拳妈妈"误匹配"南拳妈妈&Lara"的前半部分）
                if (j - i) > max_length:
                    max_length = j - i
                    found_key = normalized

        if found_key:
            # 记录需要删除的范围和匹配到的原始名称
            remove_ranges.append((i, i + max_length))
            matched_artists.append(original_map[found_key])
            i += max_length  # 跳过已处理的部分
        else:
            i += 1

    # 构造清理后的文本
    result = []
    last_end = 0
    for start, end in remove_ranges:
        result.extend(words[last_end:start])
        last_end = end
    result.extend(words[last_end:])

    cleaned_text = " ".join(result)
    return matched_artists, cleaned_text  # 返回匹配列表和清理后的文本


def process_feat(music_cleaner, prompt_template, text):
    """
    处理包含 feat 的情况，调用 AI 拆分艺术家，并更新音乐文件的艺术家信息
    :param music_cleaner: 音乐文件清理器实例
    :param prompt_template: AI 调用的提示模板
    :param text: 标题或者艺术家中的feat文本
    """
    if "feat" in music_cleaner.title.lower() or "feat" in music_cleaner.artist.lower():
        print("-" * 80)
        print(f"开始处理歌曲 “{music_cleaner.title}” 名称/艺术家信息 “{text}” 中的 feat 歌手...")
        prompt = f"{prompt_template} {text}"
        split_artists = call_ai(prompt)
        if split_artists is not None:
            # 确保包含专辑艺术家并去重
            all_artists = f"{music_cleaner.album_artist}/{split_artists}"
            new_artists = unique_artists(all_artists)
            music_cleaner.artist = new_artists
            print(f"歌曲 “{music_cleaner.title}” 艺术家设置为：{new_artists}")

def get_all_music_file(dir) -> List[str]:
    """
    遍历SRC_DIR目录下全部flac文件，并返回文件列表
    """
    music_file_list = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            extension = os.path.splitext(file)[1]
            if extension.lower() in SUPPORT_MUSIC_TYPE:
                music_file_list.append(os.path.join(root, file))
    return music_file_list

def delete_empty_dir(folder, is_keep_cover):
    """
    获取目录下所有文件,删除后缀在DELETE_FILE_SUFFIX_LIST中的文件,然后删除空的目录
    """
    # 查找目录下全部文件，得到一个列表
    # 待删除文件列表
    delete_file_list = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            # 如果file的后缀名在SUFFIX_LIST中，则将文件加入待删除列表
            if os.path.splitext(file)[1].lower() in DELETE_FILE_SUFFIX_LIST:
                # 判断是否是封面文件， 如果不是封面则添加到删除列表中
                if is_keep_cover:
                    if "cover" not in os.path.basename(file).split(".")[0].lower():
                        delete_file_list.append(os.path.join(root, file))
                else:
                    delete_file_list.append(os.path.join(root, file))

    # 删除文件
    for file in delete_file_list:
        print("删除文件:{}".format(file))
        os.remove(file)
    # 删除空目录
    dir_list = []
    for root, dirs, files in os.walk(folder):
        for dir in dirs:
            dir_list.append(os.path.join(root, dir))
    dir_list.sort(reverse=True)
    for dir in dir_list:
        if len(os.listdir(dir)) == 0:
            print("删除空目录:{}".format(dir))
            os.rmdir(dir)

@click.command()
@click.option('-s', '--src_dir', default=SRC_DIR, help='源目录')
@click.option('-t', '--target_dir', default=TARGET_DIR, help='目标目录')
@click.option('-c', '--is_cc_convert', default=IS_CC_CONVERT,
              help="是否需要opencc转换")
@click.option('-d', '--is_delete_src', default=IS_DELETE_SRC, help='是否清空源目录空文件夹')
@click.option('-m', '--is_move_file', default=IS_MOVE_FILE, help='是否移动文件到目标目录')
@click.option('-k', '--is_keep_cover', default=IS_KEEP_COVER, help='是否保留封面，根据文件名包含"cover"判断封面')
@click.option('-g', '--is_get_genre', default=IS_GET_GENRE,
              help='是否根据大模型获取音乐风格。使用前请在config.py中配置API_KEY')
@click.option('-a', '--is_split_artist', default=IS_SPLIT_ARTIST,
              help='是否根据大模型拆分多艺术家。使用前请在config.py中配置API_KEY')
def run(src_dir, target_dir, is_cc_convert, is_delete_src, is_move_file, is_keep_cover, is_get_genre, is_split_artist):
    """
    FLAC 、DSF、MP3 音乐 tag 清洗工具。
    对音乐文件进行批量操作前，务必复制小部分音乐文件进行小范围测试！！！
    修改confiy.py中SRC_DIR和TARGET_DIR，运行main.py脚本进行音乐Tag清洗
    """
    # 添加AI配置检查
    if (is_get_genre or is_split_artist) and (not API_KEY or not BASE_URL or not MODEL):
        print("启用音乐风格获取或艺术家拆分功能时，请确保在config.py中正确配置 API_KEY、BASE_URL 和 MODEL")
        return -1

    print(f"开始清洗目录 {src_dir} ...")
    print("=" * 100)
    music_file_list = get_all_music_file(src_dir)

    for music_file in music_file_list:
        print("-" * 80)
        print("开始清洗文件: {}".format(music_file))
        music_cleaner = create_music_cleaner(music_file, target_dir, is_cc_convert, is_delete_src, is_move_file)
        if music_cleaner is not None:
            music_cleaner.clean_tags()  # 清洗tag
        else:
            print(f"不支持的文件类型: {music_file}")
    print("音乐文件tag预清洗完成。")
    print("=" * 100)

    # 排除tag信息不全的文件
    # 完整tag的文件列表
    full_tag_music_list = [music_file for music_file in music_file_list if music_file not in lack_tag_file_list]
    album_music_cleaner_dict = {}  # 根据专辑名称存放歌曲
    for music_file in full_tag_music_list:
        music_cleaner = create_music_cleaner(music_file, target_dir, is_cc_convert, is_delete_src, is_move_file)
        if music_cleaner is not None:
            album_music_cleaner_dict.setdefault(music_cleaner.album, []).append(music_cleaner)

    print("-" * 80)
    # 开始处理碟号，如果专辑是单张碟，将整张专辑碟号字段清空
    for album, music_cleaner_list in album_music_cleaner_dict.items():
        # 专辑是否是单张碟
        is_album_single_disc = True
        for music_cleaner in music_cleaner_list:
            if str(music_cleaner.disc_number).isdigit():
                if int(music_cleaner.disc_number) > 1:
                    is_album_single_disc = False
                    break
        # 清空单张碟的碟号
        if is_album_single_disc:
            for music_cleaner in music_cleaner_list:
                print("开始清空单碟文件碟号：{}".format(music_cleaner.music_file))
                music_cleaner.disc_number = ""

    # 处理专辑音乐风格
    if is_get_genre:
        print("-" * 80)
        print("开始获取音乐风格...")
        for album, music_cleaner_list in album_music_cleaner_dict.items():
            print("-" * 80)
            mc: MusicCleaner = music_cleaner_list[0]
            album_info = f"{mc.album_artist} {mc.album}"
            print(f"开始获取专辑 “{album_info}” 音乐风格...")

            genre_prompt = f"{MUSIC_GENRE_PROMPT}{album_info}"
            genre = call_ai(prompt=genre_prompt)

            if genre is not None:
                print(f"专辑 “{album_info}” 音乐风格:{genre}")
                for music_cleaner in music_cleaner_list:
                    music_cleaner.genre = genre
            else:
                print(f"未查询到专辑 “{album_info}” 风格信息！！！")

    # 处理歌手feat和&
    if is_split_artist:
        # 遍历专辑
        print("-" * 80)
        print("开始拆分艺术家信息...")
        for album, music_cleaner_list in album_music_cleaner_dict.items():
            # 遍历专辑里的歌曲
            for music_cleaner in music_cleaner_list:
                music_cleaner: MusicCleaner
                title: str = music_cleaner.title
                artist: str = music_cleaner.artist
                # 处理feat artist
                if "feat" in title.lower() or "feat" in  artist.lower():
                    process_feat(music_cleaner,
                                 TITLE_SPLIT_FEAT_PROMPT if "feat" in title.lower() else ARTIST_SPLIT_FEAT_PROMPT,
                                 music_cleaner.title if "feat" in title.lower() else artist)
                elif "合唱"  in title.lower():
                    print("-" * 80)
                    print(f"开始处理歌曲 “{title}” 标题中包含“合唱”的艺术家信息...")
                    chorus_prompt = f"{ARTIST_SPLIT_CHORUS_PROMPT} {title}"
                    split_artists = call_ai(chorus_prompt)
                    if split_artists is not None:
                        # 确保包含专辑艺术家并去重
                        all_artists = f"{music_cleaner.album_artist}/{split_artists}"
                        new_artists = unique_artists(all_artists)
                        music_cleaner.artist = new_artists
                        print(f"歌曲 “{title}” 艺术家设置为：{new_artists}")
                    else:
                        print(f"未成功拆分歌曲 “{title}” 的艺术家信息。")
                elif "&" in artist.lower():
                    print("-" * 80)
                    print(f"开始处理歌曲 “{music_cleaner.title}” 艺术家 “{music_cleaner.artist}” 中包含&的艺术家...")
                    matched_artist_list, cleaned_text = clean_artists(text=music_cleaner.artist,
                                                                      target_artists=ARTISTS_WITH_AMPERSAND)
                    print(
                        f"“{music_cleaner.artist}” 清洗完成，匹配艺术家列表：{matched_artist_list}, 剩余文本：“{cleaned_text}”")
                        
                    # 处理剩余文本中还包含&的情况，使用大模型处理
                    if "&" in cleaned_text:
                        print(f"开始处理预清洗完成后仍然包含&的情况，剩余文本：“{cleaned_text}”")
                        artist_split_ampersand_prompt = f"{ARTIST_SPLIT_AMPERSAND_PROMPT} {cleaned_text}"

                        split_artists = call_ai(artist_split_ampersand_prompt)
                        if split_artists is not None:
                            # 艺术家字段中不添加专辑艺术家
                            new_artists = unique_artists(split_artists)  # 去重处理
                            # 添加预处理的艺术家
                            if len(matched_artist_list) > 0:
                                new_artists = "/".join(matched_artist_list) + "/" + new_artists

                            music_cleaner.artist = new_artists
                            print(f"歌曲 “{music_cleaner.title}” 艺术家设置为：{new_artists}")
                        else:
                            new_artists = "/".join(matched_artist_list)
                            music_cleaner.artist = new_artists
                            print(f"歌曲 “{music_cleaner.title}” 艺术家设置为：{new_artists}")
                    else:
                        if cleaned_text != "":
                            new_artists = "/".join(matched_artist_list) + "/" + cleaned_text
                        else:
                            new_artists = "/".join(matched_artist_list)
                        music_cleaner.artist = new_artists
                        print(f"歌曲 “{music_cleaner.title}” 艺术家设置为：{new_artists}")

    print("Tag清洗完成，开始文件处理...")
    print("=" * 100)

    for music_file in full_tag_music_list:
        print("开始处理文件: {}".format(music_file))
        music_cleaner = create_music_cleaner(music_file, target_dir, is_cc_convert, is_delete_src, is_move_file)
        if music_cleaner is None:
            print("不支持的文件类型：{}".format(music_file))
            continue
        new_file = music_cleaner.rename_file()

        if is_move_file and new_file is not None:
            music_cleaner.move_file(new_file)

    # 清空空目录
    if is_delete_src:
        delete_empty_dir(src_dir, is_keep_cover)

    print("=" * 100)
    if len(lack_tag_file_list) > 0:
        print("{} 清洗结束， 共有 {} 个文件失败！！！".format(src_dir, len(lack_tag_file_list)))
        print("失败文件列表如下： ")
        for file in lack_tag_file_list:
            print(file)
    else:
        print("{} 目录清洗完成".format(src_dir))


if __name__ == '__main__':
    run()
