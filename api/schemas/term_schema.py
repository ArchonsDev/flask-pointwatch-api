from marshmallow import Schema, fields

class CreateTermSchema(Schema):
    name = fields.Str(required=True)
    start_date = fields.Date(format="%m-%d-%Y", required=True)
    end_date = fields.Date(format="%m-%d-%Y", required=True)
    type = fields.Str(required=True)

class UpdateTermSchema(Schema):
    is_deleted = fields.Bool()
    name = fields.Str()
    start_date = fields.Date(format="%m-%d-%Y")
    end_date = fields.Date(format="%m-%d-%Y")
    type = fields.Str()
