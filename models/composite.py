from abc import ABC, abstractmethod

# models/composite.py
class ProgramaCartelera(ABC):
    @abstractmethod
    def mostrar_html(self) -> str:
        pass

class Funcion(ProgramaCartelera):
    def __init__(self, pelicula: str, hora: str, sala: str):
        self.pelicula = pelicula
        self.hora = hora
        self.sala = sala

    def mostrar_html(self) -> str:
        sala_id = self.sala.replace(" ", "_")
        return f"""
        <div class='funcion card mb-3'>
            <div class='card-body'>
                <h4 class='card-title'>{self.pelicula}</h4>
                <p class='card-text'>Sala: {self.sala} | Hora: {self.hora}</p>
                <a href='/sala/{sala_id}' class='btn btn-primary btn-comprar'>
                    Comprar
                </a>
            </div>
        </div>
        """

class DiaCartelera(ProgramaCartelera):
    def __init__(self, fecha: str):
        self.fecha = fecha
        self.items = []

    def agregar(self, item: ProgramaCartelera):
        self.items.append(item)

    def mostrar_html(self) -> str:
        html = f"<h3>🎬 Cartelera - {self.fecha}</h3>"
        for item in self.items:
            html += item.mostrar_html()
        return html