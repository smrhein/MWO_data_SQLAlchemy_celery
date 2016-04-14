import sqlalchemy as sqla
import datetime
import pytz

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import class_mapper

db_file = '/home/rhein/git/vims/mwo/src/mwo/mapdata/{}.sqlite'.format('mwo.mapdata.models') 
engine = sqla.create_engine('sqlite:///{}'.format(db_file), echo=False)
Base = declarative_base(engine)

def datetime2timestamp(dt):
    return (dt - datetime.datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()

class CodedBlob(sqla.TypeDecorator):
    impl = sqla.types.BLOB
    def __init__(self, codec):
        super(CodedBlob, self).__init__()
        self._codec = codec
    def process_bind_param(self, value, dialect):
        if value is not None:
            value = self._codec.encode(value)[0]
        return value
    def process_result_value(self, value, dialect):
        if value is not None:
            value = self._codec.decode(value)[0]
        return value

def sync(session, model, **kwargs):
    primary_keys = tuple(pk.name for pk in class_mapper(model).primary_key)
    instance = session.query(model).filter_by(**{name:kwargs[name] for name in primary_keys}).first()
    if instance:
        if not session.query(model).filter_by(**kwargs).first():
            for name, value in kwargs.iteritems():
                setattr(instance, name, value)
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        return instance

class Unit(Base):
    __tablename__ = 'units'
    id = sqla.Column(sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.String, nullable=False, unique=True)
     
class Faction(Base):
    __tablename__ = 'factions'
    id = sqla.Column(sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.String, nullable=False, unique=True)
    icon = sqla.Column(sqla.String, nullable=False, unique=True)
     
class Planet(Base):
    __tablename__ = 'planets'
    id = sqla.Column(sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.String, nullable=False)
    position_x = sqla.Column(sqla.Integer, nullable=False)
    position_y = sqla.Column(sqla.Integer, nullable=False)    
     
class StatusUpdate(Base):
    __tablename__ = 'statusupdates'
    datetime_generated = sqla.Column(sqla.Integer, primary_key=True)
    planet_id = sqla.Column(sqla.ForeignKey('planets.id'), primary_key=True)
    contested = sqla.Column(sqla.Boolean, nullable=False)
    total_territories = sqla.Column(sqla.Integer, nullable=False)
    min_tonnage = sqla.Column(sqla.Integer, nullable=False)
    max_tonnage = sqla.Column(sqla.Integer, nullable=False)
    dropship = sqla.Column(sqla.Integer, nullable=False)
    defense_level = sqla.Column(sqla.Integer, nullable=False)
    owner_id = sqla.Column(sqla.ForeignKey('factions.id'), nullable=False)
    unit_id = sqla.Column(sqla.ForeignKey('units.id'), nullable=False)
    invading_id = sqla.Column(sqla.ForeignKey('factions.id'), nullable=False)
    
def main():
#     import sadisplay

    Base.metadata.drop_all()
    Base.metadata.create_all()
    
#     desc = sadisplay.describe([Faction, Planet, StatusUpdate, Unit])
#     with open('tmp.dot', 'w') as fp:
#         fp.write(sadisplay.dot(desc))
    

if __name__ == '__main__':
    main()
