import os
import shutil

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

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
        
    def dump_to_pdf(self, data: list[dict[str, any]]) -> io.BytesIO:
        buffer = io.BytesIO()
        canvas = canvas.Canvas(buffer, pagesize=letter)
        canvas.setFont("Helvetica", 12)

        page_height = 792
        page_width = 612

        usable_width = page_width - left_margin + right_margin
        col_width = usable_width / len(data)

        # Define margins
        left_margin = 72
        right_margin = 72
        bottom_margin = 72
        top_margin = 72

        line_height = 24

        cursor = {
           "x_pos": left_margin,
           "y_pos":  page_height - top_margin
        }

        for key in data[0].keys():
            canvas.drawString(cursor['x_pos'], cursor['y_pos'], key)
            cursor['x_pos'] += col_width

        cursor['x_pos'] = left_margin

        for item in data:
            for _, value in item:
                if cursor['x_pos'] >= left_margin + usable_width:
                    cursor['x_pos'] = left_margin
                    cursor['y_pos'] += line_height

                canvas.drawString(cursor['x_pos'], cursor['y_pos'], value)
                cursor['x_pos'] += col_width

            cursor['x_pos'] -= line_height
            if cursor['x_pos'] <= bottom_margin:
                cursor['x_pos'] = page_height - top_margin
                canvas.showPage()

        canvas.save()
        
        buffer.seek(0)
        return buffer
