from flask import Blueprint, request, jsonify
from models import db, Contact
from flask_jwt_extended import jwt_required, get_jwt_identity

contact_bp = Blueprint('contact_bp', __name__)

@contact_bp.route('/contact', methods=['POST'])
@jwt_required()
def create_contact():
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')

    if not name:
        return jsonify({"message": "Name is required", "data": {}}), 400
    if not phone:
        return jsonify({"message": "Phone is required", "data": {}}), 400

    new_contact = Contact(
        name=name,
        email=data.get('email'),
        phone=phone,
        address=data.get('address'),
        country=data.get('country'),
        user_id=user_id
    )
    db.session.add(new_contact)
    db.session.commit()

    return jsonify({"message": "Contact added", "data": {
        "id": new_contact.id,
        "name": new_contact.name,
        "email": new_contact.email,
        "phone": new_contact.phone,
        "country": new_contact.country,
        "address": new_contact.address
    }}), 200

@contact_bp.route('/contact', methods=['GET'])
@jwt_required()
def list_contacts():
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('limit', 10, type=int)
    sort_by = request.args.get('sort_by', 'latest')
    name = request.args.get('name')
    email = request.args.get('email')
    phone = request.args.get('phone')

    query = Contact.query.filter_by(user_id=user_id)

    if name:
        query = query.filter(Contact.name.ilike(f"%{name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    if phone:
        query = query.filter(Contact.phone.ilike(f"%{phone}%"))

    if sort_by == 'latest':
        query = query.order_by(Contact.id.desc())
    elif sort_by == 'oldest':
        query = query.order_by(Contact.id.asc())
    elif sort_by == 'alphabetically_a_to_z':
        query = query.order_by(Contact.name.asc())
    elif sort_by == 'alphabetically_z_to_a':
        query = query.order_by(Contact.name.desc())

    contacts = query.paginate(page=page, per_page=per_page)

    return jsonify({
        "message": "Contact list",
        "data": {
            "list": [{"id": c.id, "name": c.name, "email": c.email, "phone": c.phone, "address": c.address, "country": c.country} for c in contacts.items],
            "has_next": contacts.has_next,
            "has_prev": contacts.has_prev,
            "page": contacts.page,
            "pages": contacts.pages,
            "per_page": contacts.per_page,
            "total": contacts.total
        }
    }), 200