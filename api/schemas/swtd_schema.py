from marshmallow import Schema, fields

class CreateSWTDSchema(Schema):
    title = fields.Str(required=True)
    venue = fields.Str(required=True)
    category = fields.Str(required=True)
    start_date = fields.Date(format="%m-%d-%Y", required=True)
    end_date = fields.Date(format="%m-%d-%Y", required=True)
    total_hours = fields.Float(required=True)
    points = fields.Float(required=True)
    benefits = fields.Str(required=True)
    term_id = fields.Int(required=True)

class UpdateSWTDScehma(Schema):
    is_deleted = fields.Bool()
    title = fields.Str()
    venue = fields.Str()
    category = fields.Str()
    start_date = fields.Date(format="%m-%d-%Y")
    end_date = fields.Date(format="%m-%d-%Y")
    total_hours = fields.Float()
    points = fields.Float()
    benefits = fields.Str()
    validation_status = fields.Str(missing="PENDING")
    validator_id = fields.Int()
    term_id = fields.Int()
