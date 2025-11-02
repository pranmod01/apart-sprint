# AI Capability Terrain Map

An interactive 3D early warning system that maps AI capabilities as literal terrain - where mountain peaks represent mastered abilities, rising hills show emerging skills, and red sinkholes reveal tasks that should be trivial but AI inexplicably fails at.

Building on real-time benchmark data from Epoch AI and Papers With Code, the system monitors capability progression and detects anomalous jumps (e.g., coding ability suddenly jumping 40%). Users can track early warning signals - benchmark acceleration, multi-model convergence, and leading indicators - to anticipate breakthroughs 3-6 months before they materialize.

**The ML component:** Anomaly detection models flag capability jumps using statistical methods on historical trends, sigmoid-based forecasting predicts future terrain evolution with uncertainty bands, and a Random Forest classifier predicts whether new tasks will become persistent sinkholes - providing actionable early warnings for researchers and policymakers.

**The SWE component:** Node.js + Express API connecting PostgreSQL database to React + Three.js frontend. Automated ETL pipeline ingesting Epoch/Papers With Code data, real-time alert generation system, notification infrastructure for capability jumps, and integration endpoints serving ML predictions. Deployed on Vercel (frontend) + Railway (backend + database).

**Novel Contributions:**
- **Sinkhole Discovery** - First systematic tracking of tasks AI should handle but can't (e.g., counting letters, basic spatial reasoning)
- **Anomaly Detection** - Automated alerts when capabilities jump unexpectedly, enabling rapid institutional response
- **Early Warning Signals** - Multi-signal system predicting breakthroughs before they occur
- **Spatial Visualization** - 3D terrain reveals capability clusters and gaps invisible in traditional benchmark charts

**Impact:** Enables researchers, policymakers, and developers to monitor AI progress in real-time, receive alerts on capability acceleration, and anticipate transformative breakthroughs - directly addressing Track 3's focus on early warning systems for rapid response to AI advancement.

# AI Capability Terrain Map

AI Capability Terrain Map is an interactive 3D early warning system that visualizes AI capabilities as literal terrain — with mountain peaks representing mastered abilities, rising hills showing emerging skills, and red sinkholes exposing tasks that AI systems should handle easily but consistently fail at.

The system integrates real-time benchmark data from Epoch AI to monitor capability progression and forecast future developments across more than 30 distinct AI domains. By combining empirical performance data with logistic growth modeling and Monte Carlo uncertainty quantification, it produces granular, capability-specific forecasts with confidence intervals — moving beyond generic “AGI timelines” to concrete capability trajectories.

**Forecasting and Analysis Pipeline**

The forecasting component models benchmark performance over time using logistic growth curves fitted to historical data. Each forecast includes a 95% confidence interval, generated via Monte Carlo simulation, allowing users to account for uncertainty in future capability trajectories. The system also detects capability sinkholes — areas where progress stalls despite strong performance in related domains — revealing blind spots in current AI architectures and training paradigms.

**Visualization and Interaction**

The 3D interface, built with React and Three.js, translates forecast data into an intuitive spatial landscape. Users can explore capability clusters, rising trends, and sinkholes in real time. Each terrain region dynamically updates as new benchmark results are integrated, making the map both an analytic and exploratory tool for researchers and policymakers.

**Novel Contributions**

-**Granular Capability Forecasting:** Predicts performance trajectories and uncertainty bounds for dozens of AI capabilities.

-**Sinkhole Detection:** Identifies domains of persistent underperformance, guiding targeted research and safety investigation.

-**Uncertainty-Aware Modeling:** Provides confidence intervals to reduce overconfidence in capability forecasts.

-**Interactive Terrain Mapping:** Offers an interpretable, multidimensional visualization of AI progress and gaps.

**Impact**

The AI Capability Terrain Map enables transparent, data-driven insight into AI progress. By highlighting where and how capabilities advance — and where they stagnate — it supports more informed decisions around AI safety, policy, and governance, equipping stakeholders with early warning signals of transformative breakthroughs or emerging risks.

<img width="1900" height="911" alt="Screenshot 2025-11-02 at 2 51 39 PM" src="https://github.com/user-attachments/assets/bcfcc0c3-9e75-4413-9f33-e7136d87f7b3" />

---

## Getting Started

### Prerequisites
- [Node.js](https://nodejs.org/) (v18 or later)
- npm or yarn

### Installation
```bash
# Clone the repository
git clone https://github.com/<your-username>/<repo-name>.git

# Navigate to the frontend
```bash
cd <repo-name>/frontend

# Install dependencies
```bash
npm install

Running the Development Server
```bash
npm run dev

Then open your browser and visit http://localhost:5173
 (or the port shown in your terminal) to view the interactive terrain map.
