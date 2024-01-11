from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash

engine = create_engine("postgresql://fincasanfrancisco_user:S5Mywbfl6XanGYLXEVKel6ce5DYXnmOx@dpg-cmfjmqocmk4c739botlg-a.oregon-postgres.render.com/fincasanfrancisco")
db = scoped_session(sessionmaker(bind=engine))


with open("FincaCreacion.sql", 'r') as query:
  data = query.read()
  db.execute(data)

nombre = "Javier"
apellido = "Rizo"
usuario = (nombre[0]+apellido).lower()

db.execute(text(f"insert into usuario(nombre, apellido, usuario, hash, isAdmin, activo) values('{nombre}', '{apellido}', '{usuario}', '{generate_password_hash(usuario)}', 'true', 'true')"))


razas = ["Suindicos", "Brahman", "Simmental", "Charolais", "Limousin", "Hereford", "Angus", "Senepol", "Cebú", "Nelore", "Gyr"]
for raza in razas:
  db.execute(text(f"insert into raza(nombreRaza) values('{raza}')"))


origenes = ["Cria", "Comprado"]
for ori in origenes:
    db.execute(text(f"insert into origenganado(origen) values('{ori}')"))


estadoGanado = ["Disponible", "Vendido", "Muerto"]
for est in estadoGanado:
  db.execute(text(f"insert into estadoganado(estado) values('{est}')"))

tiposEntidad = ["Natural", "Juridica"]
for tipo in tiposEntidad:
  db.execute(text(f"INSERT INTO tipoentidad(tipoentidad) VALUES('{tipo}')"))


db.execute(text("""
INSERT INTO presentacion (tipomedicina, viaaplicacion, unidadmedida) VALUES
('Antibióticos', 'Oral', 'mg'),
('Antibióticos', 'Inyectable', 'mg'),
('Desparasitantes Internos', 'Oral', 'mg o ml'),
('Desparasitantes Externos', 'Tópica', 'ml'),
('Desparasitantes Externos', 'Baño', 'ml o kg'),
('Vitaminas y Minerales', 'Oral', 'mg'),
('Antiinflamatorios', 'Oral', 'mg'),
('Antiinflamatorios', 'Inyectable', 'mg'),
('Antipiréticos', 'Oral', 'mg'),
('Antialérgicos', 'Oral', 'mg'),
('Inmunomoduladores', 'Oral', 'mg'),
('Vacunas', 'Inyectable', 'ml'),
('Agentes Tópicos', 'Cutánea', 'mg o ml'),
('Rehidratantes y Electrolitos', 'Oral', 'ml'),
('Hormonas', 'Inyectable', 'ml'),
('Analgésicos', 'Oral', 'mg'),
('Analgésicos', 'Inyectable', 'mg'),
('Desinfectantes y Antisépticos', 'Tópica', 'ml'),
('Implantes', 'Subcutáneo', 'Unidades');
"""))


db.execute(text("""
INSERT INTO enfermedad (nombre, contagiosa) VALUES
('Fiebre Aftosa', true),
('Anaplasmosis', true),
('Brucelosis', true),
('Mastitis', true),
('Enfermedad de la Bursa Aviar (IBD)', true),
('Leptospirosis', true),
('Tuberculosis Bovina', true),
('Campylobacteriosis', true),
('Clostridiosis', false),
('Enterotoxemia (Ovine Progressive Pneumonia)', false),
('Hemoglobinuria Bacilar', true),
('Hepatitis Infecciosa Bovina (BHV-1)', true),
('Peste Bovina', true),
('Rinotraqueítis Infecciosa Bovina (IBR)', true),
('Salmonelosis', true),
('Theileriosis', true),
('Tristeza Parasitaria Bovina (TPB)', true),
('Virus de la Diarrea Viral Bovina (BVDV)', true),
('Hiperqueratosis de la Pezuña', false),
('Hemorragia Viral de Bovinos (EVB)', true),
('Enfermedad Respiratoria Bovina (BRD)', true),
('Fascioliasis', true),
('Cisticercosis', false),
('Enfermedad de las Clostridias', false),
('Coprofagia', false),
('Coccidiosis', true),
('Dermatitis Digital', false),
('Encefalopatía Espongiforme Bovina (EEB)', true),
('Estomatitis Vesicular', true),
('Histomoniasis', true),
('Nematodiasis', true),
('Piroplasmosis', true),
('Sarna Bovina', true),
('Toxoplasmosis', true),
('Urolitiasis', false),
('Viruela Bovina', true),
('Enfermedad de los Ojos Blancos', true),
('Babesiosis', true),
('Neosporosis', true),
('Actinobacilosis', true);
"""))



db.commit()
print("Exito")



"""xd = db.execute(text("select * from usuario"))
for item in xd:
    print(item)"""


