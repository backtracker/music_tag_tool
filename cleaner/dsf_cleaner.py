from cleaner.cleaner import MusicCleaner
from mutagen.dsf import DSF
from mutagen.id3 import TIT2, TALB, TPE1, TPE2, TRCK, TDRC, TPOS
from config import POP_KEY_LIST


class DsfCleaner(MusicCleaner):
    def __init__(self, filename):
        super().__init__(filename)
        self.music = DSF(filename)

    @property
    def title(self):
        return str(self.music["TIT2"]) if "TIT2" in self.music.keys() else ""

    @title.setter
    def title(self, new_value):
        self.music["TIT2"] = TIT2(encoding=3, text=[new_value])
        self.music.save()

    @property
    def artist(self):
        return str(self.music["TPE1"]) if "TPE1" in self.music.keys() else ""

    @artist.setter
    def artist(self, new_value):
        self.music["TPE1"] = TPE1(encoding=3, text=[new_value])
        self.music.save()

    @property
    def album(self):
        return str(self.music["TALB"]) if "TALB" in self.music.keys() else ""

    @album.setter
    def album(self, new_value):
        self.music["TALB"] = TALB(encoding=3, text=[new_value])
        self.music.save()

    @property
    def track_number(self):
        return str(self.music["TRCK"]) if "TRCK" in self.music.keys() else ""

    @track_number.setter
    def track_number(self, new_value):
        self.music["TRCK"] = TRCK(encoding=3, text=[new_value])
        self.music.save()

    @property
    def date(self):
        return str(self.music["TDRC"]) if "TDRC" in self.music.keys() else ""

    @date.setter
    def date(self, new_value):
        self.music["TDRC"] = TDRC(encoding=3, text=[new_value])
        self.music.save()

    @property
    def album_artist(self):
        return str(self.music["TPE2"]) if "TPE2" in self.music.keys() else ""

    @album_artist.setter
    def album_artist(self, new_value):
        self.music["TPE2"] = TPE2(encoding=3, text=[new_value])
        self.music.save()

    @property
    def disc_number(self):
        return str(self.music["TPOS"]) if "TPOS" in self.music.keys() else ""

    @disc_number.setter
    def disc_number(self, new_value):
        self.music["TPOS"] = TPOS(encoding=3, text=[new_value])
        self.music.save()

    def clean_tags(self):
        super().clean_tags()

    def pop_keys(self):
        pop_key_list = []
        for key in self.music.keys():
            if key in POP_KEY_LIST.get("DSF", []):
                pop_key_list.append(key)
            if key.startswith("TXXX"):  # 清除DSF用户自定义的key
                pop_key_list.append(key)
        for key in pop_key_list:
            self.music.pop(key)
        self.music.save()
