import { create } from 'zustand';

export const useTerrainStore = create((set) => ({
  capabilityData: null,
  selectedCapability: null,
  filterCategory: null,
  filterModel: null,
  showSinkholes: true,
  showForecastNodes: true,
  showLabels: true,
  cameraMode: 'topdown', // 'topdown' or 'landscape'
  currentYear: 2025,
  availableYears: [2019, 2020, 2021, 2022, 2023, 2024, 2025],
  availableCategories: ['coding', 'reasoning', 'knowledge', 'spatial', 'language', 'physical'],
  availableModels: [
    'All',
    'OpenAI',
    'Anthropic',
    'Google',
    'Google DeepMind',
    'DeepMind',
    'Meta',
    'Meta AI',
    'Microsoft',
    'xAI',
    'DeepSeek',
    'Alibaba',
    'Baichuan',
    'Zhipu AI',
    'Moonshot',
    '01.AI',
    'Mistral AI',
    'Cohere',
    'Inflection AI',
    'Hugging Face',
    'Allen Institute for AI',
    'EleutherAI'
  ],

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
  setFilterModel: (model) => set({ filterModel: model }),
  setCurrentYear: (year) => set({ currentYear: year }),
  toggleSinkholes: () => set((state) => ({ showSinkholes: !state.showSinkholes })),
  toggleForecastNodes: () => set((state) => ({ showForecastNodes: !state.showForecastNodes })),
  toggleLabels: () => set((state) => ({ showLabels: !state.showLabels })),
  toggleCameraMode: () => set((state) => ({
    cameraMode: state.cameraMode === 'topdown' ? 'landscape' : 'topdown'
  })),
}));
