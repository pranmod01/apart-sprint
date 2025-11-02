import { create } from 'zustand';

export const useTerrainStore = create((set) => ({
  capabilityData: null,
  selectedCapability: null,
  filterCategory: null,
  showSinkholes: true,
  showForecastNodes: true,
  showLabels: true,

  loadCapabilityData: async () => {
    try {
      // Load capability heights data
      const response = await fetch('/data/intermediate/capability_heights.json');
      const data = await response.json();

      // Transform data for rendering
      const capabilities = {};
      Object.entries(data.all || data).forEach(([key, value]) => {
        if (value.x !== undefined && value.y !== undefined) {
          capabilities[key] = value;
        }
      });

      set({ capabilityData: capabilities });
    } catch (error) {
      console.error('Failed to load capability data:', error);
      // Fallback with empty data
      set({ capabilityData: {} });
    }
  },

  setSelectedCapability: (capability) => set({ selectedCapability: capability }),
  setFilterCategory: (category) => set({ filterCategory: category }),
  toggleSinkholes: () => set((state) => ({ showSinkholes: !state.showSinkholes })),
  toggleForecastNodes: () => set((state) => ({ showForecastNodes: !state.showForecastNodes })),
  toggleLabels: () => set((state) => ({ showLabels: !state.showLabels })),
}));
