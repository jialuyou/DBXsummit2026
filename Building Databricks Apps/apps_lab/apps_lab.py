# Databricks notebook source
# MAGIC %md
# MAGIC # Ship It! Code, Deploy, and Scale Your First Databricks App
# MAGIC
# MAGIC **Authors**
# MAGIC - Athulya Ramamoorthy, Product Specialist, Apps
# MAGIC - Mike Lo, Solution Architect

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC
# MAGIC ## Introduction
# MAGIC
# MAGIC In this hands-on session, you'll leverage coding agents (ucode), Databricks Agent Skills, and AppKit to build and deploy a production-ready Databricks App. Before we get started, here are some tools we'll be using today:
# MAGIC - **[UCode](https://github.com/databricks/ucode)** is Databricks’ toolkit for connecting AI coding agents to Databricks development workflows. It helps agents understand how to work with Databricks resources, environments, and project patterns so they can be more effective when building, modifying, and deploying apps.
# MAGIC - **[Databricks Agent Skills](https://github.com/databricks/agent-skills)** are structured instructions and project context that help an AI coding agent understand how to work effectively with a Databricks app codebase. They provide guidance on things like framework conventions, project structure, implementation patterns, and common workflows so the agent can generate better code with less prompting.
# MAGIC - **[AppKit](https://github.com/databricks/appkit)** is Databricks’ open-source TypeScript and React toolkit for building data and AI applications on Databricks. It gives you a set of reusable UI patterns, components, and integration helpers so you can move faster when building app experiences on top of Databricks data, AI, and services.
# MAGIC
# MAGIC What's pre-provisioned for you for this workshop:
# MAGIC - A Databricks workspace
# MAGIC - A Lakebase instance (`apps-workshop`) pre-loaded with two datasets
# MAGIC - Databricks ucode and agent skills with knowledge of AppKit
# MAGIC
# MAGIC Here are some suggested scenarios for you to build apps and familiarize with the app framework. 
# MAGIC
# MAGIC | Scenario | Scenario | What you'll build |
# MAGIC |---|---|---|
# MAGIC | 1 | 511 SF Bay Transit | Live disruption dashboard with alert feed, route search, and user watchlist |
# MAGIC | 2 | SF Film Locations | Film tour explorer with neighbourhood filter, map pins, and personal tour planner |
# MAGIC | 3 | Workshop Networking App | Get creative and use the workshop to network with like minded folk! |
# MAGIC | 4 | Choose Your Own Adventure | Follow our prompt guide and create your own app using AppKit |
# MAGIC
# MAGIC ## 
# MAGIC You can build one end-to-end, or combine multiple datasets or generate your synthetic data with Genie code for something more unique.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data: What's in Lakebase
# MAGIC
# MAGIC The Lakebase database (`databricks_postgres`) has the following tables. All are available to all users — the `watchlist` and `tour_stops` tables are per-user write-enabled tables for saving personal preferences.
# MAGIC
# MAGIC **Useful exploration queries to run in a notebook before building:**
# MAGIC
# MAGIC ```sql
# MAGIC -- Transit: what's currently disrupted?
# MAGIC SELECT agency_name, header_text, severity
# MAGIC FROM service_alerts WHERE is_active = true;
# MAGIC
# MAGIC -- Transit: routes for a specific agency
# MAGIC SELECT route_id, short_name, long_name
# MAGIC FROM routes WHERE agency_id = 'BA' LIMIT 10;
# MAGIC
# MAGIC -- Films: what's been shot in each neighbourhood?
# MAGIC SELECT neighborhood, COUNT(*) as films
# MAGIC FROM film_locations
# MAGIC GROUP BY neighborhood ORDER BY films DESC;
# MAGIC
# MAGIC -- Films: all locations for a specific film
# MAGIC SELECT title, location_name, lat, lon
# MAGIC FROM film_locations WHERE title = 'Vertigo';
# MAGIC ```
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Scenario 1: Transit Disruption Dashboard
# MAGIC
# MAGIC Build a dashboard that shows live Bay Area transit disruptions, lets commuters search routes, and saves a personal watchlist.
# MAGIC
# MAGIC **Features to aim for:**
# MAGIC - Live alert feed from BART, Muni, Caltrain, AC Transit — filterable by agency
# MAGIC - Route and stop browser
# MAGIC - Personal watchlist — save routes you care about, persisted per user
# MAGIC - Incident log
# MAGIC
# MAGIC ### Dataset — 511 SF Bay Transit
# MAGIC
# MAGIC | Table | What it contains |
# MAGIC |---|---|
# MAGIC | `agencies` | Transit operators: BART, Muni, Caltrain, AC Transit (4 rows) |
# MAGIC | `routes` | All lines with short name, long name, type, and colour (~212 rows) |
# MAGIC | `stops` | Stations and stops with lat/lon coordinates (~8,346 rows) |
# MAGIC | `service_alerts` | Live disruptions and notices from 511 SF Bay (~60–80 rows, refreshed) |
# MAGIC | `incidents` | Synthetic operational incidents for demo purposes (10 rows) |
# MAGIC | `watchlist` | Per-user saved routes — empty, write-enabled, yours to populate |
# MAGIC
# MAGIC ### How to build it
# MAGIC
# MAGIC **Step 1 — Scaffold the app**
# MAGIC
# MAGIC Open a terminal and run:
# MAGIC
# MAGIC ```bash
# MAGIC databricks apps init
# MAGIC ```
# MAGIC
# MAGIC This creates your AppKit project. It comes with working examples of Lakebase connection, queries, and auth already wired — the agent uses these as a reference when building your app.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC **Step 2 — Start a conversation with your coding agent**
# MAGIC
# MAGIC The recommended approach is to let the agent interview you. This gives you better results than one-shotting it:
# MAGIC
# MAGIC ```
# MAGIC I want to build a Databricks app connected to the Lakebase instance apps-workshop. Use the users group role to access Lakebase.
# MAGIC Run `databricks apps init` to scaffold it, then interview me step by step
# MAGIC about what I want to build before writing any code.
# MAGIC ```
# MAGIC
# MAGIC The agent will ask you questions — what features do you want, what should users see first, how should the watchlist work, and so on. Answer naturally. The more context you give, the better the result.
# MAGIC
# MAGIC **Note**: Suggest using the users group role in your prompt when accessing the Lakeflow instance.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC **Step 3 — Describe what you want, not how to build it**
# MAGIC
# MAGIC AppKit handles the Lakebase connection, auth, query types, and API wiring automatically. Your job is to describe the experience:
# MAGIC
# MAGIC > *"Show a feed of active service alerts. Users should be able to filter by agency. Each alert should show the agency name, what's happening, and how severe it is."*
# MAGIC
# MAGIC > *"Add a watchlist — users can save routes they care about and see them in a personal panel. Each user should only see their own saved routes."*
# MAGIC
# MAGIC > *"Add a way to report a new incident — a simple form with agency, location, and description."*
# MAGIC
# MAGIC Iterate from there. Ask the agent to add, change, or simplify features as you go.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC **Step 4 — Deploy**
# MAGIC
# MAGIC ```bash
# MAGIC databricks apps deploy
# MAGIC ```
# MAGIC
# MAGIC Your app gets a live URL on `databricksapps.com`.
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Scenario 2: SF Film Tour Explorer
# MAGIC
# MAGIC Build an app that lets you explore where San Francisco's most famous films were shot, plan a personal tour, and filter by neighbourhood.
# MAGIC
# MAGIC **Features to aim for:**
# MAGIC - Film browser — search by title, neighbourhood, year, or director
# MAGIC - Location detail — filming spot, cast, and director for each entry
# MAGIC - Personal tour planner — save locations to a tour list, persisted per user
# MAGIC - Neighbourhood view — browse films grouped by SF neighbourhood
# MAGIC
# MAGIC ### Dataset 2 — SF Film Locations
# MAGIC
# MAGIC | Table | What it contains |
# MAGIC |---|---|
# MAGIC | `film_locations` | SF filming locations: title, year, neighbourhood, director, cast, lat/lon (~1,400 rows) |
# MAGIC | `tour_stops` | Per-user saved tour stops — empty, write-enabled, yours to populate |
# MAGIC
# MAGIC ### How to build it
# MAGIC
# MAGIC **Step 1 — Scaffold**
# MAGIC
# MAGIC ```bash
# MAGIC databricks apps init
# MAGIC ```
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC **Step 2 — Let the agent interview you**
# MAGIC
# MAGIC ```
# MAGIC I want to build a Databricks app using the Lakebase instance apps-workshop.
# MAGIC The database has a film_locations table with SF filming locations and a tour_stops
# MAGIC table for saving personal tour plans.
# MAGIC Run `databricks apps init` to scaffold it, then interview me about what I want to build.
# MAGIC ```
# MAGIC
# MAGIC Answer the agent's questions. It will ask about layout, which filters matter, how the tour planner should work, whether you want a map, and more. The conversation shapes the app.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC **Step 3 — Describe features as you go**
# MAGIC
# MAGIC > *"Show a browsable list of filming locations. I want to filter by neighbourhood and search by film title."*
# MAGIC
# MAGIC > *"Each location should show the film title, year, director, and where it was shot. If there are coordinates, show a map pin."*
# MAGIC
# MAGIC > *"Add a tour planner — I can add locations to my personal tour list and see them in a separate panel. My tour should be saved so it persists across sessions."*
# MAGIC
# MAGIC > *"Group the neighbourhood view so I can see all the films shot in, say, the Mission District at once."*
# MAGIC
# MAGIC Refine as you go. You don't need to describe everything at once.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC **Step 4 — Deploy**
# MAGIC
# MAGIC ```bash
# MAGIC databricks apps deploy
# MAGIC ```
# MAGIC

# COMMAND ----------

Scenario 3: Workshop Networking App

# COMMAND ----------

# MAGIC %md
# MAGIC ## Stretch Goals
# MAGIC
# MAGIC Finished the core app? Try one of these.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Add an AI feature using Foundation Model APIs
# MAGIC
# MAGIC Add a button that calls a Databricks-hosted language model — no external API key needed, the model runs in your workspace.
# MAGIC
# MAGIC **Ideas for transit:**
# MAGIC - "Summarise today's disruptions" — one-paragraph plain-English summary of all active alerts
# MAGIC - "Should I take BART or Muni right now?" — route recommendation based on current alerts
# MAGIC - "What does this alert mean?" — explain technical service alert language in plain English
# MAGIC
# MAGIC **Ideas for film tour:**
# MAGIC - "Tell me about this filming location" — short description of the neighbourhood and why it might have been chosen
# MAGIC - "Plan my tour route" — suggest a walking order for saved tour stops
# MAGIC - "Write a caption for this spot" — generate a fun social media caption for a filming location
# MAGIC
# MAGIC **How to ask for it:**
# MAGIC > *"Add a button on each alert that calls a Databricks language model to explain the disruption in plain English. Use the Foundation Model API built into this workspace — no external keys."*
# MAGIC
# MAGIC > *"Add a 'Summarise my tour' button that sends my saved stops to an LLM and returns a short itinerary description."*
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Add a Genie chat panel
# MAGIC
# MAGIC Let users ask natural language questions about the data without leaving the app.
# MAGIC
# MAGIC > *"Add a Genie chat sidebar using the AppKit Genie plugin. Users should be able to ask questions like 'which agency has the most active alerts?' or 'what films were shot near the Embarcadero?' and get answers in natural language."*
# MAGIC
# MAGIC Ask a helper for the Genie room ID to use for this workspace.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Combine both datasets
# MAGIC
# MAGIC The most interesting builds use both datasets together:
# MAGIC
# MAGIC - **Transit-aware film tour** — show filming locations with live transit alerts for the routes nearest to each spot
# MAGIC - **Neighbourhood explorer** — for each SF neighbourhood, show both films shot there and current transit status
# MAGIC - **"Can I get there right now?"** — given a filming location, show nearest stops and any active alerts affecting them
# MAGIC
# MAGIC > *"Extend this app to combine the film locations and transit data. When I click a filming location, show me the nearest transit stops and whether any alerts currently affect them."*
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### More ideas
# MAGIC
# MAGIC - Auto-refresh alerts every 60 seconds so the feed stays live without reloading
# MAGIC - A severity heatmap using stop coordinates — visualise where disruptions are concentrated
# MAGIC - Export tour as a shareable link or PDF
# MAGIC - Click a director and see every SF location they've filmed at
# MAGIC - A leaderboard tracking which user has the longest watchlist
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC # Appendix

# COMMAND ----------

# MAGIC %md
# MAGIC ### Best Practices for using AppKit & Databricks Agent Skills
# MAGIC
# MAGIC These tips come from the awesome Databricks AppKit team and from our collective experience using Appkit. They'll save you time and improve your experience with Databricks apps
# MAGIC
# MAGIC #### Ask the agent to interview you
# MAGIC
# MAGIC Asking the agent to interview you before writing code consistently produces better results than describing everything upfront. Two good patterns:
# MAGIC
# MAGIC **Scaffold first, then interview:**
# MAGIC ```
# MAGIC Run `databricks apps init` connected to Lakebase instance apps-workshop.
# MAGIC Once scaffolding is done, interview me step by step about what I want to build.
# MAGIC ```
# MAGIC
# MAGIC **Interview first, then scaffold:**
# MAGIC ```
# MAGIC I want to build a Databricks app. Interview me about what I want to build
# MAGIC before writing any code. I'll use Lakebase instance apps-workshop.
# MAGIC ```
# MAGIC
# MAGIC The reason scaffolding first helps: `databricks apps init` installs the AppKit plugin manifest, which teaches the agent how the framework works before it starts asking questions. The quality of the interview improves.
# MAGIC
# MAGIC #### Tell the agent which resources to use
# MAGIC
# MAGIC The agent can discover resources on its own, but telling it upfront is much faster:
# MAGIC
# MAGIC ```
# MAGIC Build a Databricks app connected to Lakebase endpoint <ENDPOINT>
# MAGIC or warehouse <WAREHOUSE_ID>.
# MAGIC ```
# MAGIC
# MAGIC #### Describe what users experience, not how to build it
# MAGIC
# MAGIC AppKit handles auth, Lakebase connections, query types, and API wiring automatically. Your prompts should describe the experience:
# MAGIC
# MAGIC ✅ *"Show a feed of active alerts, filterable by agency"*  
# MAGIC ✅ *"Each user should only see their own saved routes"*  
# MAGIC ✅ *"Add a button that refreshes the data"*  
# MAGIC
# MAGIC ❌ *"Create a GET endpoint that queries service_alerts where is_active = true and returns agency_name, header_text..."*
# MAGIC
# MAGIC The agent knows how to translate experience descriptions into AppKit code. Over-specifying the technical implementation can actually confuse it.
# MAGIC
# MAGIC #### Iterate — don't try to build everything in one prompt
# MAGIC
# MAGIC Build one feature at a time. Deploy early. See it working, then add the next thing:
# MAGIC
# MAGIC 1. *"Build a basic alert feed"* → deploy → see it live
# MAGIC 2. *"Add an agency filter"* → deploy
# MAGIC 3. *"Add a watchlist"* → deploy
# MAGIC
# MAGIC Small prompts, fast feedback loop, better results.

# COMMAND ----------

# MAGIC %md
# MAGIC ### What AppKit handles so you don't have to
# MAGIC
# MAGIC | Thing | What AppKit does |
# MAGIC |---|---|
# MAGIC | Lakebase connection | Manages the connection pool and refreshes OAuth tokens automatically |
# MAGIC | Per-user data | `asUser()` pattern — queries run as the signed-in user, respecting their permissions |
# MAGIC | Right tool for the job | Analytics plugin for warehouse queries; Lakebase plugin for writes and low-latency reads |
# MAGIC | Type safety | Generates TypeScript types from your SQL files automatically |
# MAGIC | Auth | Service principal provisioned automatically on deploy; OAuth wired to workspace SSO |
# MAGIC | Dev/prod switching | `run-local` for local iteration, `deploy` to ship — no config changes needed |
# MAGIC
# MAGIC #### Deploy commands
# MAGIC
# MAGIC ```bash
# MAGIC databricks apps run-local      # run locally against real workspace data
# MAGIC databricks apps dev-remote     # hot-reload UI against the deployed backend  
# MAGIC databricks apps deploy         # ship it
# MAGIC ```
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Making Your App Production-Ready
# MAGIC
# MAGIC AppKit handles the vast majority of production concerns automatically — you don't need to think about SIGTERM handling, port binding, TLS, auth, connection pooling, or logging. These are all wired correctly the moment you scaffold with `databricks apps init`.
# MAGIC
# MAGIC There are a few things worth being intentional about.
# MAGIC
# MAGIC ### One rule that actually matters
# MAGIC
# MAGIC **Don't process heavy data inside the app.** App compute is for serving a UI, not running queries or crunching datasets. The moment you need aggregations, large scans, or batch processing — put it in a SQL warehouse or Model Serving endpoint, and call that from the app.
# MAGIC
# MAGIC AppKit makes this the natural path: the analytics plugin runs against a SQL warehouse, and the Lakebase plugin handles low-latency operational reads and writes. As long as you're using the right plugin for the right job, you're following this rule without thinking about it.
# MAGIC
# MAGIC ### Things to ask your coding agent to add
# MAGIC
# MAGIC These don't come in the scaffold by default but are quick to add:
# MAGIC
# MAGIC **Caching for expensive queries:**
# MAGIC > *"Cache the results of the alerts query for 60 seconds so we're not hitting Lakebase on every page load."*
# MAGIC
# MAGIC AppKit's built-in cache auto-selects persistent (Lakebase-backed) or in-memory storage depending on what's available.
# MAGIC
# MAGIC **Friendly error handling:**
# MAGIC > *"Add global error handling so if a query fails, the UI shows a friendly message rather than crashing."*
# MAGIC
# MAGIC **Loading states:**
# MAGIC > *"Add a loading spinner while data is being fetched and a retry button if the request fails."*
# MAGIC
# MAGIC ### The one workspace setting worth knowing
# MAGIC
# MAGIC By default your app runs on a **Medium** instance (2 vCPUs, 6 GB memory) — this is fine for most apps.
# MAGIC
# MAGIC If you notice the app feeling slow under load or with multiple users, bump it to **Large** (4 vCPUs, 12 GB):
# MAGIC
# MAGIC 1. In your workspace, go to **Apps** in the left sidebar
# MAGIC 2. Click your app name → **Settings** tab
# MAGIC 3. Under **Compute**, change the instance size to **Large**
# MAGIC 4. Click **Save** — no redeploy needed, the change applies while the app keeps running
# MAGIC
# MAGIC
# MAGIC ### Monitoring logs
# MAGIC
# MAGIC Stream live logs from your deployed app:
# MAGIC
# MAGIC ```bash
# MAGIC databricks apps logs <your-app-name> --follow
# MAGIC ```
# MAGIC
# MAGIC Filter for errors only:
# MAGIC
# MAGIC ```bash
# MAGIC databricks apps logs <your-app-name> --follow --search ERROR
# MAGIC ```
# MAGIC
# MAGIC You can also see logs in the workspace: **Apps** → click your app → **Logs** tab.
# MAGIC
# MAGIC ### Environment separation (if you want it)
# MAGIC
# MAGIC If you want a development version and a production version of your app:
# MAGIC
# MAGIC ```bash
# MAGIC databricks apps deploy --target dev    # deploys to a dev app
# MAGIC databricks apps deploy --target prod   # deploys to a prod app
# MAGIC ```
# MAGIC
# MAGIC For the workshop this isn't necessary — one deployment is fine. But it's the right pattern when handing off to a customer.
# MAGIC
# MAGIC
