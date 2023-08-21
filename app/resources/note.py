from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

from db import db
from app.models import Note, Tag
from app.schamas import NoteSchema, NoteUpdateSchema

note_blp = Blueprint("Notes", "notes", description="Operations on notes")


@note_blp.route("/note/<int:note_id>")
class NoteResource(MethodView):
    @jwt_required()
    @note_blp.response(200, NoteSchema)
    def get(self, note_id):
        current_user = get_jwt_identity()
        note = Note.query.get_or_404(note_id)

        if note.user_id != current_user:
            abort(403, message="You are not authorized to access this note.")

        return note

    @jwt_required()
    def delete(self, note_id):
        current_user = get_jwt_identity()
        note = Note.query.get_or_404(note_id)

        # Check if the note belongs to the current user
        if note.user_id != current_user:
            abort(403, message="You are not authorized to delete this note.")

        db.session.delete(note)
        db.session.commit()
        return {"message": "Note deleted."}

    @jwt_required()
    @note_blp.arguments(NoteUpdateSchema)
    @note_blp.response(200, NoteSchema)
    def put(self, note_data, note_id):
        note = Note.query.get(note_id)
        current_user = get_jwt_identity()
        note = Note.query.get_or_404(note_id)

        # Check if the note belongs to the current user
        if note.user_id != current_user:
            abort(403, message="You are not authorized to update this note.")

        if note:
            note.title = note_data["title"]
            note.content = note_data["content"]
        else:
            note = Note(id=note_id, **note_data)

        db.session.add(note)
        db.session.commit()

        return note


@note_blp.route("/note")
class NoteList(MethodView):
    @jwt_required()
    @note_blp.arguments(NoteSchema)
    @note_blp.response(201, NoteSchema)
    def post(self, note_data):
        current_user = get_jwt_identity()
        note = Note(**note_data)

        # Check if the note belongs to the current user
        if note.user_id != current_user:
            abort(403, message="You are not authorized to update this note.")

        try:
            db.session.add(note)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the note.")

        return note

    @jwt_required()
    @note_blp.response(200, NoteSchema(many=True))
    def get(self, query_params):
        current_user = get_jwt_identity()

        page = query_params.get("page", 1, type=int)
        per_page = query_params.get("per_page", 10, type=int)
        sort_by = query_params.get("sort_by", "date")
        order = query_params.get("order", "desc")
        tag = query_params.get("tag")

        # Build the query based on the query parameters and user identity
        query = Note.query.join(Note.tags).filter(Note.user_id == current_user)

        if tag:
            query = query.filter(func.lower(Tag.name).ilike(f"%{tag.lower()}%"))

        if sort_by == "date":
            query = query.order_by(Note.date.desc() if order == "desc" else Note.date)
        elif sort_by == "title":
            query = query.order_by(Note.title.desc() if order == "desc" else Note.title)

        notes = query.paginate(page=page, per_page=per_page, error_out=False)
        note_schema = NoteSchema(many=True)
        return {
            "notes": note_schema.dump(notes.items),
            "page": notes.page,
            "per_page": notes.per_page,
            "total_pages": notes.pages,
            "total_notes": notes.total,
        }, 200
