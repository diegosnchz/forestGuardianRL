"""
Módulo de visualización GIS para Forest Guardian RL
Proporciona mapas interactivos con Folium
"""

import folium
from folium.plugins import HeatMap, MarkerCluster
import numpy as np
from typing import List, Tuple, Dict, Optional
from forest_fire_gis import ForestFireGISEnv

class MapaForestGuardian:
    """Crea mapas interactivos con Folium para visualizar simulaciones GIS"""
    
    def __init__(self, env: ForestFireGISEnv, zoom_level: int = 12):
        """
        Inicializa el generador de mapas
        
        Args:
            env: Entorno ForestFireGISEnv
            zoom_level: Nivel de zoom inicial (6-18)
        """
        self.env = env
        self.zoom_level = zoom_level
        self.bosque = env.bosque
        
        # Colores
        self.COLOR_FUEGO = '#ff0000'
        self.COLOR_ARBOL = '#00aa00'
        self.COLOR_AGENTE1 = '#0066ff'
        self.COLOR_AGENTE2 = '#ff9900'
        self.COLOR_AGENTE3 = '#9966ff'
    
    def crear_mapa_base(self) -> folium.Map:
        """
        Crea el mapa base con OpenStreetMap satelital
        
        Returns:
            Mapa Folium centrado en el bosque
        """
        center_lat, center_lon = self.env.get_grid_center()
        
        mapa = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=self.zoom_level,
            tiles='OpenStreetMap',  # Puede ser 'Satellite', etc.
            attr='© OpenStreetMap contributors'
        )
        
        return mapa
    
    def crear_mapa_satelital(self) -> folium.Map:
        """Crea mapa con visualización satelital"""
        center_lat, center_lon = self.env.get_grid_center()
        
        mapa = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=self.zoom_level,
            tiles='Stamen Terrain',  # Relieve
            attr='© OpenStreetMap contributors'
        )
        
        return mapa
    
    def agregar_limites_grid(self, mapa: folium.Map) -> folium.Map:
        """Dibuja el rectángulo que delimita el área del grid"""
        bounds = self.env.get_grid_bounds()
        
        # Esquinas del rectángulo
        esquinas = [
            [bounds['north'], bounds['west']],
            [bounds['north'], bounds['east']],
            [bounds['south'], bounds['east']],
            [bounds['south'], bounds['west']],
            [bounds['north'], bounds['west']]  # Cerrar el polígono
        ]
        
        folium.PolyLine(
            esquinas,
            color='purple',
            weight=3,
            opacity=0.7,
            popup=f"Área de simulación: {self.env.get_coverage_area_km2():.2f} km²"
        ).add_to(mapa)
        
        return mapa
    
    def agregar_grid_cells(self, mapa: folium.Map) -> folium.Map:
        """Dibuja las celdas del grid como un cuadriculado"""
        bounds = self.env.get_grid_bounds()
        lat_step = (bounds['north'] - bounds['south']) / self.env.grid_size
        lon_step = (bounds['east'] - bounds['west']) / self.env.grid_size
        
        # Dibujar líneas horizontales y verticales
        for i in range(self.env.grid_size + 1):
            # Líneas horizontales (latitud constante)
            lat = bounds['north'] - (i * lat_step)
            folium.PolyLine(
                [[lat, bounds['west']], [lat, bounds['east']]],
                color='gray',
                weight=1,
                opacity=0.3
            ).add_to(mapa)
            
            # Líneas verticales (longitud constante)
            lon = bounds['west'] + (i * lon_step)
            folium.PolyLine(
                [[bounds['north'], lon], [bounds['south'], lon]],
                color='gray',
                weight=1,
                opacity=0.3
            ).add_to(mapa)
        
        return mapa
    
    def agregar_arboles(self, mapa: folium.Map) -> folium.Map:
        """Añade marcadores para los árboles salvados"""
        arboles = self.env.get_trees_geo_positions()
        
        for tree_lat, tree_lon in arboles:
            folium.CircleMarker(
                location=[tree_lat, tree_lon],
                radius=4,
                popup='Árbol',
                color=self.COLOR_ARBOL,
                fill=True,
                fillColor=self.COLOR_ARBOL,
                fillOpacity=0.7,
                weight=1,
                opacity=0.8
            ).add_to(mapa)
        
        return mapa
    
    def agregar_fuegos(self, mapa: folium.Map) -> folium.Map:
        """Añade marcadores para los fuegos activos"""
        fuegos = self.env.get_fires_geo_positions()
        
        for fire_lat, fire_lon in fuegos:
            folium.CircleMarker(
                location=[fire_lat, fire_lon],
                radius=6,
                popup='🔥 Fuego Activo',
                color=self.COLOR_FUEGO,
                fill=True,
                fillColor=self.COLOR_FUEGO,
                fillOpacity=0.9,
                weight=2,
                opacity=1.0
            ).add_to(mapa)
        
        return mapa
    
    def agregar_heatmap_fuego(self, mapa: folium.Map) -> folium.Map:
        """Añade un heatmap de intensidad del fuego"""
        heatmap_data = self.env.get_heatmap_data()
        
        if heatmap_data:
            # Convertir formato para HeatMap de Folium
            heat_data = [[lat, lon, intensity] for lat, lon, intensity in heatmap_data]
            
            HeatMap(
                heat_data,
                min_opacity=0.2,
                radius=20,
                blur=15,
                max_zoom=1,
                gradient={0.2: 'green', 0.5: 'yellow', 0.7: 'orange', 1.0: 'red'}
            ).add_to(mapa)
        
        return mapa
    
    def agregar_drones(self, mapa: folium.Map) -> folium.Map:
        """Añade iconos para los drones"""
        agentes_geo = self.env.get_agent_geo_positions()
        colores = [self.COLOR_AGENTE1, self.COLOR_AGENTE2, self.COLOR_AGENTE3]
        nombres = ['Dron ALPHA (Proximidad)', 'Dron BRAVO (Contención)', 'Dron CHARLIE (Apoyo)']
        
        for i, (agent_lat, agent_lon) in enumerate(agentes_geo):
            # Usar popup con información del dron
            popup_text = f"{nombres[i % len(nombres)]}<br>Pos: {agent_lat:.4f}, {agent_lon:.4f}"
            
            folium.Marker(
                location=[agent_lat, agent_lon],
                popup=folium.Popup(popup_text, max_width=200),
                icon=folium.Icon(
                    color='blue' if i == 0 else 'orange' if i == 1 else 'purple',
                    icon='drone',
                    prefix='fa'
                ),
                tooltip=f"Dron {i + 1}"
            ).add_to(mapa)
        
        return mapa
    
    def agregar_informacion_bosque(self, mapa: folium.Map) -> folium.Map:
        """Añade información del bosque en el mapa"""
        center_lat, center_lon = self.env.get_grid_center()
        
        info_text = f"""
        <b>{self.bosque.nombre}</b><br>
        País: {self.bosque.pais}<br>
        Área bosque: {self.bosque.area_km2:,.0f} km²<br>
        Densidad: {self.bosque.densidad}<br>
        <br>
        <b>Amenazas:</b><br>
        {', '.join(self.bosque.amenazas)}
        """
        
        folium.Marker(
            location=[center_lat, center_lon],
            popup=folium.Popup(info_text, max_width=250),
            icon=folium.Icon(color='green', icon='info-sign'),
            tooltip='Información del bosque'
        ).add_to(mapa)
        
        return mapa
    
    def crear_mapa_completo(
        self,
        incluir_arboles: bool = True,
        incluir_heatmap: bool = True,
        incluir_grid: bool = True,
        incluir_drones: bool = True,
        incluir_info: bool = True
    ) -> folium.Map:
        """
        Crea un mapa completo con todos los elementos
        
        Args:
            incluir_arboles: Mostrar árboles salvados
            incluir_heatmap: Mostrar mapa de calor de fuego
            incluir_grid: Mostrar cuadriculado
            incluir_drones: Mostrar iconos de drones
            incluir_info: Mostrar información del bosque
        
        Returns:
            Mapa Folium completamente configurado
        """
        mapa = self.crear_mapa_base()
        
        if incluir_grid:
            mapa = self.agregar_limites_grid(mapa)
            mapa = self.agregar_grid_cells(mapa)
        
        if incluir_arboles:
            mapa = self.agregar_arboles(mapa)
        
        # Heatmap siempre (para fuegos)
        mapa = self.agregar_heatmap_fuego(mapa)
        
        # Marcadores de fuegos (redundante con heatmap pero más visibles)
        mapa = self.agregar_fuegos(mapa)
        
        if incluir_drones:
            mapa = self.agregar_drones(mapa)
        
        if incluir_info:
            mapa = self.agregar_informacion_bosque(mapa)
        
        # Agregar leyenda
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; width: 220px; height: 200px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <b>Leyenda</b><br>
        <i style="background-color:#00aa00; width: 12px; height: 12px; 
                  border-radius: 50%; display: inline-block;"></i> Árbol<br>
        <i style="background-color:#ff0000; width: 12px; height: 12px; 
                  border-radius: 50%; display: inline-block;"></i> Fuego<br>
        <i style="background-color:#0066ff; width: 12px; height: 12px; 
                  border-radius: 50%; display: inline-block;"></i> Dron Azul<br>
        <i style="background-color:#ff9900; width: 12px; height: 12px; 
                  border-radius: 50%; display: inline-block;"></i> Dron Naranja<br>
        <i style="background-color:#9966ff; width: 12px; height: 12px; 
                  border-radius: 50%; display: inline-block;"></i> Dron Púrpura<br>
        <hr style="margin: 5px 0;">
        Red: Heatmap de fuego<br>
        Verde: Cobertura forestal
        </div>
        '''
        mapa.get_root().html.add_child(folium.Element(legend_html))
        
        return mapa
    
    def crear_mapa_estado_simulacion(self) -> folium.Map:
        """
        Crea un mapa especial mostrando el estado actual de la simulación
        """
        mapa = self.crear_mapa_base()
        mapa = self.agregar_limites_grid(mapa)
        mapa = self.agregar_heatmap_fuego(mapa)
        mapa = self.agregar_fuegos(mapa)
        mapa = self.agregar_drones(mapa)
        
        return mapa
