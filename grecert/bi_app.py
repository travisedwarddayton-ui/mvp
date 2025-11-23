# ❌ INCORRECTO (causa el error)
coloraxis_colorbar=dict(
    title="Puntuación Verde",
    titlefont=dict(size=14)  # Esta estructura es incorrecta
)

# ✅ CORRECTO (versión fija)
coloraxis_colorbar=dict(
    title=dict(text="Puntuación Verde", font=dict(size=14))  # Estructura correcta
)
