import os
import shutil

class FTService:
    def __init__(self):
        self.data_dir = os.path.abspath('data')

    def save(self, user_id, swtd_id, file):
        user_fp = os.path.join(self.data_dir, str(user_id))

        if not os.path.exists(user_fp):
            os.mkdir(user_fp)

        user_swtd_fp = os.path.join(user_fp, str(swtd_id))

        if not os.path.exists(user_swtd_fp):
            os.mkdir(user_swtd_fp)

        fp = os.path.join(user_swtd_fp, file.filename)

        file.save(fp)

    def delete(self, user_id, swtd_id):
        fp = os.path.join(self.data_dir, str(user_id), str(swtd_id))
        shutil.rmtree(fp)

    def get_file_type(self, filename):
        _, extension = os.path.splitext(filename)
        if extension.lower() == '.txt':
            return 'text/plain'
        elif extension.lower() in ['.jpg', '.jpeg']:
            return 'image/jpeg'
        elif extension.lower() == '.png':
            return 'image/png'
        elif extension.lower() == '.pdf':
            return 'application/pdf'
        else:
            return 'application/octet-stream'
