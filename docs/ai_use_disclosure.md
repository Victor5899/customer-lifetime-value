# AI-use disclosure

**Project:** Customer Lifetime Value and Segmentation Engine
**Dataset:** Olist Brazilian E-Commerce public dataset
**Tool:** Cursor, using its coding agent

Parts of this project were prepared with Cursor's coding agent. The agent drafted and revised notebook code, the Week 6 extract script, validation checks, and project documentation, including the Week 8 QA report and the Week 8 performance report.

The agent does not replace the measured results. Counts, joins, revenue, the CLV score, and the Week 7 pulse in those reports were recomputed from the files in `data/`. The public Olist tables are stored locally. No private customer system and no API credential were connected for this work.

The performance pass did not change the CLV formula, the segment thresholds, the delivered-revenue definition, the geolocation bounding box, or the forecast method. Where code changed, the replacement was compared with the previous result on the full file. The comparison is in `docs/week8_performance_and_packaging_report.md`.

The person submitting the project is responsible for the figures, the definitions, and what is said about them in the viva. The agent can draft prose and code. It is not the author of the business rules.
