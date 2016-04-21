import os.path


class Picture(object):

    favourite = False
    pixbuf = None

    def __init__(self, directory, filename):
        self.directory = directory
        self.filename = filename
        self.favourite = self.check_is_favourite()

    @property
    def favourite_marker_path(self):
        filename = '.{filename}.favourite'.format(filename=self.filename)
        return os.path.join(self.directory, filename)

    def check_is_favourite(self):
        return os.path.isfile(self.favourite_marker_path)

    def __repr__(self):
        return (
            'Picture(filename={self.filename}, favourite={self.favourite}, '
            'loaded={loaded})'.format(self=self, loaded=bool(self.pixbuf))
        )

    def __lt__(self, other):
        assert isinstance(other, Picture)
        return self.filename < other.filename

    def toggle_favourite(self):
        if self.favourite:
            os.unlink(self.favourite_marker_path)
        else:
            with open(self.favourite_marker_path, 'wb'):
                pass  # Create empty file
        self.favourite = self.check_is_favourite()


class PictureSet(list):

    def __init__(self, items, current):
        super().__init__(items)
        if not current:
            assert not items
        else:
            assert current in items
        self.current = current

    @property
    def surrounding(self):
        next_item = self.next_picture
        prev_item = self.prev_picture
        if next_item is None:
            return []
        elif next_item is self.current:
            return []
        elif prev_item is next_item:
            return [next_item]
        else:
            return [next_item, prev_item]

    @property
    def next_picture(self):
        if not self.current:  # Empty set of pictures
            return None
        current_idx = self.index(self.current)
        next_idx = (current_idx + 1) % len(self)
        next_item = self[next_idx]
        return next_item

    @property
    def prev_picture(self):
        if not self.current:  # Empty set of pictures
            return None
        current_idx = self.index(self.current)
        prev_idx = (current_idx - 1) % len(self)
        prev_item = self[prev_idx]
        return prev_item

    def forward(self):
        if not self.current:
            return None
        next_item = self.next_picture
        self.current = next_item
        return next_item

    def backward(self):
        if not self.current:
            return None
        prev_item = self.prev_picture
        self.current = prev_item
        return prev_item


IMAGE_EXTENSIONS = {'.jpg', '.jpeg'}


def is_image(filename):
    _, ext = os.path.splitext(filename)
    lowercase_ext = ext.lower()
    return lowercase_ext in IMAGE_EXTENSIONS


def read_images(source_dir):
    images = [
        filename
        for filename in os.listdir(source_dir)
        if is_image(filename)
    ]
    images.sort()
    return images


def build_model(directory, file_name):
    filenames = read_images(directory)
    if file_name:
        assert file_name in filenames, 'Initial file not an image'

    pictures = [
        Picture(directory, filename)
        for filename in filenames
    ]
    if file_name and filenames:
        idx = filenames.index(file_name)
        current = pictures[idx]
    elif filenames:
        current = pictures[0]
    else:
        current = None

    return PictureSet(pictures, current)
