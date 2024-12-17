from marshmallow import Schema, fields

class RegistrationSchema(Schema):
    employee_id = fields.Str(required=True)
    email = fields.Email(required=True)
    firstname = fields.Str(required=True)
    lastname = fields.Str(required=True)
    password = fields.Str(required=True)
    department_id = fields.Int(required=False, missing=0)

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class AccountRecoverySchema(Schema):
    email = fields.Email(required=True)

class PasswordResetSchema(Schema):
    password = fields.Str(required=True)

class UpdateUserSchema(Schema):
    is_deleted = fields.Bool()
    password = fields.Str()
    employee_id = fields.Str()
    firstname = fields.Str()
    lastname = fields.Str()
    point_balance = fields.Float()
    is_ms_linked = fields.Bool()
    access_level = fields.Int()
    department_id = fields.Int()
