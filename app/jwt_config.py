from flask_jwt_extended import JWTManager
from .shared.mongodb import collection

def configure_jwt(app):
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        mongodb = collection('revoked_tokens')
        jti = jwt_payload["jti"]
        token = mongodb.find_one({"jti": jti})
        return token is not None