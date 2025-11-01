# AI Capability Terrain Map

An interactive 3D visualization that maps the landscape of AI capabilities as literal terrain - where mountain peaks represent mastered abilities, rising hills show emerging skills, and mysterious red sinkholes reveal tasks that should be trivial but AI inexplicably fails at.

Building on benchmark data from Epoch AI and Papers With Code, users can scroll through time (2020-2025) to observe the terrain evolve, hover over regions to view benchmark details, and click on sinkholes to discover surprising failures, such as "counting letters in 'strawberry'".

**The ML component:** Machine learning models forecast which capabilities will emerge next, predict future terrain evolution with uncertainty bands, and classify whether new tasks will become sinkholes—turning raw benchmark data into actionable AI progress predictions.

**The SWE component:** Node.js API layer connecting PostgreSQL database (historical benchmarks, test results) to React + Three.js frontend. Automated ETL pipeline for Epoch/Papers With Code data, live model testing via OpenAI/Anthropic APIs, and integration endpoints serving ML predictions. Deployed on Vercel (frontend) + Railway (backend).

**The Data Eng component:** an ETL pipeline that aggregates benchmarks into semantic capabilities, an automated testing infrastructure for sinkhole discovery, and real-time data validation to ensure terrain accuracy across 30+ AI capability domains.
Impact: Provides researchers, policymakers, and developers an intuitive way to understand AI's current limitations, track capability acceleration, and forecast transformative milestones - with a novel focus on persistent failure modes that traditional benchmarks miss.
