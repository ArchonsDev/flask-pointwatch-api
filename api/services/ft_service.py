import os
import shutil

data_dir = os.path.abspath('data')

def save(user_id, swtd_id, file):
    user_fp = os.path.join(data_dir, str(user_id))

    if not os.path.exists(user_fp):
        os.mkdir(user_fp)

    user_swtd_fp = os.path.join(user_fp, str(swtd_id))

    if not os.path.exists(user_swtd_fp):
        os.mkdir(user_swtd_fp)

    fp = os.path.join(user_swtd_fp, file.filename)

    file.save(fp)

def delete(user_id, swtd_id):
    fp = os.path.join(data_dir, str(user_id), str(swtd_id))
    shutil.rmtree(fp)
    