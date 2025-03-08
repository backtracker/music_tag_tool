from cleaner.cleaner import MusicCleaner
from mutagen.mp4 import MP4
from config import POP_KEY_LIST


class M4aCleaner(MusicCleaner):
    def __init__(self, music_file, target_dir, is_cc_convert, is_delete_src, is_move_file):
        super().__init__(music_file, target_dir, is_cc_convert, is_delete_src, is_move_file)
        self.music = MP4(music_file)

    @property
    def title(self):
        key = '\xa9nam'
        return str(self.music.tags[key][0]) if key in self.music.tags else ""

    @title.setter
    def title(self, new_value):
        self.music.tags['\xa9nam'] = [new_value]
        self.music.save()

    @property
    def artist(self):
        key = '\xa9ART'
        return str(self.music.tags[key][0]) if key in self.music.tags else ""

    @artist.setter
    def artist(self, new_value):
        self.music.tags['\xa9ART'] = [new_value]
        self.music.save()

    @property
    def album(self):
        key = '\xa9alb'
        return str(self.music.tags[key][0]) if key in self.music.tags else ""

    @album.setter
    def album(self, new_value):
        self.music.tags['\xa9alb'] = [new_value]
        self.music.save()

    @property
    def track_number(self):
        key = 'trkn'
        return str(self.music.tags[key][0][0]) if key in self.music.tags else ""

    @track_number.setter
    def track_number(self, new_value):
        if new_value:
            self.music.tags['trkn'] = [(int(new_value), 0)]
            self.music.save()

    @property
    def date(self):
        key = '\xa9day'
        return str(self.music.tags[key][0]) if key in self.music.tags else ""

    @date.setter
    def date(self, new_value):
        self.music.tags['\xa9day'] = [new_value]
        self.music.save()

    @property
    def album_artist(self):
        key = 'aART'
        return str(self.music.tags[key][0]) if key in self.music.tags else ""

    @album_artist.setter
    def album_artist(self, new_value):
        self.music.tags['aART'] = [new_value]
        self.music.save()

    @property
    def disc_number(self):
        key = 'disk'
        return str(self.music.tags[key][0][0]) if key in self.music.tags else ""

    @disc_number.setter
    def disc_number(self, new_value):
        if new_value:
            self.music.tags['disk'] = [(int(new_value), 0)]
            self.music.save()

    @property
    def genre(self):
        key = '\xa9gen'
        return str(self.music.tags[key][0]) if key in self.music.tags else ""

    @genre.setter
    def genre(self, new_value):
        self.music.tags['\xa9gen'] = [new_value]
        self.music.save()

    def clean_tags(self):
        super().clean_tags()

    def pop_keys(self):
        pop_key_list = []
        for key in self.music.tags.keys():
            if key in POP_KEY_LIST.get("M4A", []):
                pop_key_list.append(key)
        for key in pop_key_list:
            self.music.tags.pop(key)
        self.music.save() 