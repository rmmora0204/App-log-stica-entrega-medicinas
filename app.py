import streamlit as st
import pandas as pd
import numpy as np
from itertools import combinations
from math import radians, sin, cos, sqrt, atan2

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="MediUbica - Dispensarios",
    page_icon="💊",
    layout="wide",
)

# ─────────────────────────────────────────────
# DATOS SIMULADOS
# ─────────────────────────────────────────────

# Catálogo maestro de medicamentos
CATALOGO_MEDICAMENTOS = [
    "Acetaminofén 500mg",
    "Ibuprofeno 400mg",
    "Losartán 50mg",
    "Metformina 850mg",
    "Omeprazol 20mg",
    "Enalapril 20mg",
    "Atorvastatina 40mg",
    "Amlodipino 5mg",
    "Levotiroxina 50mcg",
    "Metoprolol 50mg",
    "Fluoxetina 20mg",
    "Diclofenaco 50mg",
    "Amoxicilina 500mg",
    "Ciprofloxacino 500mg",
    "Insulina Glargina",
    "Salbutamol Inhalador",
    "Loratadina 10mg",
    "Ranitidina 150mg",
    "Clonazepam 2mg",
    "Hidroclorotiazida 25mg",
]

# Dispensarios con coordenadas (lat, lon) en una ciudad simulada (Bogotá aprox.)
DISPENSARIOS = {
    "Dispensario Central - Sede Norte": {
        "lat": 4.7110,
        "lon": -74.0721,
        "tiempo_atencion_min": 15,
        "horario": "7:00 AM - 5:00 PM",
        "direccion": "Calle 100 #15-20",
        "telefono": "(601) 555-0101",
    },
    "Dispensario Clínica del Sur": {
        "lat": 4.5981,
        "lon": -74.0760,
        "tiempo_atencion_min": 25,
        "horario": "7:00 AM - 4:00 PM",
        "direccion": "Carrera 30 #45-10",
        "telefono": "(601) 555-0102",
    },
    "Dispensario Hospital de Occidente": {
        "lat": 4.6486,
        "lon": -74.1180,
        "tiempo_atencion_min": 20,
        "horario": "8:00 AM - 6:00 PM",
        "direccion": "Avenida 68 #22-15",
        "telefono": "(601) 555-0103",
    },
    "Farmacia Clínica Oriental": {
        "lat": 4.6580,
        "lon": -74.0400,
        "tiempo_atencion_min": 10,
        "horario": "6:00 AM - 8:00 PM",
        "direccion": "Carrera 7 #60-30",
        "telefono": "(601) 555-0104",
    },
    "Dispensario Universitario": {
        "lat": 4.6350,
        "lon": -74.0830,
        "tiempo_atencion_min": 30,
        "horario": "7:30 AM - 3:30 PM",
        "direccion": "Calle 45 #26-85",
        "telefono": "(601) 555-0105",
    },
    "Punto de Entrega Norte Express": {
        "lat": 4.7320,
        "lon": -74.0550,
        "tiempo_atencion_min": 8,
        "horario": "6:00 AM - 9:00 PM",
        "direccion": "Calle 127 #10-45",
        "telefono": "(601) 555-0106",
    },
}

# Generar inventario simulado (reproducible)
np.random.seed(42)
INVENTARIO = {}
for disp in DISPENSARIOS:
    disponibles = np.random.choice(
        [True, False], size=len(CATALOGO_MEDICAMENTOS), p=[0.75, 0.25]
    )
    INVENTARIO[disp] = {
        med: bool(disp_val)
        for med, disp_val in zip(CATALOGO_MEDICAMENTOS, disponibles)
    }


# ─────────────────────────────────────────────
# FUNCIONES AUXILIARES
# ─────────────────────────────────────────────


def haversine(lat1, lon1, lat2, lon2):
    """Calcula la distancia en km entre dos puntos geográficos."""
    R = 6371  # Radio de la Tierra en km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def calcular_distancia(lat_pac, lon_pac, nombre_dispensario):
    """Distancia del paciente a un dispensario."""
    d = DISPENSARIOS[nombre_dispensario]
    return haversine(lat_pac, lon_pac, d["lat"], d["lon"])


def verificar_disponibilidad(medicamentos_requeridos, nombre_dispensario):
    """Verifica qué medicamentos están disponibles en un dispensario."""
    inv = INVENTARIO[nombre_dispensario]
    resultado = {}
    for med in medicamentos_requeridos:
        resultado[med] = inv.get(med, False)
    return resultado


def porcentaje_disponibilidad(medicamentos_requeridos, nombre_dispensario):
    """Porcentaje de medicamentos disponibles en un dispensario."""
    disp = verificar_disponibilidad(medicamentos_requeridos, nombre_dispensario)
    if not disp:
        return 0
    return sum(disp.values()) / len(disp) * 100


def encontrar_dispensarios_completos(medicamentos_requeridos):
    """Encuentra dispensarios que tengan TODOS los medicamentos."""
    completos = []
    for nombre in DISPENSARIOS:
        disp = verificar_disponibilidad(medicamentos_requeridos, nombre)
        if all(disp.values()):
            completos.append(nombre)
    return completos


def estimar_tiempo_traslado(distancia_km):
    """Estima el tiempo de traslado asumiendo velocidad promedio urbana (20 km/h)."""
    velocidad_promedio_kmh = 20
    return (distancia_km / velocidad_promedio_kmh) * 60  # en minutos


def ranking_dispensarios(medicamentos_requeridos, lat_pac, lon_pac):
    """Genera un ranking de dispensarios según disponibilidad, distancia y tiempo."""
    ranking = []
    for nombre in DISPENSARIOS:
        distancia = calcular_distancia(lat_pac, lon_pac, nombre)
        pct = porcentaje_disponibilidad(medicamentos_requeridos, nombre)
        tiempo_traslado = estimar_tiempo_traslado(distancia)
        tiempo_atencion = DISPENSARIOS[nombre]["tiempo_atencion_min"]
        tiempo_total = tiempo_traslado + tiempo_atencion

        ranking.append({
            "Dispensario": nombre,
            "Disponibilidad (%)": round(pct, 1),
            "Distancia (km)": round(distancia, 2),
            "Tiempo traslado (min)": round(tiempo_traslado, 1),
            "Tiempo atención (min)": tiempo_atencion,
            "Tiempo total (min)": round(tiempo_total, 1),
        })

    return sorted(ranking, key=lambda x: (-x["Disponibilidad (%)"], x["Tiempo total (min)"]))


def mejor_combinacion_dos_dispensarios(medicamentos_requeridos, lat_pac, lon_pac):
    """
    Si ningún dispensario tiene todos los medicamentos, encuentra la mejor
    combinación de DOS dispensarios que cubra la totalidad, minimizando distancia.
    """
    nombres = list(DISPENSARIOS.keys())
    mejor = None
    mejor_distancia_total = float("inf")

    for d1, d2 in combinations(nombres, 2):
        disp1 = verificar_disponibilidad(medicamentos_requeridos, d1)
        disp2 = verificar_disponibilidad(medicamentos_requeridos, d2)

        # Verificar si juntos cubren todos
        todos_cubiertos = all(disp1[m] or disp2[m] for m in medicamentos_requeridos)
        if not todos_cubiertos:
            continue

        # Distancia total: paciente -> d1 -> d2
        dist_p_d1 = calcular_distancia(lat_pac, lon_pac, d1)
        dist_d1_d2 = haversine(
            DISPENSARIOS[d1]["lat"], DISPENSARIOS[d1]["lon"],
            DISPENSARIOS[d2]["lat"], DISPENSARIOS[d2]["lon"],
        )
        dist_total_12 = dist_p_d1 + dist_d1_d2

        # También evaluar paciente -> d2 -> d1
        dist_p_d2 = calcular_distancia(lat_pac, lon_pac, d2)
        dist_d2_d1 = dist_d1_d2  # misma distancia
        dist_total_21 = dist_p_d2 + dist_d2_d1

        if dist_total_12 <= dist_total_21:
            dist_total = dist_total_12
            orden = (d1, d2)
        else:
            dist_total = dist_total_21
            orden = (d2, d1)

        if dist_total < mejor_distancia_total:
            mejor_distancia_total = dist_total
            # Determinar qué medicamentos recoger en cada uno
            meds_en_primero = [m for m in medicamentos_requeridos if verificar_disponibilidad(medicamentos_requeridos, orden[0])[m]]
            meds_solo_segundo = [m for m in medicamentos_requeridos if not verificar_disponibilidad(medicamentos_requeridos, orden[0])[m]]
            mejor = {
                "dispensario_1": orden[0],
                "dispensario_2": orden[1],
                "meds_dispensario_1": meds_en_primero,
                "meds_dispensario_2": meds_solo_segundo,
                "distancia_total_km": round(dist_total, 2),
            }

    return mejor


# ─────────────────────────────────────────────
# INTERFAZ STREAMLIT
# ─────────────────────────────────────────────

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
    }
    .recomendacion-box {
        background-color: #d4edda;
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .alerta-box {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .info-dispensario {
        background-color: #e8f4f8;
        border-radius: 8px;
        padding: 15px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("💊 MediUbica")
st.subheader("Sistema inteligente de localización de dispensarios")
st.markdown("---")
st.markdown(
    "Encuentra el dispensario óptimo donde reclamar tus medicamentos, "
    "minimizando desplazamientos y tiempos de espera."
)

# ── Sidebar: datos de entrada ──
with st.sidebar:
    st.header("📋 Datos del paciente")

    st.subheader("1. Medicamentos requeridos")
    medicamentos_seleccionados = st.multiselect(
        "Selecciona los medicamentos de tu fórmula:",
        options=CATALOGO_MEDICAMENTOS,
        default=None,
        help="Escoge todos los medicamentos que necesitas reclamar.",
    )

    st.markdown("---")
    st.subheader("2. Tu ubicación")
    st.markdown("Ingresa tus coordenadas aproximadas o usa los valores por defecto (centro de Bogotá).")
    lat_paciente = st.number_input("Latitud", value=4.6600, format="%.4f", step=0.001)
    lon_paciente = st.number_input("Longitud", value=-74.0700, format="%.4f", step=0.001)

    st.markdown("---")
    buscar = st.button("🔍 Buscar mejor dispensario", type="primary", use_container_width=True)

# ── Contenido principal ──
if not buscar:
    # Vista inicial: mostrar dispensarios y su información
    st.header("🏥 Dispensarios disponibles")
    st.markdown("Estos son los dispensarios asociados a la clínica en la ciudad:")

    cols = st.columns(2)
    for i, (nombre, info) in enumerate(DISPENSARIOS.items()):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"**{nombre}**")
                st.markdown(f"📍 {info['direccion']}")
                st.markdown(f"🕐 {info['horario']}")
                st.markdown(f"📞 {info['telefono']}")
                st.markdown(f"⏱️ Tiempo promedio de atención: **{info['tiempo_atencion_min']} min**")

    st.markdown("---")
    st.info("👈 Selecciona tus medicamentos en el panel lateral y presiona **Buscar** para obtener tu recomendación.")

else:
    # ── Validación ──
    if not medicamentos_seleccionados:
        st.error("⚠️ Debes seleccionar al menos un medicamento para buscar.")
        st.stop()

    # ── Resultados ──
    st.header("📊 Resultados de búsqueda")

    # Mostrar medicamentos solicitados
    with st.expander("📝 Medicamentos solicitados", expanded=True):
        for med in medicamentos_seleccionados:
            st.markdown(f"- {med}")

    st.markdown("---")

    # 1. Buscar dispensarios con todos los medicamentos
    completos = encontrar_dispensarios_completos(medicamentos_seleccionados)

    # 2. Generar ranking general
    ranking = ranking_dispensarios(medicamentos_seleccionados, lat_paciente, lon_paciente)

    if completos:
        # ── CASO 1: Hay dispensarios con todos los medicamentos ──
        st.success(f"✅ ¡Se encontraron **{len(completos)}** dispensario(s) con todos tus medicamentos!")

        # Determinar el mejor (menor tiempo total entre los completos)
        mejor_nombre = None
        mejor_tiempo = float("inf")
        for r in ranking:
            if r["Dispensario"] in completos and r["Tiempo total (min)"] < mejor_tiempo:
                mejor_nombre = r["Dispensario"]
                mejor_tiempo = r["Tiempo total (min)"]

        info_mejor = DISPENSARIOS[mejor_nombre]
        distancia_mejor = calcular_distancia(lat_paciente, lon_paciente, mejor_nombre)
        disp_detalle = verificar_disponibilidad(medicamentos_seleccionados, mejor_nombre)

        # Tarjeta de recomendación
        st.markdown("### 🏆 Dispensario recomendado")
        with st.container(border=True):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"## {mejor_nombre}")
                st.markdown(f"📍 **Dirección:** {info_mejor['direccion']}")
                st.markdown(f"🕐 **Horario:** {info_mejor['horario']}")
                st.markdown(f"📞 **Teléfono:** {info_mejor['telefono']}")
            with col2:
                st.metric("Distancia", f"{distancia_mejor:.2f} km")
                st.metric("Tiempo total estimado", f"{mejor_tiempo:.0f} min")
                st.metric("Disponibilidad", "100%")

            st.markdown("---")
            st.markdown("**Disponibilidad de medicamentos:**")
            for med, disponible in disp_detalle.items():
                icono = "✅" if disponible else "❌"
                estado = "Disponible" if disponible else "No disponible"
                st.markdown(f"{icono} {med} — *{estado}*")

            st.markdown("---")
            tiempo_traslado = estimar_tiempo_traslado(distancia_mejor)
            st.markdown("**📋 Justificación de la recomendación:**")
            st.markdown(
                f"Se recomienda **{mejor_nombre}** porque cuenta con el **100% de los medicamentos** "
                f"solicitados. La distancia estimada es de **{distancia_mejor:.2f} km** "
                f"(aprox. **{tiempo_traslado:.0f} min** de traslado) y el tiempo promedio de atención "
                f"es de **{info_mejor['tiempo_atencion_min']} min**, para un tiempo total estimado de "
                f"**{mejor_tiempo:.0f} minutos**. Esto permite al paciente reclamar toda su fórmula "
                f"en un solo lugar, evitando desplazamientos adicionales."
            )

    else:
        # ── CASO 2: Ningún dispensario tiene todos ──
        st.warning("⚠️ Ningún dispensario tiene la totalidad de los medicamentos solicitados.")

        # Mostrar el que tiene mayor porcentaje
        mejor_individual = ranking[0]
        st.markdown("### 📊 Dispensario con mayor disponibilidad individual")
        with st.container(border=True):
            info_ind = DISPENSARIOS[mejor_individual["Dispensario"]]
            disp_ind = verificar_disponibilidad(medicamentos_seleccionados, mejor_individual["Dispensario"])
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"## {mejor_individual['Dispensario']}")
                st.markdown(f"📍 {info_ind['direccion']}")
                st.markdown(f"🕐 {info_ind['horario']}")
            with col2:
                st.metric("Disponibilidad", f"{mejor_individual['Disponibilidad (%)']:.0f}%")
                st.metric("Distancia", f"{mejor_individual['Distancia (km)']} km")
                st.metric("Tiempo total", f"{mejor_individual['Tiempo total (min)']:.0f} min")

            st.markdown("**Detalle de disponibilidad:**")
            for med, disponible in disp_ind.items():
                icono = "✅" if disponible else "❌"
                estado = "Disponible" if disponible else "No disponible"
                st.markdown(f"{icono} {med} — *{estado}*")

        # Buscar mejor combinación de 2 dispensarios
        st.markdown("---")
        st.markdown("### 🔄 Mejor combinación de dos dispensarios")

        combinacion = mejor_combinacion_dos_dispensarios(
            medicamentos_seleccionados, lat_paciente, lon_paciente
        )

        if combinacion:
            st.success("Se encontró una combinación que cubre el 100% de tu fórmula:")
            with st.container(border=True):
                col1, col2 = st.columns(2)

                info_d1 = DISPENSARIOS[combinacion["dispensario_1"]]
                info_d2 = DISPENSARIOS[combinacion["dispensario_2"]]

                with col1:
                    st.markdown(f"**🥇 Primera parada:**")
                    st.markdown(f"### {combinacion['dispensario_1']}")
                    st.markdown(f"📍 {info_d1['direccion']}")
                    dist_1 = calcular_distancia(lat_paciente, lon_paciente, combinacion["dispensario_1"])
                    st.markdown(f"📏 Distancia desde tu ubicación: **{dist_1:.2f} km**")
                    st.markdown("**Medicamentos a recoger aquí:**")
                    for m in combinacion["meds_dispensario_1"]:
                        st.markdown(f"  ✅ {m}")

                with col2:
                    st.markdown(f"**🥈 Segunda parada:**")
                    st.markdown(f"### {combinacion['dispensario_2']}")
                    st.markdown(f"📍 {info_d2['direccion']}")
                    st.markdown("**Medicamentos a recoger aquí:**")
                    for m in combinacion["meds_dispensario_2"]:
                        st.markdown(f"  ✅ {m}")

                st.markdown("---")
                tiempo_traslado_total = estimar_tiempo_traslado(combinacion["distancia_total_km"])
                tiempo_atencion_total = info_d1["tiempo_atencion_min"] + info_d2["tiempo_atencion_min"]
                tiempo_total_comb = tiempo_traslado_total + tiempo_atencion_total

                mcol1, mcol2, mcol3 = st.columns(3)
                mcol1.metric("Distancia total recorrida", f"{combinacion['distancia_total_km']} km")
                mcol2.metric("Tiempo traslado estimado", f"{tiempo_traslado_total:.0f} min")
                mcol3.metric("Tiempo total estimado", f"{tiempo_total_comb:.0f} min")

                st.markdown("**📋 Justificación de la recomendación:**")
                st.markdown(
                    f"Dado que ningún dispensario individual tiene todos los medicamentos, "
                    f"se recomienda visitar primero **{combinacion['dispensario_1']}** "
                    f"(donde se concentra la mayoría de medicamentos disponibles) y luego "
                    f"**{combinacion['dispensario_2']}** para completar la fórmula. "
                    f"La distancia total del recorrido es de **{combinacion['distancia_total_km']} km** "
                    f"con un tiempo total estimado de **{tiempo_total_comb:.0f} minutos** "
                    f"(traslado + atención en ambos puntos)."
                )

        else:
            st.error(
                "❌ No se encontró una combinación de dos dispensarios que cubra todos los medicamentos. "
                "Se recomienda contactar a la clínica para solicitar un traslado de medicamentos."
            )

    # ── Tabla comparativa general ──
    st.markdown("---")
    st.markdown("### 📋 Comparativa general de dispensarios")

    df_ranking = pd.DataFrame(ranking)
    st.dataframe(
        df_ranking.style.background_gradient(
            subset=["Disponibilidad (%)"], cmap="Greens"
        ).background_gradient(
            subset=["Tiempo total (min)"], cmap="Reds_r"
        ),
        use_container_width=True,
        hide_index=True,
    )

    # ── Mapa de dispensarios ──
    st.markdown("---")
    st.markdown("### 🗺️ Mapa de dispensarios")

    map_data = []
    for nombre, info in DISPENSARIOS.items():
        map_data.append({
            "lat": info["lat"],
            "lon": info["lon"],
        })
    # Agregar ubicación del paciente
    map_data.append({
        "lat": lat_paciente,
        "lon": lon_paciente,
    })

    df_map = pd.DataFrame(map_data)
    st.map(df_map)
    st.caption("📍 Los puntos incluyen los dispensarios y tu ubicación actual.")

    # ── Resumen formato solicitado ──
    st.markdown("---")
    st.markdown("### 📄 Resumen")

    if completos:
        disp_rec = mejor_nombre
        info_rec = DISPENSARIOS[disp_rec]
        dist_rec = calcular_distancia(lat_paciente, lon_paciente, disp_rec)
        disp_det = verificar_disponibilidad(medicamentos_seleccionados, disp_rec)
        t_traslado = estimar_tiempo_traslado(dist_rec)
        t_total = t_traslado + info_rec["tiempo_atencion_min"]

        resumen = f"""**Medicamentos solicitados:**\n"""
        for m in medicamentos_seleccionados:
            resumen += f"- {m}\n"
        resumen += f"""\n**Dispensario recomendado:**\n{disp_rec}\n\n**Disponibilidad:**\n"""
        for m, d in disp_det.items():
            estado = "✅ Disponible" if d else "❌ No disponible"
            resumen += f"- {m}: {estado}\n"
        resumen += f"""\n**Tiempo estimado total:**\n{t_total:.0f} minutos (traslado: {t_traslado:.0f} min + atención: {info_rec['tiempo_atencion_min']} min)\n"""
        resumen += f"""\n**Distancia total:**\n{dist_rec:.2f} km\n"""
        resumen += f"""\n**Justificación de la recomendación:**\nSe recomienda {disp_rec} por tener el 100% de los medicamentos solicitados, con la mejor combinación de cercanía ({dist_rec:.2f} km) y menor tiempo total estimado ({t_total:.0f} min)."""

    else:
        resumen = f"""**Medicamentos solicitados:**\n"""
        for m in medicamentos_seleccionados:
            resumen += f"- {m}\n"
        resumen += f"""\n**Dispensario con mayor disponibilidad:**\n{mejor_individual['Dispensario']} ({mejor_individual['Disponibilidad (%)']:.0f}%)\n"""
        if combinacion:
            resumen += f"""\n**Combinación recomendada:**\n1. {combinacion['dispensario_1']}\n2. {combinacion['dispensario_2']}\n"""
            resumen += f"""\n**Distancia total:**\n{combinacion['distancia_total_km']} km\n"""
            resumen += f"""\n**Tiempo estimado total:**\n{tiempo_total_comb:.0f} minutos\n"""
            resumen += f"""\n**Justificación:**\nNingún dispensario individual tiene todos los medicamentos. La combinación recomendada cubre el 100% de la fórmula minimizando la distancia total de desplazamiento."""
        else:
            resumen += "\n**No se encontró combinación que cubra todos los medicamentos.** Contacte a la clínica."

    st.markdown(resumen)
