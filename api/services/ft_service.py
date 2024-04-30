import os

data_dir = os.path.abspath('data')

def save(user_id, swtd_id, filename, content):
    user_fp = os.path.join(data_dir, user_id)

    if not os.path.exists(user_fp):
        os.mkdir(user_fp)

    user_swtd_fp = os.path.join(user_fp, swtd_id)

    if not os.path.exists(user_swtd_fp):
        os.mkdir(user_swtd_fp)

    fp = os.path.join(user_swtd_fp, filename)

    with open(fp, 'w') as f:
        f.write(content)

def delete(user_id, swtd_id, filename):
    fp = os.path.join(data_dir, user_id, swtd_id, filename)
    os.remove(fp)
    