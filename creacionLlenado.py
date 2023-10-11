from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash

engine = create_engine("postgresql://finca_w3np_user:c1W9vy5mfQt9hq22T33nJgeHVwVHZxjl@dpg-ckj6gggmccbs73e45m90-a.oregon-postgres.render.com/finca_w3np")
db = scoped_session(sessionmaker(bind=engine))


with open("FincaCreacion.sql", 'r') as query:
  data = query.read()
  db.execute(data)

nombre = "Javier"
apellido = "Rizo"
usuario = (nombre[0]+apellido).lower()

db.execute(text(f"insert into usuario(nombre, apellido, usuario, hash, isAdmin) values('{nombre}', '{apellido}', '{usuario}', '{generate_password_hash(usuario)}', 'true')"))
db.commit()

print("Exito")


"""xd = db.execute(text("select * from usuario"))
for item in xd:
    print(item)"""


