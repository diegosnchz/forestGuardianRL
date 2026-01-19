#!/usr/bin/env python3
"""
Script para cargar datos GeoJSON de zonas forestales a MongoDB Atlas
con soporte de índices geoespaciales 2dsphere.

Características:
- Conexión segura a MongoDB Atlas
- Lectura de archivos GeoJSON locales
- Validación de geometrías GeoJSON
- Creación automática de índices 2dsphere
- Manejo robusto de errores
- Logging detallado

Autor: Forest Guardian RL Team
Fecha: Enero 2026
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
import logging
from datetime import datetime

try:
    from pymongo import MongoClient, GEOSPHERE
    from pymongo.errors import ConnectionFailure, BulkWriteError, DuplicateKeyError
except ImportError:
    print("❌ Error: pymongo no está instalado")
    print("   Instala con: pip install pymongo")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class GeoJSONUploader:
    """
    Clase para cargar datos GeoJSON a MongoDB Atlas con índices geoespaciales.
    """
    
    def __init__(self, uri: str, database_name: str = "forest_guardian", 
                 collection_name: str = "mapa_forestal"):
        """
        Inicializa el uploader con la configuración de MongoDB.
        
        Args:
            uri: URI de conexión a MongoDB Atlas
            database_name: Nombre de la base de datos
            collection_name: Nombre de la colección
        """
        self.uri = uri
        self.database_name = database_name
        self.collection_name = collection_name
        self.client = None
        self.db = None
        self.collection = None
    
    def connect(self) -> bool:
        """
        Establece conexión con MongoDB Atlas.
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        try:
            logger.info("🔌 Conectando a MongoDB Atlas...")
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            
            # Verificar conexión
            self.client.admin.command('ping')
            
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            
            logger.info(f"✅ Conectado exitosamente a la base de datos '{self.database_name}'")
            logger.info(f"📁 Usando colección: '{self.collection_name}'")
            return True
            
        except ConnectionFailure as e:
            logger.error(f"❌ Error de conexión a MongoDB Atlas: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error inesperado al conectar: {e}")
            return False
    
    def load_geojson(self, file_path: str) -> Dict[str, Any]:
        """
        Carga y valida un archivo GeoJSON.
        
        Args:
            file_path: Ruta al archivo GeoJSON
            
        Returns:
            Diccionario con los datos GeoJSON
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            json.JSONDecodeError: Si el archivo no es JSON válido
            ValueError: Si la estructura GeoJSON es inválida
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        logger.info(f"📖 Leyendo archivo: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validar estructura básica de GeoJSON
        if 'type' not in data:
            raise ValueError("El archivo no contiene un campo 'type'")
        
        if data['type'] not in ['FeatureCollection', 'Feature']:
            raise ValueError(f"Tipo de GeoJSON no soportado: {data['type']}")
        
        logger.info(f"✅ Archivo GeoJSON válido cargado")
        
        if data['type'] == 'FeatureCollection':
            features_count = len(data.get('features', []))
            logger.info(f"📊 Total de features encontradas: {features_count}")
        
        return data
    
    def validate_geometry(self, geometry: Dict[str, Any]) -> bool:
        """
        Valida que una geometría sea GeoJSON válida.
        
        Args:
            geometry: Diccionario con la geometría
            
        Returns:
            True si la geometría es válida
        """
        if not isinstance(geometry, dict):
            return False
        
        if 'type' not in geometry or 'coordinates' not in geometry:
            return False
        
        valid_types = ['Point', 'LineString', 'Polygon', 'MultiPoint', 
                      'MultiLineString', 'MultiPolygon', 'GeometryCollection']
        
        return geometry['type'] in valid_types
    
    def prepare_documents(self, geojson_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Prepara los documentos para insertar en MongoDB con estructura optimizada.
        
        Args:
            geojson_data: Datos GeoJSON cargados
            
        Returns:
            Lista de documentos listos para insertar
        """
        documents = []
        
        # Manejar FeatureCollection
        if geojson_data['type'] == 'FeatureCollection':
            features = geojson_data.get('features', [])
        # Manejar Feature individual
        elif geojson_data['type'] == 'Feature':
            features = [geojson_data]
        else:
            logger.warning(f"⚠️  Tipo de GeoJSON no soportado: {geojson_data['type']}")
            return documents
        
        logger.info(f"🔄 Preparando {len(features)} documentos...")
        
        for idx, feature in enumerate(features):
            try:
                # Validar que sea una Feature
                if feature.get('type') != 'Feature':
                    logger.warning(f"⚠️  Feature {idx} no es de tipo 'Feature', omitiendo...")
                    continue
                
                geometry = feature.get('geometry')
                properties = feature.get('properties', {})
                
                # Validar geometría
                if not self.validate_geometry(geometry):
                    logger.warning(f"⚠️  Geometría inválida en feature {idx}, omitiendo...")
                    continue
                
                # Crear documento con estructura optimizada para MongoDB
                document = {
                    # Campo de geometría con índice 2dsphere
                    'location': {
                        'type': geometry['type'],
                        'coordinates': geometry['coordinates']
                    },
                    
                    # Propiedades del feature
                    'properties': properties,
                    
                    # Metadatos adicionales
                    'metadata': {
                        'uploaded_at': datetime.utcnow(),
                        'source': 'geojson_upload',
                        'feature_id': feature.get('id', f"feature_{idx}")
                    }
                }
                
                # Agregar campos adicionales de propiedades al nivel raíz para consultas
                if 'nombre' in properties or 'name' in properties:
                    document['nombre'] = properties.get('nombre') or properties.get('name')
                
                if 'area' in properties:
                    document['area'] = properties['area']
                
                if 'tipo' in properties or 'type' in properties:
                    document['tipo'] = properties.get('tipo') or properties.get('type')
                
                documents.append(document)
                
            except Exception as e:
                logger.error(f"❌ Error procesando feature {idx}: {e}")
                continue
        
        logger.info(f"✅ {len(documents)} documentos preparados exitosamente")
        return documents
    
    def create_geospatial_index(self) -> bool:
        """
        Crea un índice 2dsphere en el campo 'location' para consultas geoespaciales.
        
        Returns:
            True si el índice fue creado exitosamente
        """
        try:
            logger.info("🔧 Creando índice geoespacial 2dsphere...")
            
            # Crear índice 2dsphere en el campo location
            index_name = self.collection.create_index(
                [("location", GEOSPHERE)],
                name="location_2dsphere"
            )
            
            logger.info(f"✅ Índice '{index_name}' creado exitosamente")
            
            # Crear índices adicionales para consultas comunes
            try:
                self.collection.create_index("nombre", name="nombre_index")
                logger.info("✅ Índice de nombre creado")
            except:
                pass
            
            try:
                self.collection.create_index("tipo", name="tipo_index")
                logger.info("✅ Índice de tipo creado")
            except:
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creando índices: {e}")
            return False
    
    def insert_documents(self, documents: List[Dict[str, Any]], 
                        clear_collection: bool = False) -> int:
        """
        Inserta los documentos en la colección de MongoDB.
        
        Args:
            documents: Lista de documentos a insertar
            clear_collection: Si True, limpia la colección antes de insertar
            
        Returns:
            Número de documentos insertados exitosamente
        """
        if not documents:
            logger.warning("⚠️  No hay documentos para insertar")
            return 0
        
        try:
            # Limpiar colección si se solicita
            if clear_collection:
                logger.warning("⚠️  Limpiando colección existente...")
                result = self.collection.delete_many({})
                logger.info(f"🗑️  {result.deleted_count} documentos eliminados")
            
            # Insertar documentos
            logger.info(f"📤 Insertando {len(documents)} documentos...")
            
            result = self.collection.insert_many(documents, ordered=False)
            inserted_count = len(result.inserted_ids)
            
            logger.info(f"✅ {inserted_count} documentos insertados exitosamente")
            return inserted_count
            
        except BulkWriteError as e:
            # Manejar inserciones parciales
            inserted_count = e.details['nInserted']
            logger.warning(f"⚠️  Inserción parcial: {inserted_count} documentos insertados")
            logger.warning(f"   Errores: {len(e.details['writeErrors'])}")
            return inserted_count
            
        except Exception as e:
            logger.error(f"❌ Error insertando documentos: {e}")
            return 0
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la colección.
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            stats = {
                'total_documents': self.collection.count_documents({}),
                'indexes': list(self.collection.list_indexes()),
                'sample_document': self.collection.find_one()
            }
            return stats
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}
    
    def print_summary(self):
        """
        Imprime un resumen de la colección.
        """
        logger.info("\n" + "="*70)
        logger.info("📊 RESUMEN DE LA COLECCIÓN")
        logger.info("="*70)
        
        stats = self.get_collection_stats()
        
        if stats:
            logger.info(f"📁 Base de datos: {self.database_name}")
            logger.info(f"📚 Colección: {self.collection_name}")
            logger.info(f"📄 Total de documentos: {stats['total_documents']}")
            
            logger.info(f"\n🔍 Índices:")
            for idx in stats['indexes']:
                logger.info(f"   - {idx['name']}: {idx.get('key', {})}")
            
            if stats['sample_document']:
                logger.info(f"\n📝 Ejemplo de documento:")
                sample = stats['sample_document']
                logger.info(f"   - ID: {sample.get('_id')}")
                logger.info(f"   - Nombre: {sample.get('nombre', 'N/A')}")
                logger.info(f"   - Tipo geometría: {sample.get('location', {}).get('type', 'N/A')}")
        
        logger.info("="*70 + "\n")
    
    def close(self):
        """
        Cierra la conexión con MongoDB.
        """
        if self.client:
            self.client.close()
            logger.info("🔌 Conexión cerrada")


def main():
    """
    Función principal del script.
    """
    print("\n" + "="*70)
    print("🌲 FOREST GUARDIAN RL - GEOJSON TO MONGODB ATLAS UPLOADER 🌲")
    print("="*70 + "\n")
    
    # ========================================================================
    # CONFIGURACIÓN - MODIFICA ESTOS VALORES
    # ========================================================================
    
    # URI de conexión a MongoDB Atlas (obtener desde Atlas UI)
    MONGODB_URI = "mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority"
    
    # Ruta al archivo GeoJSON local
    GEOJSON_FILE = "zonas_forestales.geojson"
    
    # Nombre de la base de datos
    DATABASE_NAME = "forest_guardian"
    
    # Nombre de la colección
    COLLECTION_NAME = "mapa_forestal"
    
    # Limpiar colección antes de insertar
    CLEAR_COLLECTION = False
    
    # ========================================================================
    
    # Validar que se haya configurado la URI
    if "<username>" in MONGODB_URI or "<password>" in MONGODB_URI:
        logger.error("❌ Error: Debes configurar tu URI de MongoDB Atlas")
        logger.info("\n📖 Para obtener tu URI:")
        logger.info("   1. Ingresa a https://cloud.mongodb.com/")
        logger.info("   2. Ve a tu cluster → Connect → Connect your application")
        logger.info("   3. Copia la URI y reemplaza <username> y <password>")
        logger.info("   4. Modifica la variable MONGODB_URI en este script\n")
        sys.exit(1)
    
    # Validar que el archivo GeoJSON exista
    if not Path(GEOJSON_FILE).exists():
        logger.error(f"❌ Error: Archivo no encontrado: {GEOJSON_FILE}")
        logger.info("\n📖 Coloca tu archivo GeoJSON en el mismo directorio que este script")
        logger.info("   o modifica la variable GEOJSON_FILE con la ruta correcta\n")
        sys.exit(1)
    
    # Crear instancia del uploader
    uploader = GeoJSONUploader(
        uri=MONGODB_URI,
        database_name=DATABASE_NAME,
        collection_name=COLLECTION_NAME
    )
    
    try:
        # 1. Conectar a MongoDB Atlas
        if not uploader.connect():
            logger.error("❌ No se pudo establecer conexión con MongoDB Atlas")
            sys.exit(1)
        
        # 2. Cargar archivo GeoJSON
        geojson_data = uploader.load_geojson(GEOJSON_FILE)
        
        # 3. Preparar documentos
        documents = uploader.prepare_documents(geojson_data)
        
        if not documents:
            logger.error("❌ No se pudieron preparar documentos válidos")
            sys.exit(1)
        
        # 4. Insertar documentos
        inserted = uploader.insert_documents(documents, clear_collection=CLEAR_COLLECTION)
        
        if inserted == 0:
            logger.error("❌ No se insertaron documentos")
            sys.exit(1)
        
        # 5. Crear índice geoespacial
        uploader.create_geospatial_index()
        
        # 6. Mostrar resumen
        uploader.print_summary()
        
        print("✅ ¡Proceso completado exitosamente!")
        print("\n💡 Próximos pasos:")
        print("   1. Verifica los datos en MongoDB Atlas Compass")
        print("   2. Prueba consultas geoespaciales con $near o $geoWithin")
        print("   3. Integra las consultas en Forest Guardian RL\n")
        
    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error al parsear JSON: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"❌ {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        uploader.close()


if __name__ == "__main__":
    main()
