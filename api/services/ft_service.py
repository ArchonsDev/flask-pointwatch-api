import os
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import shutil
import io

from ..models.user import User
from ..services.term_service import TermService

class FTService:
    def __init__(self, term_service, clearing_service, user_service):
        self.data_dir = os.path.abspath('data')
        self.term_service = term_service
        self.clearing_service = clearing_service
        self.user_service = user_service

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
        
    def dump_user_swtd_data(self, requester: User, user: User) -> io.BytesIO:
        buffer = io.BytesIO()

        # Define page dimensions
        height, width = [792, 612]

        # Define font
        font_family = "Helvetica"
        font_size = 12
        line_height = font_size * 1.2

        # Define page margins
        margin_top, margin_right, margin_bottom, margin_left = [72, 72, 72, 72]

        c = canvas.Canvas(buffer, pagesize=letter)
        c.setTitle(f"{user.employee_id}_SWTDReport")
        c.setFont(font_family, font_size)

        term_ids = list({form.term_id for form in user.swtd_forms})
        terms = [self.term_service.get_term(id) for id in term_ids]

        for term in terms:
            cursor = {'x': margin_left, 'y': height - margin_top}

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'], "PointWatch: Employee Seminars, Workshops, Trainings, and Development Report")
            c.setFont(font_family, font_size)

            cursor['y'] -= line_height

            c.line(margin_left, cursor['y'], width-margin_left, cursor['y'])

            cursor['y'] -= line_height

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'],'Date & Time')
            c.setFont(font_family, font_size)

            c.drawString(cursor['x'] + width / 6, cursor['y'], f': {datetime.now().strftime('%m-%d-%Y %I:%M %p')}')

            cursor['y'] -= line_height

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'],'Generated by: ')
            c.setFont(font_family, font_size)

            c.drawString(cursor['x'] + width / 6, cursor['y'], f': {requester.employee_id} | {requester.lastname}, {requester.firstname}')

            cursor['y'] -= line_height

            c.line(margin_left, cursor['y'], width-margin_left, cursor['y'])

            cursor['y'] -= line_height

            x = cursor['x']
            y = cursor['y']

            text = c.beginText(x, y)
            text.setFont(font_family + "-Bold", font_size)
            text.textLine('ID No.')
            text.textLine('Name')
            text.textLine('Email')
            text.textLine('Department')
            text.textLine('Available Points')
            c.setFont(font_family, font_size)
            c.drawText(text)

            x = cursor['x'] + width / 6
            y = cursor['y']

            text = c.beginText(x, y)
            text.textLine(f': {user.employee_id}')
            text.textLine(f': {user.lastname}, {user.firstname}')
            text.textLine(f': {user.email}')
            text.textLine(f': {user.department}')
            text.textLine(f': {user.point_balance}')
            c.setFont(font_family, font_size)
            c.drawText(text)

            cursor['y'] -= line_height * 5

            c.line(margin_left, cursor['y'], width-margin_left, cursor['y'])

            cursor['y'] -= line_height

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'],'Term')
            c.setFont(font_family, font_size)

            c.drawString(cursor['x'] + width / 15, cursor['y'], f': {term.name} ({term.start_date.strftime('%m-%d-%Y')} to {term.end_date.strftime('%m-%d-%Y')})')

            cursor['y'] -= line_height

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'],'Status')
            c.setFont(font_family, font_size)

            is_cleared = self.clearing_service.get_user_term_clearing(user.id, term.id)
            c.drawString(cursor['x'] + width / 15, cursor['y'], f': {"CLEARED" if is_cleared else "NOT CLEARED"}')

            cursor['y'] -= line_height * 2

            points = self.user_service.get_point_summary(user, term)
            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'],'Valid Points')
            c.setFont(font_family, font_size)

            c.drawString(cursor['x'] + width / 6, cursor['y'], f': {points.valid_points}')

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'] + width / 3, cursor['y'],'Required Points')
            c.setFont(font_family, font_size)

            c.drawString(cursor['x'] + width / 3 + width / 6, cursor['y'], f': {points.required_points}')

            cursor['y'] -= line_height

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'],'Invalid Points')
            c.setFont(font_family, font_size)

            c.drawString(cursor['x'] + width / 6, cursor['y'], f': {points.invalid_points}')

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'] + width / 3, cursor['y'],'Lacking Points')
            c.setFont(font_family, font_size)

            c.drawString(cursor['x'] + width / 3 + width / 6, cursor['y'], f': {points.lacking_points}')

            cursor['y'] -= line_height

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'],'Pending Points')
            c.setFont(font_family, font_size)

            c.drawString(cursor['x'] + width / 6, cursor['y'], f': {points.pending_points}')

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'] + width / 3, cursor['y'],'Excess Points')
            c.setFont(font_family, font_size)

            c.drawString(cursor['x'] + width / 3 + width / 6, cursor['y'], f': {points.excess_points}')

            cursor['y'] -= line_height * 2

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'], 'Title')
            c.drawString(cursor['x'] + width / 1.8, cursor['y'], 'Points')
            c.drawString(cursor['x'] + width / 1.55, cursor['y'], 'Status')
            c.setFont(font_family, font_size)

            swtd_forms = filter(lambda form: form.author_id == user.id, term.swtd_forms)

            cursor['y'] -= line_height

            for form in swtd_forms:
                c.drawString(cursor['x'], cursor['y'], f'{form.title[:39]}{"..." if len(form.title) > 39 else ""}')
                c.drawString(cursor['x'] + width / 1.8, cursor['y'], str(form.points))
                c.drawString(cursor['x'] + width / 1.55, cursor['y'], str(form.validation.status))

                cursor['y'] -= line_height

            c.showPage()

        c.save()
        
        buffer.seek(0)
        return buffer

    def dump_staff_validation_data(self, requester: User, user: User) -> io.BytesIO:
        buffer = io.BytesIO()

        # Define page dimensions
        height, width = [792, 612]

        # Define font
        font_family = "Helvetica"
        font_size = 12
        line_height = font_size * 1.2

        # Define page margins
        margin_top, margin_right, margin_bottom, margin_left = [72, 72, 72, 72]

        c = canvas.Canvas(buffer, pagesize=letter)
        c.setTitle(f"{user.employee_id}_ValidationReport")
        c.setFont(font_family, font_size)

        term_ids = list({validation.form.term_id for validation in user.validated_forms})
        terms = [self.term_service.get_term(id) for id in term_ids]

        for term in terms:
            cursor = {'x': margin_left, 'y': height - margin_top}

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'], "PointWatch: Staff Validation Report")
            c.setFont(font_family, font_size)

            cursor['y'] -= line_height

            c.line(margin_left, cursor['y'], width-margin_left, cursor['y'])

            cursor['y'] -= line_height

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'],'Date & Time')
            c.setFont(font_family, font_size)

            c.drawString(cursor['x'] + width / 6, cursor['y'], f': {datetime.now().strftime('%m-%d-%Y %I:%M %p')}')

            cursor['y'] -= line_height

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'],'Generated by: ')
            c.setFont(font_family, font_size)

            c.drawString(cursor['x'] + width / 6, cursor['y'], f': {requester.employee_id} | {requester.lastname}, {requester.firstname}')

            cursor['y'] -= line_height

            c.line(margin_left, cursor['y'], width-margin_left, cursor['y'])

            cursor['y'] -= line_height

            x = cursor['x']
            y = cursor['y']

            text = c.beginText(x, y)
            text.setFont(font_family + "-Bold", font_size)
            text.textLine('ID No.')
            text.textLine('Name')
            text.textLine('Email')
            text.textLine('Department')
            c.setFont(font_family, font_size)
            c.drawText(text)

            x = cursor['x'] + width / 6
            y = cursor['y']

            text = c.beginText(x, y)
            text.textLine(f': {user.employee_id}')
            text.textLine(f': {user.lastname}, {user.firstname}')
            text.textLine(f': {user.email}')
            text.textLine(f': {user.department}')
            c.setFont(font_family, font_size)
            c.drawText(text)

            cursor['y'] -= line_height * 4

            c.line(margin_left, cursor['y'], width-margin_left, cursor['y'])

            cursor['y'] -= line_height

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'],'Term')
            c.setFont(font_family, font_size)

            c.drawString(cursor['x'] + width / 15, cursor['y'], f': {term.name} ({term.start_date.strftime('%m-%d-%Y')} to {term.end_date.strftime('%m-%d-%Y')})')

            cursor['y'] -= line_height * 2

            swtd_forms = list(filter(lambda form: form.validation.validator_id == user.id, term.swtd_forms))
            approved_ctr = 0
            rejected_ctr = 0

            for form in swtd_forms:
                if form.validation.status == 'APPROVED': approved_ctr += 1
                if form.validation.status == 'REJECTED': rejected_ctr += 1

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'],'Approved SWTDs')
            c.setFont(font_family, font_size)

            c.drawString(cursor['x'] + width / 6, cursor['y'], f': {approved_ctr}')

            cursor['y'] -= line_height

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'],'Rejected SWTDs')
            c.setFont(font_family, font_size)

            c.drawString(cursor['x'] + width / 6, cursor['y'], f': {rejected_ctr}')

            cursor['y'] -= line_height * 2

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'], 'SWTD ID')
            c.drawString(cursor['x'] + width / 6, cursor['y'], 'Author')
            c.drawString(cursor['x'] + width / 2.5, cursor['y'], 'Date')
            c.drawString(cursor['x'] + width / 1.55, cursor['y'], 'Action')
            c.setFont(font_family, font_size)

            cursor['y'] -= line_height

            for form in swtd_forms:
                c.drawString(cursor['x'], cursor['y'], str(form.id))
                c.drawString(cursor['x'] + width / 6, cursor['y'], f'{form.author.lastname}, {form.author.firstname}')
                c.drawString(cursor['x'] + width / 2.5, cursor['y'], form.validation.validated_on.strftime('%m-%d-%Y %I:%M %p'))
                c.drawString(cursor['x'] + width / 1.55, cursor['y'], str(form.validation.status))

                cursor['y'] -= line_height

            c.showPage()

        c.save()
        
        buffer.seek(0)
        return buffer

    def dump_admin_clearing_data(self, requester: User, user: User) -> io.BytesIO:
        buffer = io.BytesIO()

        # Define page dimensions
        height, width = [792, 612]

        # Define font
        font_family = "Helvetica"
        font_size = 12
        line_height = font_size * 1.2

        # Define page margins
        margin_top, margin_right, margin_bottom, margin_left = [72, 72, 72, 72]

        c = canvas.Canvas(buffer, pagesize=letter)
        c.setTitle(f"{user.employee_id}_AdminReport")
        c.setFont(font_family, font_size)

        cursor = {'x': margin_left, 'y': height - margin_top}

        clearings = self.clearing_service.get_clearing_by_clearer_id(user.id)
        users = [self.user_service.get_user(id=clearing.user_id) for clearing in clearings]
        term_ids = list({clearing.term_id for clearing in clearings})
        terms = [self.term_service.get_term(id) for id in term_ids]

        for term in terms:
            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'], "PointWatch: Admin Term Clearing Report")
            c.setFont(font_family, font_size)

            cursor['y'] -= line_height

            c.line(margin_left, cursor['y'], width-margin_left, cursor['y'])

            cursor['y'] -= line_height

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'],'Date & Time')
            c.setFont(font_family, font_size)

            c.drawString(cursor['x'] + width / 6, cursor['y'], f': {datetime.now().strftime('%m-%d-%Y %I:%M %p')}')

            cursor['y'] -= line_height

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'],'Generated by: ')
            c.setFont(font_family, font_size)

            c.drawString(cursor['x'] + width / 6, cursor['y'], f': {requester.employee_id} | {requester.lastname}, {requester.firstname}')

            cursor['y'] -= line_height

            c.line(margin_left, cursor['y'], width-margin_left, cursor['y'])

            cursor['y'] -= line_height

            x = cursor['x']
            y = cursor['y']

            text = c.beginText(x, y)
            text.setFont(font_family + "-Bold", font_size)
            text.textLine('ID No.')
            text.textLine('Name')
            text.textLine('Email')
            text.textLine('Department')
            c.setFont(font_family, font_size)
            c.drawText(text)

            x = cursor['x'] + width / 6
            y = cursor['y']

            text = c.beginText(x, y)
            text.textLine(f': {user.employee_id}')
            text.textLine(f': {user.lastname}, {user.firstname}')
            text.textLine(f': {user.email}')
            text.textLine(f': {user.department}')
            c.setFont(font_family, font_size)
            c.drawText(text)

            cursor['y'] -= line_height * 4

            c.line(margin_left, cursor['y'], width-margin_left, cursor['y'])

            cursor['y'] -= line_height

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'],'Term')
            c.setFont(font_family, font_size)

            c.drawString(cursor['x'] + width / 15, cursor['y'], f': {term.name} ({term.start_date.strftime('%m-%d-%Y')} to {term.end_date.strftime('%m-%d-%Y')})')

            cursor['y'] -= line_height * 2

            c.setFont(font_family + "-Bold", font_size)
            c.drawString(cursor['x'], cursor['y'], 'ID No.')
            c.drawString(cursor['x'] + width / 7, cursor['y'], 'Name')
            c.drawString(cursor['x'] + width / 2.5, cursor['y'], 'Department')
            c.drawString(cursor['x'] + width / 1.8, cursor['y'], 'Date Cleared')
            c.setFont(font_family, font_size)

            cursor['y'] -= line_height

            for user in users:
                clearing = self.clearing_service.get_user_term_clearing(user.id, term.id)

                c.drawString(cursor['x'], cursor['y'], f'{user.employee_id}')
                c.drawString(cursor['x'] + width / 7, cursor['y'], f'{user.lastname}, {user.firstname}')
                c.drawString(cursor['x'] + width / 2.5, cursor['y'], f'{user.department}')
                c.drawString(cursor['x'] + width / 1.8, cursor['y'], f'{clearing.date_cleared.strftime('%m-%d-%Y %I:%M %p')}')

                cursor['y'] -= line_height

            c.showPage()

        c.save()

        buffer.seek(0)  
        return buffer
