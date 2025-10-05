import google.generativeai as genai

genai.configure(api_key="YOUR API KEY")

model = genai.GenerativeModel('gemini-2.5-flash-lite')

def generar_precauciones(perfil, alteraciones):
    prompt = f'''
    Genera recomendaciones de salud personalizadas y directas basadas en el siguiente perfil de usuario {perfil} y las alteraciones ambientales enlistadas {alteraciones}. La respuesta debe ser únicamente la recomendación o alerta, formulada de manera clara, concisa y fácil de entender.

Si el tipo_usuario es "persona", la recomendación debe ser un consejo directo para ese individuo.

Si el tipo_usuario es "empresa", la recomendación debe enfocarse en acciones para proteger a sus empleados o a la comunidad afectada por sus operaciones.

Si el tipo_usuario es "gobierno", la recomendación debe ser una alerta de salud pública o acciones sugeridas para la comunidad.'''
    response = model.generate_content(prompt)   
    return response.text

if __name__ == "__main__":
    pass