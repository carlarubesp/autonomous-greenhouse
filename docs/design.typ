
#set document(title: [Design Considerations — Autonomous Greenhouse System])
#set heading(numbering: "1.1.")
#set par(justify: true)
#set page(margin: 2.5cm, numbering: "1")

#show table.cell.where(y: 0): strong

// Title and abstract
#align(center)[
  #v(3cm)
  #text(size: 22pt, weight: "bold")[Design Considerations]
  #v(0.3cm)
  #text(size: 14pt, style: "italic")[Autonomous Greenhouse]
  #v(0.3cm)
  #text(size: 11pt)[Carla Rubio Espiñeira]
  #v(0.1cm)
  #text(size: 11pt)[#datetime.today().display("[day] [month repr:long] [year]")]
]

#v(2cm)

#heading(outlined: false, numbering: none)[Abstract]
// TODO: finish the abstract

#pagebreak()

// Index
#outline()
#pagebreak()

= Tech stack

+ *Python 3*: language used across all components.
+ *Eclipse Mosquitto*: MQTT broker for the control plane.
+ *FastAPI + Uvicorn*: REST API for the knowledge base.
+ *Pydantic*: data validation for API payloads.
+ *Docker + Docker Compose*: containerization and orchestration of the whole pipeline.

= Goals of the system

The main goal of the system is that the plants survive and grow. This can be achieved using the following sub-goals:

#table(
  columns: (auto, auto, auto),
  align: (left, left, left),
  [Goal], [Description], [Evaluation metric],

  [Plant survival],
  [The system must prevent metrics from reaching the alarm thresholds that could kill the plants.],
  [e.g.: (isDay == True ⇒ 12 ≤ Temp ≤ 32) ∧ (isDay == False ⇒ 10 ≤ Temp ≤ 22)],

  [Optimal growth conditions],
  [The system should maintain all metrics within their ideal or secure ranges to promote plant health.],
  [e.g.: isDay == True ⇒ 18 < Temp < 26],

  [Energy and resource efficiency],
  [When the system is not in an alarm state, it should minimize actuator usage (e.g., heaters, pumps) to save energy.],
  [Minimization of active time for binary actuators (e.g., `Heater == True`)],
)

= Managed resources

The system includes the following sensors and actuators:

#table(
  columns: (auto, auto, 1.3fr),
  align: (left, left, left),
  [Metric], [Monitored by], [Managed by],

  [Temperature], [Temperature sensor], [
    - Heater (increase)
    - Fan (decrease)
  ],

  [CO2], [CO2 sensor], [
    - Fan (decrease)
    - CO2 injector (increase)
  ],

  [Relative humidity], [Hygrometer], [
    - Sprinklers (increase)
    - Fan (decrease)
  ],

  [Ground humidity], [Soil Moisture Sensor], [
    - Water pump (increase)
    - Sprinklers (increase)
  ],

  [pH], [pH Probe], [
    - Acid dosing pump (decrease)
    - Base dosing pump (increase)
  ],

  [Conductivity (EC)], [EC Sensor], [
    - Nutrient dosing pump (increase)
    - Water pump (decrease)
  ],
)

#pagebreak(weak: true)
= Architectural pattern

The architectural pattern used is the MAPE-K loop.
// TODO: justification of the MAPE-K loop

== Justification


= Communication

The components communicate on two distinct ways:

#table(
  columns: (auto, auto, 1fr),
  align: (left, left, left),
  [Channel], [Protocol], [Use],

  [Control],
  [MQTT (`greenhouse/...`)],
  [Actuator commands, planner plans, `start` / `reset` signals.],

  [Data],
  [HTTP REST (`/short-term`, `/actuators`, `/logs`...)],
  [Synchronous reads and writes against the knowledge base.]
)

The MAPE-K loop is structured as follows:
// TODO: insert MAPE-K diagram

= Design considerations: Monitor

The monitor function provides the mechanisms that collect, aggregate, filter,
and report details collected from a managed resource.

+ *What kinds of data and events are collected from which sources, sensors, or
  probes?* \
  A simulator has been created to emulate the sensor and actuator components.
  It produces information with added randomization to imitate real-world
  fluctuations in the metrics, allowing evaluation of whether the autonomous
  system works under realistic conditions.

+ *Are there common event formats?* \
  The information produced by the simulator is emitted in JSON format into the
  monitor. 
  
  Inside this JSON, it is important to note that the simulation clock runs from 0 to 1439, where 0–719 corresponds to day and 720–1439 to night. This clock drives the day/night profile selection used throughout the system.

+ *What is the sampling rate and is it fixed or varying?* \
  The sampling rate is fixed at one minute.

+ *Are the sampled sources fixed or do they change dynamically?* \
  The sampled sources are fixed.

+ *What are appropriate filters for the data streams?* \
  Two filters are applied:
  + Every minute, the monitor retrieves the information from the last minute
    and checks whether there is an alarm or a dangerous metric. If so, the
    alarm protocol is activated.
  + Every 20 minutes, the system evaluates all the metrics of the
    greenhouse and activates the corresponding actuators. These actuators
    then self-regulate based on the metrics from the sensors and deactivate
    when needed.

#pagebreak(weak: true)
= Design considerations: Knowledge

A large portion of the knowledge base consists of monitored information.

+ *How much information is needed for future reference?* \
  Two types of memory are used:
  + *Short-term memory* (for the analyzer): the raw data accumulated over the
    20-minute window. When the window ends, the short-term memory is reset,
    but a log entry is created that the system uses to determine whether the
    state is consistent or whether changes occurred. Approximately nine logs
    are retained so that the system can reason over the last approx. 3 h and
    detect emerging patterns.
  + *Long-term memory* (for future reference): a log of every important event,
    the time frame in which it occurred, related information, and the
    corrective action that was taken.

With the detailed level of reporting and logging available in modern software
systems, it is important to monitor and store only the data that is genuinely
useful to the control loop. If large amounts of log data are stored, performance
may deteriorate because data is constantly monitored even when it has no
relevance to the system. The knowledge component additionally contains:

+ The max/min tables for every metric used by the alarm protocols.
+ The priority hierarchy.
+ The active profile (day or night).
+ Both short- and long-term memory.
+ Symptom rules.

#pagebreak(weak: true)
= Design considerations: Analyzer

The analyzer provides mechanisms to correlate and model complex situations. It
embodies the control model together with the planner, along with time-series
forecasting and queuing models.

These mechanisms allow the autonomic manager to learn about the IT environment
and to help predict future situations.

+ *How are the collected data represented and stored?* \
  The collected data is represented in a 20-minute log, in which all data is
  stored as JSON inside the knowledge base.

+ *What are appropriate diagnosis methods to analyze the data?*

  #table(
    columns: (auto, auto, auto, auto),
    align: (left, left, left, left),
    [Metric], [Ideal measurement], [Secure range], [Alarm / Danger],

    [Temperature (Day)], [22 °C], [18 °C – 26 °C], [< 12 °C or > 32 °C],
    [Temperature (Night)], [16 °C], [14 °C – 18 °C], [< 10 °C or > 22 °C],
    [Relative humidity], [70%], [60% – 80%], [< 50% or > 85%],
    [Ground humidity], [40%], [30% – 60%], [< 20% or > 80%],
    [CO2], [800 ppm], [400 – 1000 ppm], [< 350 ppm or > 1500 ppm],
    [Water / ground pH], [6.0], [5.5 – 6.5], [< 5.0 or > 7.0],
    [Conductivity (EC)], [2.0 mS/cm], [1.5 – 2.5 mS/cm], [< 1.0 or > 3.5 mS/cm],
  )

+ *How is the current state of the system assessed?* \
  Two states are distinguished:
  + *Reference state*: the average of the previous 20-minute window,
    used as a baseline to detect trends.
  + *Current state*: the newest 20-minute window.

+ *How much past state needs to be kept around?* \
  The last nine evaluated states.

+ *How are critical states achieved?* \
  If a metric is dangerously out of range, the alarm protocol is activated and
  the system acts immediately, even outside the 20-minute evaluation window.

+ *How are common symptoms recognized (e.g., symptoms database)?* \
  Symptoms are derived from the alarm/danger column in the table above. Each
  case has its own symptom, for example, if the temperature is above 32 degrees and the soil humidity is below 20%, then the symptom would be "heating risk".

#pagebreak(weak: true)
= Design considerations: Planning Engine

The planning engine provides mechanisms to construct the actions needed to
achieve goals and objectives. It uses policy information to guide its work.

+ *How is the future state of the system inferred and how is a decision
  reached?* (via off-line simulation, quality-of-service (QoS) objectives, or
  utility goal functions.) \
  The future state corresponds to the next 20-minute window, evaluated from the
  data gathered. Decisions are reached if certain thresholds are crossed, for
  example, the target is to maintain the temperature between 18 °C and 26 °C,
  so if the forecast indicates it will rise above 26 °C, the blinds or a fan
  are activated to keep the plants cooler. All decisions follow a utility goal
  function so that the overall wellness of the system is maximized. Such
  metrics can be changed in the future to cater to a specific plant type or
  weather.

+ *What models and algorithms are used for trade-off analysis?* \
  In this system, energy cost is a secondary concern to plant survival. If the
  system is under alarm, it acts without consideration for energy costs. In all
  other instances, it regulates the metrics within the required range while
  minimizing energy consumption.

+ *What are the priorities for adaptation across multiple control loops and
  within a single control loop?* \
  The priority hierarchy is:
  + Extreme temperature or pH is fixed first, as it can kill the plant within
    minutes.
  + Soil moisture and relative humidity come next, as they are basic needs of
    the plant; the plant has a water reserve and can survive slightly longer
    without them.
  + CO2 levels and conductivity adjustments come after, as they are less
    immediately dangerous for the plant.

+ *Under what conditions should adaptation be performed?* \
  Adaptation is triggered by changes in the normal metrics. Adaptation is also
  conditional on whether the system is in day or night mode, which is
  quantified by a simulation clock (enabling experiments to run faster than a real
  clock).

+ *How is head-room provided and system thrashing avoided, considering the
  timing of the required adaptations?* \
  To avoid system thrashing, hysteresis is used. For example, if the
  temperature should be between 18 °C and 26 °C, the heater is not stopped
  until the reading is further ahead of 18 °C (around 22–23 °C) after which a
  short cooldown of approximately 5 minutes is applied.

= Design considerations: Execution Engine

The execution engine provides mechanisms to control the execution of a plan by
updating the managed element dynamically.

+ *What are the managed elements and how can they be manipulated?* \
  The managed elements are the actuators, and all of them are manipulated
  through parameter tuning (e.g., switching the heater on or off). Each
  actuator is in a binary state of True or False, which determines whether it
  is active or not.

+ *Are changes of the system pre-computed, opportunistically assembled,
  composed, or generated?* \
  The system switches between known configurations, selecting pre-computed
  actions that are known to have value. It does not create new combinations of
  known actions.

= Conclusion
// TODO: do the conclusion (if needed)

= References

+ Course material, "Autonomous Systems" (2025–2026), Università degli Studi
  dell'Aquila.