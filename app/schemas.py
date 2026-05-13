from app.extensions import ma
from app.models import User, Document, Appeal, Webinar, MasterClass, Test, Survey, Certificate

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        exclude = ('password_hash',)

class DocumentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Document

class AppealSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Appeal

class WebinarSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Webinar

class MasterClassSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MasterClass
        include_relationships = True

class TestSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Test

class CertificateSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Certificate

class SurveySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Survey