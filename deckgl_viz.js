/**
 * ForestGuardian Deck.gl Visualization Configuration
 * This file defines the layers used to render the 3D Forest Fire environment.
 */

const INITIAL_VIEW_STATE = {
  latitude: 37.75, // Virtual coordinates
  longitude: -122.4,
  zoom: 11,
  bearing: 0,
  pitch: 45
};

// Color Palettes
const FIRE_COLOR = [255, 69, 0, 200]; // Orange-Red
const TREE_COLOR = [34, 139, 34, 255]; // Forest Green
const AGENT_COLOR = [0, 255, 255, 255]; // Cyan

function getLayers(data) {
  // data should contain: { topography: [], fire: [], agents: [] }

  return [
    // 1. Terrain Layer (The Environment Base)
    new deck.TerrainLayer({
      id: 'terrain-layer',
      data: data.topography, // URL or Data array
      elevationDecoder: {
        rScaler: 2,
        gScaler: 0,
        bScaler: 0,
        offset: 0
      },
      texture: 'texture.png', // Optional texture
      wireframe: false,
      color: [255, 255, 255]
    }),

    // 2. Fire Layer (Hexagon or Column Layer for intensity)
    new deck.ColumnLayer({
      id: 'fire-layer',
      data: data.fire_points,
      diskResolution: 12,
      radius: 20,
      extruded: true,
      pickable: true,
      elevationScale: 10,
      getPosition: d => d.position, // [lon, lat]
      getFillColor: d => [255, d.intensity * 255, 0, 200], // Red to Yellow based on intensity
      getElevation: d => d.intensity * 100
    }),

    // 3. Agent Layer (Icons or PointClouds)
    new deck.IconLayer({
      id: 'agent-layer',
      data: data.agents,
      pickable: true,
      iconAtlas: 'https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/icon-atlas.png',
      iconMapping: {
        marker: { x: 0, y: 0, width: 128, height: 128, mask: true }
      },
      getIcon: d => 'marker',
      sizeScale: 15,
      getPosition: d => d.position,
      getColor: AGENT_COLOR
    })
  ];
}
