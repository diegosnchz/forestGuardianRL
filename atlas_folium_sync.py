"""
Módulo de visualización Folium integrado con MongoDB Atlas.

Este módulo proporciona funciones para sincronizar mapas de Folium
con datos geoespaciales almacenados en MongoDB Atlas.

Características:
- Conexión automática a MongoDB Atlas
- Visualización de features GeoJSON en Folium
- Tooltips dinámicos con información de estado
- Sistema de reinicio de base de datos
- Actualización en tiempo real de estados

Autor: Forest Guardian RL Team
Fecha: Enero 2026
"""

import streamlit as st
import folium
from folium import plugins
import json
from typing import Optional, Dict, List, Any, Tuple
from pathlib import Path
import logging

try:
    from pymongo import MongoClient, GEOSPHERE
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

try:
    from streamlit_folium import st_folium
    STREAMLIT_FOLIUM_AVAILABLE = True
except ImportError:
    STREAMLIT_FOLIUM_AVAILABLE = False

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Colores para diferentes tipos de zonas
ZONE_COLORS = {
    'coniferas': '#228B22',      # Verde bosque
    'mixto': '#90EE90',           # Verde claro
    'protegida': '#006400',       # Verde oscuro
    'estacion': '#FF4500',        # Rojo-naranja
    'ruta': '#1E90FF',            # Azul
    'default': '#808080'          # Gris
}

# Colores para niveles de riesgo
RISK_COLORS = {
    'bajo': '#00FF00',    # Verde
    'medio': '#FFA500',   # Naranja
    'alto': '#FF0000',    # Rojo
    'critico': '#8B0000'  # Rojo oscuro
}


class AtlasFoliumSync:
    """
    Clase para sincronizar mapas de Folium con MongoDB Atlas.
    
    Gestiona la conexión a MongoDB Atlas, recupera datos geoespaciales,
    y los visualiza en mapas de Folium con tooltips interactivos.
    """
    
    def __init__(self, uri: Optional[str] = None, 
                 database: str = "forest_guardian",
                 collection: str = "mapa_forestal"):
        """
        Inicializa la sincronización Atlas-Folium.
        
        Args:
            uri: URI de conexión a MongoDB Atlas
            database: Nombre de la base de datos
            collection: Nombre de la colección
        """
        self.uri = uri
        self.database_name = database
        self.collection_name = collection
        self.client = None
        self.db = None
        self.collection = None
        self.connected = False
        
        if uri and PYMONGO_AVAILABLE:
            self._connect()
    
    def _connect(self) -> bool:
        """
        Establece conexión con MongoDB Atlas.
        
        Returns:
            True si la conexión fue exitosa
        """
        try:
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=3000,
                connectTimeoutMS=5000
            )
            
            # Verificar conexión
            self.client.admin.command('ping')
            
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            self.connected = True
            
            logger.info(f"✅ Conectado a MongoDB Atlas: {self.database_name}.{self.collection_name}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ Error de conexión a MongoDB Atlas: {e}")
            self.connected = False
            return False
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            self.connected = False
            return False
    
    def get_all_features(self) -> List[Dict[str, Any]]:
        """
        Recupera todos los documentos de la colección.
        
        Returns:
            Lista de documentos con features GeoJSON
        """
        if not self.connected or not self.collection:
            logger.warning("⚠️ No hay conexión a MongoDB Atlas")
            return []
        
        try:
            documents = list(self.collection.find({}))
            logger.info(f"📊 Recuperados {len(documents)} documentos de Atlas")
            return documents
        except Exception as e:
            logger.error(f"❌ Error recuperando documentos: {e}")
            return []
    
    def get_features_by_type(self, zone_type: str) -> List[Dict[str, Any]]:
        """
        Recupera documentos filtrados por tipo.
        
        Args:
            zone_type: Tipo de zona a filtrar
            
        Returns:
            Lista de documentos del tipo especificado
        """
        if not self.connected or not self.collection:
            return []
        
        try:
            documents = list(self.collection.find({"tipo": zone_type}))
            return documents
        except Exception as e:
            logger.error(f"❌ Error filtrando por tipo: {e}")
            return []
    
    def update_zone_state(self, zone_id: str, state_updates: Dict[str, Any]) -> bool:
        """
        Actualiza el estado de una zona en Atlas.
        
        Args:
            zone_id: ID del feature (metadata.feature_id)
            state_updates: Diccionario con actualizaciones de estado
            
        Returns:
            True si la actualización fue exitosa
        """
        if not self.connected or not self.collection:
            return False
        
        try:
            result = self.collection.update_one(
                {"metadata.feature_id": zone_id},
                {"$set": state_updates}
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ Zona {zone_id} actualizada")
                return True
            else:
                logger.warning(f"⚠️ Zona {zone_id} no encontrada")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error actualizando zona: {e}")
            return False
    
    def clear_database(self) -> Tuple[bool, int]:
        """
        Limpia todos los documentos de la colección.
        
        Returns:
            Tupla (éxito, cantidad de documentos eliminados)
        """
        if not self.connected or not self.collection:
            return False, 0
        
        try:
            result = self.collection.delete_many({})
            deleted_count = result.deleted_count
            logger.info(f"🗑️ {deleted_count} documentos eliminados")
            return True, deleted_count
            
        except Exception as e:
            logger.error(f"❌ Error limpiando base de datos: {e}")
            return False, 0
    
    def reload_from_geojson(self, geojson_path: str) -> Tuple[bool, int]:
        """
        Recarga datos desde un archivo GeoJSON.
        
        Args:
            geojson_path: Ruta al archivo GeoJSON
            
        Returns:
            Tupla (éxito, cantidad de documentos insertados)
        """
        if not self.connected or not self.collection:
            return False, 0
        
        try:
            # Leer GeoJSON
            with open(geojson_path, 'r', encoding='utf-8') as f:
                geojson_data = json.load(f)
            
            # Preparar documentos
            from datetime import datetime
            documents = []
            
            features = geojson_data.get('features', [])
            for idx, feature in enumerate(features):
                geometry = feature.get('geometry')
                properties = feature.get('properties', {})
                
                document = {
                    'location': {
                        'type': geometry['type'],
                        'coordinates': geometry['coordinates']
                    },
                    'properties': properties,
                    'metadata': {
                        'uploaded_at': datetime.utcnow(),
                        'source': 'geojson_reload',
                        'feature_id': feature.get('id', f"feature_{idx}")
                    }
                }
                
                # Campos adicionales para indexación
                if 'nombre' in properties or 'name' in properties:
                    document['nombre'] = properties.get('nombre') or properties.get('name')
                
                if 'tipo' in properties or 'type' in properties:
                    document['tipo'] = properties.get('tipo') or properties.get('type')
                
                documents.append(document)
            
            # Insertar documentos
            if documents:
                result = self.collection.insert_many(documents)
                inserted_count = len(result.inserted_ids)
                logger.info(f"📤 {inserted_count} documentos insertados desde {geojson_path}")
                return True, inserted_count
            else:
                return False, 0
                
        except Exception as e:
            logger.error(f"❌ Error recargando desde GeoJSON: {e}")
            return False, 0
    
    def close(self):
        """Cierra la conexión con MongoDB."""
        if self.client:
            self.client.close()
            self.connected = False
            logger.info("🔌 Conexión cerrada")


def create_feature_tooltip(feature: Dict[str, Any]) -> str:
    """
    Crea un HTML tooltip para un feature.
    
    Args:
        feature: Diccionario con datos del feature
        
    Returns:
        String HTML para el tooltip
    """
    nombre = feature.get('nombre', 'Sin nombre')
    tipo = feature.get('tipo', 'desconocido')
    properties = feature.get('properties', {})
    
    # Obtener información de estado
    riesgo = properties.get('riesgo_incendio', 'desconocido')
    humedad = properties.get('humedad', None)
    temperatura = properties.get('temperatura', None)
    area = feature.get('area', properties.get('area', None))
    
    # Construir HTML
    html = f"""
    <div style='font-family: Arial, sans-serif; min-width: 200px;'>
        <h4 style='margin: 0 0 10px 0; color: #333;'>
            {nombre}
        </h4>
        <hr style='margin: 10px 0; border: none; border-top: 1px solid #ddd;'>
        <table style='width: 100%; font-size: 12px;'>
            <tr>
                <td style='padding: 3px; color: #666;'><b>Tipo:</b></td>
                <td style='padding: 3px;'>{tipo}</td>
            </tr>
    """
    
    if riesgo != 'desconocido':
        risk_color = RISK_COLORS.get(riesgo, '#808080')
        html += f"""
            <tr>
                <td style='padding: 3px; color: #666;'><b>Riesgo:</b></td>
                <td style='padding: 3px;'>
                    <span style='background: {risk_color}; color: white; padding: 2px 6px; border-radius: 3px;'>
                        {riesgo.upper()}
                    </span>
                </td>
            </tr>
        """
    
    if humedad is not None:
        html += f"""
            <tr>
                <td style='padding: 3px; color: #666;'><b>Humedad:</b></td>
                <td style='padding: 3px;'>{humedad}%</td>
            </tr>
        """
    
    if temperatura is not None:
        html += f"""
            <tr>
                <td style='padding: 3px; color: #666;'><b>Temperatura:</b></td>
                <td style='padding: 3px;'>{temperatura}°C</td>
            </tr>
        """
    
    if area is not None:
        html += f"""
            <tr>
                <td style='padding: 3px; color: #666;'><b>Área:</b></td>
                <td style='padding: 3px;'>{area} ha</td>
            </tr>
        """
    
    # Información adicional
    densidad = properties.get('densidad_arboles')
    if densidad:
        html += f"""
            <tr>
                <td style='padding: 3px; color: #666;'><b>Densidad:</b></td>
                <td style='padding: 3px;'>{densidad} árboles/ha</td>
            </tr>
        """
    
    html += """
        </table>
    </div>
    """
    
    return html


def get_feature_color(feature: Dict[str, Any]) -> str:
    """
    Determina el color de un feature basado en su tipo y riesgo.
    
    Args:
        feature: Diccionario con datos del feature
        
    Returns:
        Color en formato hexadecimal
    """
    tipo = feature.get('tipo', 'default')
    properties = feature.get('properties', {})
    riesgo = properties.get('riesgo_incendio')
    
    # Si hay riesgo, priorizar ese color
    if riesgo in RISK_COLORS:
        return RISK_COLORS[riesgo]
    
    # Si no, usar color por tipo
    return ZONE_COLORS.get(tipo, ZONE_COLORS['default'])


def create_atlas_folium_map(features: List[Dict[str, Any]], 
                            center: Optional[Tuple[float, float]] = None,
                            zoom_start: int = 13,
                            show_heatmap: bool = False) -> folium.Map:
    """
    Crea un mapa de Folium con features de MongoDB Atlas.
    
    Args:
        features: Lista de documentos de Atlas
        center: Centro del mapa (lat, lon). Si es None, se calcula automáticamente
        zoom_start: Nivel de zoom inicial
        show_heatmap: Si True, muestra heatmap de riesgo
        
    Returns:
        Objeto folium.Map
    """
    # Calcular centro automáticamente si no se proporciona
    if center is None:
        center = calculate_center(features)
    
    # Crear mapa base
    m = folium.Map(
        location=center,
        zoom_start=zoom_start,
        tiles='OpenStreetMap'
    )
    
    # Agregar capas base alternativas
    folium.TileLayer('CartoDB positron', name='Claro').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='Oscuro').add_to(m)
    
    # Grupos de features por tipo
    grupos = {
        'Zonas Forestales': folium.FeatureGroup(name='Zonas Forestales'),
        'Estaciones': folium.FeatureGroup(name='Estaciones'),
        'Rutas': folium.FeatureGroup(name='Rutas de Patrulla'),
        'Otros': folium.FeatureGroup(name='Otros')
    }
    
    # Datos para heatmap
    heatmap_data = []
    
    # Procesar cada feature
    for feature in features:
        location = feature.get('location', {})
        geom_type = location.get('type')
        coords = location.get('coordinates', [])
        tipo = feature.get('tipo', 'default')
        properties = feature.get('properties', {})
        
        # Determinar grupo
        if tipo == 'estacion':
            grupo = grupos['Estaciones']
        elif tipo == 'ruta':
            grupo = grupos['Rutas']
        elif tipo in ['coniferas', 'mixto', 'protegida']:
            grupo = grupos['Zonas Forestales']
        else:
            grupo = grupos['Otros']
        
        # Crear tooltip
        tooltip_html = create_feature_tooltip(feature)
        tooltip = folium.Tooltip(tooltip_html)
        
        # Color del feature
        color = get_feature_color(feature)
        
        # Dibujar según tipo de geometría
        if geom_type == 'Point':
            # Punto (estación)
            lat, lon = coords[1], coords[0]
            
            if tipo == 'estacion':
                icon = folium.Icon(color='red', icon='tower-broadcast', prefix='fa')
            else:
                icon = folium.Icon(color='blue', icon='info-sign')
            
            folium.Marker(
                location=[lat, lon],
                tooltip=tooltip,
                icon=icon
            ).add_to(grupo)
            
            # Agregar a heatmap si tiene riesgo alto
            riesgo = properties.get('riesgo_incendio')
            if riesgo == 'alto':
                heatmap_data.append([lat, lon, 1.0])
            elif riesgo == 'medio':
                heatmap_data.append([lat, lon, 0.5])
        
        elif geom_type == 'Polygon':
            # Polígono (zona forestal)
            # Convertir coordenadas (lon, lat) a (lat, lon)
            poly_coords = [[[lat, lon] for lon, lat in ring] for ring in coords]
            
            folium.Polygon(
                locations=poly_coords[0],  # Primer anillo (exterior)
                tooltip=tooltip,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.3,
                weight=2
            ).add_to(grupo)
            
            # Agregar centroide a heatmap si tiene riesgo
            riesgo = properties.get('riesgo_incendio')
            if riesgo in ['alto', 'medio']:
                centroid = calculate_polygon_centroid(coords[0])
                weight = 1.0 if riesgo == 'alto' else 0.5
                heatmap_data.append([centroid[1], centroid[0], weight])
        
        elif geom_type == 'LineString':
            # Línea (ruta)
            line_coords = [[lat, lon] for lon, lat in coords]
            
            folium.PolyLine(
                locations=line_coords,
                tooltip=tooltip,
                color=color,
                weight=3,
                opacity=0.8
            ).add_to(grupo)
    
    # Agregar grupos al mapa
    for grupo in grupos.values():
        grupo.add_to(m)
    
    # Agregar heatmap si se solicita
    if show_heatmap and heatmap_data:
        from folium.plugins import HeatMap
        HeatMap(
            heatmap_data,
            name='Mapa de Calor - Riesgo',
            min_opacity=0.3,
            max_opacity=0.8,
            radius=25,
            blur=20,
            gradient={
                0.0: 'green',
                0.5: 'yellow',
                1.0: 'red'
            }
        ).add_to(m)
    
    # Agregar control de capas
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    
    # Agregar minimap
    plugins.MiniMap(toggle_display=True).add_to(m)
    
    # Agregar medidor de distancia
    plugins.MeasureControl(position='bottomleft').add_to(m)
    
    # Agregar fullscreen
    plugins.Fullscreen(position='topleft').add_to(m)
    
    return m


def calculate_center(features: List[Dict[str, Any]]) -> Tuple[float, float]:
    """
    Calcula el centro geográfico de un conjunto de features.
    
    Args:
        features: Lista de documentos con geometrías
        
    Returns:
        Tupla (latitud, longitud) del centro
    """
    if not features:
        return (19.4200, -99.1900)  # Centro de México por defecto
    
    lats = []
    lons = []
    
    for feature in features:
        location = feature.get('location', {})
        geom_type = location.get('type')
        coords = location.get('coordinates', [])
        
        if geom_type == 'Point':
            lons.append(coords[0])
            lats.append(coords[1])
        elif geom_type == 'Polygon':
            for lon, lat in coords[0]:
                lons.append(lon)
                lats.append(lat)
        elif geom_type == 'LineString':
            for lon, lat in coords:
                lons.append(lon)
                lats.append(lat)
    
    if lats and lons:
        return (sum(lats) / len(lats), sum(lons) / len(lons))
    else:
        return (19.4200, -99.1900)


def calculate_polygon_centroid(coords: List[List[float]]) -> Tuple[float, float]:
    """
    Calcula el centroide de un polígono.
    
    Args:
        coords: Lista de coordenadas [lon, lat]
        
    Returns:
        Tupla (lon, lat) del centroide
    """
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    
    return (sum(lons) / len(lons), sum(lats) / len(lats))


def streamlit_atlas_map_viewer(uri: Optional[str] = None,
                               geojson_path: str = "zonas_forestales_ejemplo.geojson",
                               enable_reload: bool = True):
    """
    Componente de Streamlit para visualizar mapas de MongoDB Atlas.
    
    Esta función crea una interfaz completa en Streamlit que:
    - Se conecta a MongoDB Atlas
    - Recupera y visualiza features en Folium
    - Permite actualizar estados de zonas
    - Proporciona botón de reinicio de base de datos
    
    Args:
        uri: URI de MongoDB Atlas (None para modo demo sin conexión)
        geojson_path: Ruta al archivo GeoJSON para recargas
        enable_reload: Si True, muestra botón de reinicio
    """
    st.header("🗺️ Mapa Geoespacial - MongoDB Atlas")
    
    # Verificar dependencias
    if not STREAMLIT_FOLIUM_AVAILABLE:
        st.error("❌ streamlit-folium no está instalado")
        st.code("pip install streamlit-folium", language="bash")
        return
    
    if not PYMONGO_AVAILABLE:
        st.error("❌ pymongo no está instalado")
        st.code("pip install pymongo", language="bash")
        return
    
    # Columnas para configuración
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if uri:
            st.success("✅ Conectado a MongoDB Atlas")
        else:
            st.warning("⚠️ No hay URI de MongoDB Atlas configurado")
            uri = st.text_input(
                "URI de MongoDB Atlas",
                type="password",
                help="Pega tu URI de conexión aquí"
            )
    
    with col2:
        show_heatmap = st.checkbox("🔥 Mapa de Calor", value=False)
    
    with col3:
        auto_refresh = st.checkbox("🔄 Auto-actualizar", value=False)
    
    # Crear instancia de sincronización
    sync = AtlasFoliumSync(uri=uri)
    
    if not sync.connected and uri:
        st.error("❌ No se pudo conectar a MongoDB Atlas")
        st.info("💡 Verifica tu URI y configuración de red")
        return
    
    # Botones de control
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    
    with col_btn1:
        if st.button("🔄 Actualizar Mapa", use_container_width=True):
            st.rerun()
    
    with col_btn2:
        if enable_reload and st.button("🗑️ Limpiar BD", use_container_width=True, type="secondary"):
            if sync.connected:
                success, count = sync.clear_database()
                if success:
                    st.success(f"✅ {count} documentos eliminados")
                    st.rerun()
                else:
                    st.error("❌ Error al limpiar base de datos")
    
    with col_btn3:
        if enable_reload and st.button("📤 Recargar GeoJSON", use_container_width=True, type="primary"):
            if sync.connected and Path(geojson_path).exists():
                with st.spinner("Cargando datos..."):
                    # Primero limpiar
                    sync.clear_database()
                    # Luego recargar
                    success, count = sync.reload_from_geojson(geojson_path)
                    if success:
                        st.success(f"✅ {count} documentos cargados desde {geojson_path}")
                        st.rerun()
                    else:
                        st.error("❌ Error al recargar datos")
            elif not sync.connected:
                st.error("❌ No hay conexión a Atlas")
            else:
                st.error(f"❌ Archivo no encontrado: {geojson_path}")
    
    with col_btn4:
        if st.button("💾 Exportar GeoJSON", use_container_width=True):
            if sync.connected:
                features = sync.get_all_features()
                if features:
                    # Convertir a GeoJSON
                    geojson = {
                        "type": "FeatureCollection",
                        "features": []
                    }
                    for f in features:
                        geojson["features"].append({
                            "type": "Feature",
                            "id": f.get("metadata", {}).get("feature_id"),
                            "properties": f.get("properties", {}),
                            "geometry": f.get("location", {})
                        })
                    
                    st.download_button(
                        label="⬇️ Descargar GeoJSON",
                        data=json.dumps(geojson, indent=2),
                        file_name="mapa_forestal_export.geojson",
                        mime="application/json"
                    )
    
    # Recuperar features
    if sync.connected:
        features = sync.get_all_features()
    else:
        # Modo demo: cargar desde archivo local
        try:
            with open(geojson_path, 'r') as f:
                geojson_data = json.load(f)
            features = []
            for f in geojson_data.get('features', []):
                features.append({
                    'location': f['geometry'],
                    'properties': f.get('properties', {}),
                    'tipo': f.get('properties', {}).get('tipo', 'default'),
                    'nombre': f.get('properties', {}).get('nombre', 'Sin nombre')
                })
        except Exception as e:
            st.error(f"❌ Error cargando archivo demo: {e}")
            features = []
    
    # Mostrar estadísticas
    if features:
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.metric("📍 Total Features", len(features))
        
        with col_stat2:
            zonas_count = len([f for f in features if f.get('tipo') in ['coniferas', 'mixto', 'protegida']])
            st.metric("🌲 Zonas Forestales", zonas_count)
        
        with col_stat3:
            estaciones_count = len([f for f in features if f.get('tipo') == 'estacion'])
            st.metric("📡 Estaciones", estaciones_count)
        
        with col_stat4:
            alto_riesgo = len([f for f in features 
                              if f.get('properties', {}).get('riesgo_incendio') == 'alto'])
            st.metric("⚠️ Alto Riesgo", alto_riesgo)
    
    # Crear y mostrar mapa
    if features:
        with st.spinner("Generando mapa..."):
            mapa = create_atlas_folium_map(features, show_heatmap=show_heatmap)
            
            # Mostrar mapa
            st_folium(
                mapa,
                width=None,
                height=600,
                returned_objects=[]
            )
    else:
        st.info("ℹ️ No hay datos para mostrar. Carga un archivo GeoJSON.")
    
    # Cerrar conexión
    if sync.connected:
        sync.close()
    
    # Auto-refresh
    if auto_refresh:
        import time
        time.sleep(5)
        st.rerun()


# ============================================================================
# FUNCIÓN DE EJEMPLO PARA INTEGRACIÓN
# ============================================================================

def example_integration():
    """
    Ejemplo de cómo integrar esta función en app.py
    """
    st.title("🌲 Forest Guardian RL - Mapa Geoespacial")
    
    # Configuración en sidebar
    with st.sidebar:
        st.header("⚙️ Configuración MongoDB Atlas")
        
        uri = st.text_input(
            "URI de MongoDB Atlas",
            type="password",
            help="mongodb+srv://user:pass@cluster.mongodb.net/..."
        )
        
        geojson_file = st.text_input(
            "Archivo GeoJSON",
            value="zonas_forestales_ejemplo.geojson"
        )
    
    # Mostrar mapa
    streamlit_atlas_map_viewer(
        uri=uri if uri else None,
        geojson_path=geojson_file,
        enable_reload=True
    )


if __name__ == "__main__":
    # Ejecutar ejemplo
    example_integration()
