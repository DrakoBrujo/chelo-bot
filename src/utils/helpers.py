def get_command_list():
    commands = [
        {"nombre": "!play", "descripcion": "Reproduce una canción a partir de una consulta"},
        {"nombre": "!stop", "descripcion": "Detiene la reproducción de música y vacía la lista de reproducción"},
        {"nombre": "!skip", "descripcion": "Salta la canción actual"},
        {"nombre": "!current", "descripcion": "Muestra información sobre la canción que se está reproduciendo actualmente"},
        {"nombre": "!pey", "descripcion": "Muestra las canciones en la lista de reproducción"},
        {"nombre": "!info", "descripcion": "Muestra información sobre los comandos disponibles"},
        {"nombre": "!gnt", "descripcion": "Genera una peylist con IA a partir de una consulta ✨✨✨"},
        {"nombre": "!remove", "descripcion": "Elimina una cancion de la peylist"}
    ]
    return commands
