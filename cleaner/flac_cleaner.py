from cleaner.cleaner import MusicCleaner
from mutagen.flac import FLAC
from config import POP_KEY_LIST


class FlacCleaner(MusicCleaner):
    def __init__(self, filename):
        super().__init__(filename)
        self.music = FLAC(filename)

    @property
    def title(self):
        key = "title"
        # flac key的值是个list,有这个key则取列表第一个元素
        return self.music[key][0] if key in self.music.keys() else ""

    @title.setter
    def title(self, new_value):
        self.music["title"] = new_value
        self.music.save()

    @property
    def artist(self):
        key = "artist"
        return self.music[key][0] if key in self.music.keys() else ""

    @artist.setter
    def artist(self, new_value):
        self.music["artist"] = new_value
        self.music.save()

    @property
    def album(self):
        key = "album"
        return self.music[key][0] if key in self.music.keys() else ""

    @album.setter
    def album(self, new_value):
        self.music["album"] = new_value
        self.music.save()

    @property
    def track_number(self):
        key = "tracknumber"
        return self.music[key][0] if key in self.music.keys() else ""

    @track_number.setter
    def track_number(self, new_value):
        self.music["tracknumber"] = new_value
        self.music.save()

    @property
    def date(self):
        key = "date"
        return self.music[key][0] if key in self.music.keys() else ""

    @date.setter
    def date(self, new_value):
        self.music["date"] = new_value
        self.music.save()

    @property
    def album_artist(self):
        key = "albumartist"
        return self.music[key][0] if key in self.music.keys() else ""

    @album_artist.setter
    def album_artist(self, new_value):
        self.music["albumartist"] = new_value
        self.music.save()

    @property
    def disc_number(self):
        key = "discnumber"
        return self.music[key][0] if key in self.music.keys() else ""

    @disc_number.setter
    def disc_number(self, new_value):
        self.music["discnumber"] = new_value
        self.music.save()

    def clean_tags(self):
        super().clean_tags()

    def pop_keys(self):
        pop_key_list = []
        for key in self.music.keys():
            if key in POP_KEY_LIST.get("FLAC", []):
                pop_key_list.append(key)
            if key.startswith("musicbrainz") or key.startswith("itunes"):
                pop_key_list.append(key)
        for key in pop_key_list:
            self.music.pop(key)
        self.music.save()
