from marshmallow import Schema, fields

class CreateDepartmentSchema(Schema):
    name = fields.Str(required=True)
    required_points = fields.Float(required=True)
    level = fields.Str(required=True)
    midyear_points = fields.Float(required=True)
    use_schoolyear = fields.Bool(required=True)

class UpdateDepartmentSchema(Schema):
    is_deleted = fields.Bool()
    name = fields.Str()
    required_points = fields.Float()
    midyear_points = fields.Float()
    use_schoolyear = fields.Bool()
    head_id = fields.Int()
    level = fields.Str()
