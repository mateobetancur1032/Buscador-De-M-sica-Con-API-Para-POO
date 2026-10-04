# Importamos Flask para crear la aplicación web y manejar las rutas,
# render_template para conectar con el HTML, y request para recibir datos del formulario.
from flask import Flask, render_template, request
import requests  # Librería para hacer peticiones HTTP a la API externa de Deezer

# Inicializamos la aplicación web con Flask
app = Flask(__name__)


class Track:
#La clase Track representa una canción individual obtenida de la API
# Se utiliza doble _ para que los datos sean privados y no puedan ser modificados directamente desde fuera de la clase.
  def __init__(self, title, duration, artist_name, album_title, preview_url):
    self.__title = title
    self.__duration = duration  # Viene en segundos
    self.__artist_name = artist_name
    self.__album_title = album_title
    self.__preview_url = preview_url

  #(@property)permite acceder al atributo privado (self.__title) desde fuera de la clase
  @property
  def title(self):
    return self.__title


  @property
  def duration_formatted(self):
    #Convierte los segundos de la API a un formato de minutos y segundos (ej. 3:45)
    mins = self.__duration // 60
    secs = self.__duration % 60
    return f"{mins}:{secs:02d}"


  @property
  def artist_name(self):
    return self.__artist_name


  @property
  def album_title(self):
    return self.__album_title

  @property
  def preview_url(self):
    return self.__preview_url

  def to_dict(self):
    #Método de apoyo (Serialización).Convierte los datos privados del objeto en un diccionario estándar de Python. Flask lo necesita para poder empaquetarlos y enviarlos con éxito hacia la interfaz web (HTML).
    return {
        "title": self.__title,
        "duration": self.duration_formatted,  # Usamos la propiedad calculada
        "artist": self.__artist_name,
        "album": self.__album_title,
        "preview": self.__preview_url,
    }

class MusicApiService:
  
  #Esta clase se encarga únicamente de la comunicación con el servidor y de transformar la respuesta en objetos limpios de la clase Track.


  BASE_URL = "https://api.deezer.com/search?q="
  #Almacena la URL base de la API de Deezer para búsquedas


  @staticmethod  # Método estático: No necesita instanciar la clase para usarse.
  def search_tracks(query):
    #Realiza la petición HTTP GET a la API utilizando lo que el usuario escribió en el buscador.
    
    url = f"{MusicApiService.BASE_URL}{query.strip()}"
    # Construimos la URL final combinando la dirección base de la API y el texto de búsqueda del usuario.
    
    try:
      # Hacemos la consulta web con un límite de tiempo de espera de 5s
      response = requests.get(url, timeout=5)

      # Verificamos si la API respondió correctamente (Código HTTP 200)
      if response.status_code == 200:
        data = response.json()  # Convertimos la respuesta cruda en JSON (diccionario)
        tracks_data = data.get("data", [])

        track_list = []
        # Recorremos cada resultado crudo y lo transformamos en un Objeto "Track" (POO)
        for item in tracks_data:
          track = Track(
              title=item["title"],
              duration=item["duration"],
              artist_name=item["artist"]["name"],
              album_title=item["album"]["title"],
              preview_url=item.get("preview", ""),
          )
          track_list.append(track)  # Guardamos el objeto en la lista
        return track_list

      return []  # Retorna lista vacía si la API falla en el status code
    except requests.exceptions.RequestException:
      # Si hay un error de red (sin internet, caídas de servidor), evitamos que la app colapse
      return []

@app.route("/", methods=["GET", "POST"])
def index():
#Ruta principal de la aplicación web.

  tracks = []
  query = ""

  # Si el usuario hace clic en el botón "Buscar" (método POST del formulario)
  if request.method == "POST":
    query = request.form.get("query", "")
    if query:
      # 1. Llamamos al servicio para consumir la API y obtener los objetos
      track_objs = MusicApiService.search_tracks(query)

      # 2. Convertimos la lista de objetos a diccionarios para que el HTML los pinte
      tracks = [t.to_dict() for t in track_objs]

  # Renderizamos el archivo index.html enviándole los resultados obtenidos
  return render_template("index.html", tracks=tracks, query=query)

if __name__ == "__main__":
  # Inicia el servidor local de desarrollo de Flask en modo depuración (debug)
  app.run(debug=True)