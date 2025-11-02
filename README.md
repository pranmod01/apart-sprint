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

<img width="1900" height="911" alt="Screenshot 2025-11-02 at 2 51 39 PM" src="https://github.com/user-attachments/assets/bcfcc0c3-9e75-4413-9f33-e7136d87f7b3" />
