from datetime import datetime
from extensions import db


class Conversion(db.Model):
    __tablename__ = "conversions"

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type          = db.Column(db.Enum("html_to_react", "css_to_tailwind"), nullable=False)
    input_code    = db.Column(db.Text(4294967295), nullable=False)
    output_code   = db.Column(db.Text(4294967295), nullable=False)
    output_format = db.Column(db.Enum("single", "merged", "zip"), nullable=False, default="single")
    filename      = db.Column(db.String(255))
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":            self.id,
            "type":          self.type,
            "input_code":    self.input_code,
            "output_code":   self.output_code,
            "output_format": self.output_format,
            "filename":      self.filename,
            "created_at":    self.created_at.isoformat() if self.created_at else None,
        }
