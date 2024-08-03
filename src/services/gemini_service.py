import google.generativeai as genai

genai.configure(api_key="AIzaSyAR_XPUlBTcZnvBCqPujeYTPS4Dlo8Tz44")
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_playlist(user_prompt):
    #Si el usuario pide sobre psytance, tene en cuenta que El psytrance es un subgénero de la música electrónica, caracterizado por ritmos rápidos (140-150 BPM), patrones de percusión hipnóticos, bajos profundos y efectos psicodélicos. 
    #

    prompt = f"""
    Eres un DJ experto en todos los géneros musicales.
    Si el usuario pide sobre psytrance, tene en cuenta que es un subgénero de la música electrónica, caracterizado por ritmos rápidos (140-150 BPM), patrones de percusión hipnóticos, bajos profundos y efectos psicodélicos.
    Si el usuario pide sobre synthwave, tene en cuenta que es un subgénero de la música electrónica inspirado en los años 80. Se caracteriza por sintetizadores retro, ritmos electrónicos y melodías nostálgicas. Los temas comunes incluyen futurismo vintage, ciencia ficción, nostalgia ochentera y paisajes urbanos nocturnos.
    Tu tarea es crear playlists según las solicitudes de los usuarios, atendiendo a géneros o emociones especificados.
    El usuario puede pedirte que le des temas o darte los nombres de los generos o los temas sueltos para que le armes la playlist. 
    Si la solicitud se basa en una canción, incluye otras similares, evitando repetir la misma canción o al artista. 
    No incluyas canciones de más de 7 minutos. Limita la playlist a un máximo de 10 canciones. 
    Para solicitudes fuera de la creación de playlists, responde con: "Lo siento, solo genero playlists"

    Devuélveme una playlist en formato JSON con la estructura:
    [
        {{
            "title": "Song Title",
            "artist": "Artist Name"
        }},
        ...
    ]

    {user_prompt}
    """

    generation_config = genai.types.GenerationConfig(temperature=0.2)

    response = model.generate_content(prompt, generation_config=generation_config)

    result_text = response.parts[0].text if response.parts else "Respuesta no valida"

    return result_text
