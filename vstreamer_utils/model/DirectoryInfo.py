import vstreamer_utils
from vstreamer_utils import model
import pathlib


class DirectoryInfo:
    def __init__(self, path, directory_root):
        path = pathlib.Path(path)
        directory_root = pathlib.Path(directory_root)
        if not path.is_dir():
            raise ValueError("'%s' is not a directory" % str(path))
        self.name = str(path.name)
        self.path = str(path.relative_to(directory_root))

        def key(file):
            return not file.is_dir(), file

        self.entries = [model.FileEntry(x, directory_root) for x in sorted(path.iterdir(), key=key)
                        if x.is_dir() or vstreamer_utils.is_video_file(x)]