import os
import shutil


def prepare_download(root_dir):
    """
    Prepare Downloads folder for youtube_dl
    """

    downloads_path = os.path.join(root_dir, 'Downloads')
    if not os.path.exists(downloads_path):
        os.makedirs(downloads_path)
    else:
        for filename in os.listdir(downloads_path):
            file_path = os.path.join(downloads_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))
        os.chdir(downloads_path)