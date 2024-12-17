from marshmallow import Schema, fields

class CreateCommentSchema(Schema):
    message = fields.Str(required=True)
    author_id = fields.Int(required=True)
    swtd_id = fields.Int(required=True)

class UpdateCommentSchema(Schema):
    message = fields.Str(required=True)
