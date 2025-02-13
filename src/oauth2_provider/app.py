from flask import Flask, request, jsonify, Blueprint, current_app


TOKEN_HEADER = 'Authorization'

NAME2SUB = {}
MAX_SUB = 3000


def get_new_sub():
    global MAX_SUB
    MAX_SUB += 1
    return MAX_SUB


def get_user_sub(*, username):
    if username in NAME2SUB:
        sub = NAME2SUB[username]
    else:
        sub = get_new_sub()
        NAME2SUB[username] = sub
    return sub


def create_app(app_config):
    app = Flask(__name__)
    app_config.setdefault('OAUTH2_USERS', {})
    for key, value in app_config.items():
        app.config[key] = value
    app.register_blueprint(introspection_bp, url_prefix='/rest/test-oauth2/')
    app.register_blueprint(user_profile_bp, url_prefix='/rest/test-oauth2/')
    return app


introspection_bp = Blueprint('rest_test_oauth2_introspection', __name__)
user_profile_bp = Blueprint('rest_test_oauth2_user_profile', __name__)


@introspection_bp.route('introspection', methods=['POST'])
def post():
    is_active = request.args.get('is_active', None)
    is_active = is_active is not None and is_active.lower() == 'true'

    access_token = request.form.get('token')
    result = {
        "active": is_active,
        "client_id": "VECGuQb00tWt8HZNkA4cxu6dnoQD5pF6Up3daAoK",
        "exp": 1568981517,
        "iat": 1568980917,
        'sub': get_user_sub(username=access_token),
        "token_type": "Bearer",
        "username": f"{access_token} {access_token}",
        "company.id": "20099"
    }
    return jsonify(result), 200


@user_profile_bp.route('user-profile', methods=['GET'])
def get():
    access_token = request.headers.get(TOKEN_HEADER).split(' ')[1]

    result = {
        "agreedToTermsOfUse": False,
        "comments": "",
        "companyId": "20099",
        "contactId": "20141",
        "createDate": 1557361648854,
        "defaultUser": False,
        "emailAddress": f"{access_token}@oauth2.org",
        "externalReferenceCode": "",
        "facebookId": "0",
        "failedLoginAttempts": 0,
        "firstName": f"{access_token}",
        "googleUserId": "",
        "graceLoginCount": 0,
        "greeting": "Welcome Test Test!",
        "jobTitle": "",
        "languageId": "en_US",
        "lastFailedLoginDate": None,
        "lastLoginDate": 1565768756360,
        "lastLoginIP": "172.19.0.1",
        "lastName": f"{access_token}",
        "ldapServerId": "-1",
        "lockout": False,
        "lockoutDate": None,
        "loginDate": 1568805421539,
        "loginIP": "172.18.0.1",
        "middleName": "",
        "modifiedDate": 1568805421548,
        "mvccVersion": "11",
        "openId": "",
        "portraitId": "0",
        "reminderQueryAnswer": "aa",
        "reminderQueryQuestion": "what-is-your-father's-middle-name",
        "screenName": f"{access_token}",
        "status": 0,
        "timeZoneId": "UTC",
        "userId": get_user_sub(username=access_token),
        "uuid": "4ef84411-749a-e617-6191-10e0c6a7147b",
        "FLASK_DEBUG": "1" if current_app.debug else '',
    }
    return jsonify(result), 200
