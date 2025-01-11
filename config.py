from opencc import OpenCC

# 源目录
SRC_DIR = r"音乐修复/待整理"

# 目标目录
TARGET_DIR = r'音乐修复/已整理'

# 设置简繁转换，如果不想转换，将IS_CC_CONVERT设置为False
# OpenCC  conversion ： 'hk2s', 's2hk', 's2t', 's2tw', 's2twp', 't2hk', 't2s', 't2tw', 'tw2s', and 'tw2sp'
cc = OpenCC('t2s')

IS_CC_CONVERT = True  # 是否需要opencc转换
IS_DELETE_SRC = True  # 是否清空源目录空文件夹
IS_KEEP_COVER = True  # 是否保留封面，根据文件名是"cover"判断封面
IS_MOVE_FILE = True  # 是否移动文件到目标目录
IS_GET_GENRE = False  # 是否获取音乐风格
IS_SPLIT_ARTIST = False  # 是否拆分艺术家(feat或多艺术家)

# 支持清洗的音乐类型
SUPPORT_MUSIC_TYPE = ['.flac', '.dsf', '.mp3']

# 创建目录中需要的专辑艺术家和专辑名，以及FLAC文件名，将不支持的字符替换为支持的字符
CHAR_REPLACE_DICT = {'.': '_', ':': '：', '?': '？', '"': '“', '|': ' ', '*': '', '<': '', '>': '', '\\': '', '/': ''}

# 需要删除的源文件中的文件后缀名，如果想要保留cover，则需要IS_KEEP_SRC_DIR_COVER设置为True
DELETE_FILE_SUFFIX_LIST = ['.cue', '.log', '.txt', '.m3u', '.m3u8', '.nfo', '.md5', '.jpg', '.png', '.tif', '.gif',
                           '.url']

# tag中需要删除的key
POP_KEY_LIST = {
    "FLAC": ['author', 'albumartistsort', 'artistsort', 'albumsort', 'arranger', "acoustid_id", "isrc",
             "length",
             "script", "originalyear", "originaldate", "barcode", "media", "releasecountry", "publisher",
             "label",
             "releasestatus", "id", "comment", "encoder", "performer", 'discid', 'ctdbtrackconfidence',
             'cdtoc', "album artist", "notes", 'gnid', 'aaaa', 'ssss', 'ddddd', 'cccc', 'description'],
    "DSF": ['TSO2', 'TSOP', 'TSRC', 'TMED', 'COMM'],
    "MP3": ['TSO2', 'TSOP', 'TSRC', 'TMED', 'COMM']
}

# deepseek API KEY
# 申请地址：https://platform.deepseek.com/api_keys
API_KEY = ""

# 音乐风格的prompt
MUSIC_GENRE_PROMPT = ("请说出音乐专辑的音乐风格（musicgenre），"
                      "风格请从Pop,Mandopop,K-Pop,J-Pop,Cantopop,Europop,Folk，Folk-Pop,World,Soundtrack,Anime,"
                      "Disco,PianoBallad,Blues,Concert,Live,HeavyMetal,Country,Classical,Indie,Instrumental,Rock,Punk,"
                      "Jazz,NewAge,Dance,Electronic,Hip Hop,Musical,Reggae,Alternative,Holiday,Remix 这些风格中选择。"
                      "请直接给出风格信息，不要缀述。如果有多个风格请用;分隔。如果没有匹配风格请说未知。请清空多余的空格。"
                      "下面给出专辑信息:")

# 歌曲标题中feat
TITLE_SPLIT_FEAT_PROMPT = ("请将音乐名称中解析出feat的(合作的)艺术家信息。多个艺术家之间用英文斜杠/分隔。"
                           "请注意排除歌曲名称，不要将歌曲名称解析成艺术家。"
                           "直接给出艺术家信息，不要赘述。如果没有匹配请说未知。请清空多余的空格。下面给出包含feat的音乐名称:")

# 艺术家字段中feat
ARTIST_SPLIT_FEAT_PROMPT = ("请将音乐艺术家信息中包含feat的情况拆分出单独的艺术家信息。多个艺术家之间用英文斜杠/分隔。"
                            "直接给出艺术家信息，不要赘述。如果没有匹配请说未知。请清空多余的空格。下面给出包含feat的信息:")

# 处理艺术家中的 &
ARTIST_SPLIT_AND_PROMPT = ("请将音乐艺术家信息中包含&符号的情况拆分出单独的艺术家信息。多个艺术家之间用英文斜杠/分隔"
                           "请注意赠别艺术家名称本来就包含&的情况，例如 伍佰 & China Blue"
                           "直接给出艺术家信息，不要赘述。如果没有匹配请说未知。请清空多余的空格。下面给出艺术家信息:")
# tag信息缺失文件列表
lack_tag_file_list = []
