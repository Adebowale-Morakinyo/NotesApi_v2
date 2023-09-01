from marshmallow import Schema, fields, validate, ValidationError

v_error = ValidationError


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class TagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)


class NoteSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    content = fields.Str(required=True)
    date = fields.DateTime(dump_only=True)
    user_id = fields.Int(required=True, load_only=True)
    user = fields.Nested(UserSchema(), dump_only=True)
    tags = fields.Nested(TagSchema(), many=True, dump_only=True)


class NoteUpdateSchema(Schema):
    title = fields.Str()
    content = fields.Str()


class NoteListSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    content = fields.Str()
    date = fields.DateTime()
    user_id = fields.Int()
    user = fields.Nested(UserSchema())


class NoteListResponseSchema(Schema):
    notes = fields.List(fields.Nested(NoteListSchema))
    page = fields.Int()
    per_page = fields.Int()
    total_pages = fields.Int()
    total_notes = fields.Int()


class NoteListQuerySchema(Schema):
    page = fields.Int(required=False)
    per_page = fields.Int(required=False)
    sort_by = fields.Str(required=False)
    order = fields.Str(required=False)
    tag = fields.Str(required=False)


class NoteTagSchema(Schema):
    message = fields.Str()
    note_id = fields.Int(required=True, load_only=True)
    tag_id = fields.Int(required=True, load_only=True)


class UserNoteSchema(Schema):
    user_id = fields.Int(required=True, load_only=True)
    note_id = fields.Int(required=True, load_only=True)


class UserRegistrationSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))


class UserLoginResponseSchema(Schema):
    access_token = fields.Str()


class UserProfileSchema(Schema):
    username = fields.Str(dump_only=True)
    email = fields.Email(dump_only=True)
    full_name = fields.Str(required=True)
    profile_picture = fields.Str()  # Field for profile picture URL
    bio = fields.Str()


class ShareViaEmailSchema(Schema):
    email = fields.Email(required=True)


class TagAutocompleteSchema(Schema):
    query = fields.Str(required=True)


class TagAutocompleteResponseSchema(Schema):
    tags = fields.List(fields.Str())
