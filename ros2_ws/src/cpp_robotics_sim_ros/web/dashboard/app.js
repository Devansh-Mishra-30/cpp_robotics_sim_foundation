"use strict";

const ROSBRIDGE_URL = "ws://localhost:9090";
const COMMAND_PUBLISH_INTERVAL_MS = 100;
const RECONNECT_DELAY_MS = 2000;
const STOP_BURST_COUNT = 3;
const STOP_BURST_INTERVAL_MS = 60;

const state = {
  socket: null,
  connected: false,
  reconnectTimer: null,
  publishTimer: null,

  linearDirection: 0,
  angularDirection: 0,

  linearSpeed: 0.15,
  angularSpeed: 0.60,

  emergencyStop: false,
  activeSource: "unknown",
  simulationState: "unknown",

  selectedEnvironment: "warehouse",
  availableEnvironments: [
    "warehouse",
    "hospital",
  ],
  environmentWorldFile: "warehouse_world.sdf",
  environmentSelectionLocked: true,
  environmentState: "unknown",

  modeState: "stopped",
  mapSaveState: "ready",
  savedMaps: [],
  selectedMapName: "",
  selectedMapPath: "",
  selectedMapEnvironment: "",

  navigationState: "inactive",
  navigationGoalActive: false,
  navigationRequestPending: false,
  navigationResult: "",

  navigationFeedback: {
    distanceRemaining: null,
    estimatedTimeRemaining: null,
    navigationTime: null,
    recoveryCount: 0,
  },

  serviceRequests: new Map(),

  pressedKeys: new Set(),
  activePointerButton: null,
};

const elements = {
  connectionIndicator:
    document.getElementById("connectionIndicator"),

  connectionText:
    document.getElementById("connectionText"),

  activeSource:
    document.getElementById("activeSource"),

  linearCommand:
    document.getElementById("linearCommand"),

  angularCommand:
    document.getElementById("angularCommand"),

  safetyState:
    document.getElementById("safetyState"),

  linearSpeed:
    document.getElementById("linearSpeed"),

  linearSpeedValue:
    document.getElementById("linearSpeedValue"),

  angularSpeed:
    document.getElementById("angularSpeed"),

  angularSpeedValue:
    document.getElementById("angularSpeedValue"),

  stopButton:
    document.getElementById("stopButton"),

  emergencyStopButton:
    document.getElementById("emergencyStopButton"),

  emergencyButtonTitle:
    document.getElementById("emergencyButtonTitle"),

  emergencyButtonSubtitle:
    document.getElementById("emergencyButtonSubtitle"),

  clearLogButton:
    document.getElementById("clearLogButton"),

  eventLog:
    document.getElementById("eventLog"),

  driveButtons:
    document.querySelectorAll(".drive-button[data-linear]"),

  simulationState:
    document.getElementById("simulationState"),

  simulationStateIndicator:
    document.getElementById("simulationStateIndicator"),

  simulationMessage:
    document.getElementById("simulationMessage"),

  startSimulationButton:
    document.getElementById("startSimulationButton"),

  stopSimulationButton:
    document.getElementById("stopSimulationButton"),

  resetSimulationButton:
    document.getElementById("resetSimulationButton"),

  selectedEnvironmentLabel:
    document.getElementById(
      "selectedEnvironmentLabel"
    ),

  environmentLockBadge:
    document.getElementById(
      "environmentLockBadge"
    ),

  environmentWorldFile:
    document.getElementById(
      "environmentWorldFile"
    ),

  environmentMessage:
    document.getElementById(
      "environmentMessage"
    ),

  warehouseEnvironmentButton:
    document.getElementById(
      "warehouseEnvironmentButton"
    ),

  hospitalEnvironmentButton:
    document.getElementById(
      "hospitalEnvironmentButton"
    ),

  environmentButtons:
    document.querySelectorAll(
      ".environment-button[data-environment]"
    ),

  modeState:
    document.getElementById("modeState"),

  modeStateIndicator:
    document.getElementById("modeStateIndicator"),

  modeMessage:
    document.getElementById("modeMessage"),

  manualModeButton:
    document.getElementById("manualModeButton"),

  mappingModeButton:
    document.getElementById("mappingModeButton"),

  localizationModeButton:
    document.getElementById("localizationModeButton"),

  navigationModeButton:
    document.getElementById("navigationModeButton"),

  stopModeButton:
    document.getElementById("stopModeButton"),

  mapNameInput:
    document.getElementById("mapNameInput"),

  saveMapButton:
    document.getElementById("saveMapButton"),

  mapSaveMessage:
    document.getElementById("mapSaveMessage"),

  savedMapList:
    document.getElementById("savedMapList"),

  savedMapCount:
    document.getElementById("savedMapCount"),

  selectedMapLabel:
    document.getElementById("selectedMapLabel"),

  localizationMapSelect:
    document.getElementById("localizationMapSelect"),

  selectLocalizationMapButton:
    document.getElementById(
      "selectLocalizationMapButton"
    ),

  initialPoseX:
    document.getElementById("initialPoseX"),

  initialPoseY:
    document.getElementById("initialPoseY"),

  initialPoseYaw:
    document.getElementById("initialPoseYaw"),

  setInitialPoseButton:
    document.getElementById("setInitialPoseButton"),

  localizationMessage:
    document.getElementById("localizationMessage"),

  navigationStateIndicator:
    document.getElementById(
      "navigationStateIndicator"
    ),

  navigationGoalState:
    document.getElementById(
      "navigationGoalState"
    ),

  navigationGoalX:
    document.getElementById(
      "navigationGoalX"
    ),

  navigationGoalY:
    document.getElementById(
      "navigationGoalY"
    ),

  navigationGoalYaw:
    document.getElementById(
      "navigationGoalYaw"
    ),

  sendNavigationGoalButton:
    document.getElementById(
      "sendNavigationGoalButton"
    ),

  cancelNavigationGoalButton:
    document.getElementById(
      "cancelNavigationGoalButton"
    ),

  navigationDistanceRemaining:
    document.getElementById(
      "navigationDistanceRemaining"
    ),

  navigationEstimatedTime:
    document.getElementById(
      "navigationEstimatedTime"
    ),

  navigationElapsedTime:
    document.getElementById(
      "navigationElapsedTime"
    ),

  navigationRecoveryCount:
    document.getElementById(
      "navigationRecoveryCount"
    ),

  navigationGoalMessage:
    document.getElementById(
      "navigationGoalMessage"
    ),
};


function connectRosbridge() {
  clearTimeout(state.reconnectTimer);

  updateConnectionStatus("connecting");

  addLog(
    `Connecting to ${ROSBRIDGE_URL}`,
    "info",
  );

  const socket = new WebSocket(ROSBRIDGE_URL);
  state.socket = socket;

  socket.addEventListener("open", () => {
    if (socket !== state.socket) {
      return;
    }

    state.connected = true;
    updateConnectionStatus("connected");

    advertiseTopics();
    subscribeToActiveSource();
    subscribeToSimulationStatus();
    subscribeToEnvironmentStatus();
    subscribeToModeStatus();
    subscribeToMappingStatus();
    subscribeToSavedMaps();
    subscribeToLocalizationStatus();
    subscribeToSelectedMap();
    subscribeToNavigationStatus();
    subscribeToNavigationFeedback();

    publishEmergencyStop(state.emergencyStop);

    addLog("Connected to ROS bridge.", "success");
  });

  socket.addEventListener("message", (event) => {
    if (socket !== state.socket) {
      return;
    }

    handleRosbridgeMessage(event.data);
  });

  socket.addEventListener("error", () => {
    if (socket !== state.socket) {
      return;
    }

    addLog("ROS bridge connection error.", "danger");
  });

  socket.addEventListener("close", () => {
    if (socket !== state.socket) {
      return;
    }

    state.connected = false;
    stopCommandLoop();
    stopMotion(false);

    updateConnectionStatus("disconnected");

    addLog(
      "ROS bridge disconnected. Reconnecting…",
      "warning",
    );

    state.reconnectTimer = window.setTimeout(
      connectRosbridge,
      RECONNECT_DELAY_MS,
    );
  });
}


function sendRosbridgeMessage(message) {
  if (
    !state.connected
    || !state.socket
    || state.socket.readyState !== WebSocket.OPEN
  ) {
    return false;
  }

  state.socket.send(JSON.stringify(message));
  return true;
}


function advertiseTopics() {
  sendRosbridgeMessage({
    op: "advertise",
    topic: "/cmd_vel/gui",
    type: "geometry_msgs/msg/TwistStamped",
  });

  sendRosbridgeMessage({
    op: "advertise",
    topic: "/control/emergency_stop",
    type: "std_msgs/msg/Bool",
  });

  sendRosbridgeMessage({
    op: "advertise",
    topic: "/simulation/environment_request",
    type: "std_msgs/msg/String",
  });
}


function subscribeToActiveSource() {
  sendRosbridgeMessage({
    op: "subscribe",
    topic: "/control/active_source",
    type: "std_msgs/msg/String",
    throttle_rate: 100,
    queue_length: 1,
  });
}


function subscribeToSimulationStatus() {
  sendRosbridgeMessage({
    op: "subscribe",
    topic: "/simulation/status",
    type: "std_msgs/msg/String",
    throttle_rate: 100,
    queue_length: 1,
  });
}


function subscribeToEnvironmentStatus() {
  sendRosbridgeMessage({
    op: "subscribe",
    topic: "/simulation/environment_status",
    type: "std_msgs/msg/String",
    throttle_rate: 100,
    queue_length: 1,
  });
}


function subscribeToModeStatus() {
  sendRosbridgeMessage({
    op: "subscribe",
    topic: "/mode/status",
    type: "std_msgs/msg/String",
    throttle_rate: 100,
    queue_length: 1,
  });
}


function subscribeToMappingStatus() {
  sendRosbridgeMessage({
    op: "subscribe",
    topic: "/mapping/save_status",
    type: "std_msgs/msg/String",
    queue_length: 1,
  });
}


function subscribeToSavedMaps() {
  sendRosbridgeMessage({
    op: "subscribe",
    topic: "/mapping/saved_maps",
    type: "std_msgs/msg/String",
    queue_length: 1,
  });
}


function subscribeToLocalizationStatus() {
  sendRosbridgeMessage({
    op: "subscribe",
    topic: "/localization/status",
    type: "std_msgs/msg/String",
    queue_length: 1,
  });
}


function subscribeToSelectedMap() {
  sendRosbridgeMessage({
    op: "subscribe",
    topic: "/localization/selected_map",
    type: "std_msgs/msg/String",
    queue_length: 1,
  });
}


function subscribeToNavigationStatus() {
  sendRosbridgeMessage({
    op: "subscribe",
    topic: "/navigation/status",
    type: "std_msgs/msg/String",
    queue_length: 1,
  });
}


function subscribeToNavigationFeedback() {
  sendRosbridgeMessage({
    op: "subscribe",
    topic: "/navigation/feedback",
    type: "std_msgs/msg/String",
    throttle_rate: 100,
    queue_length: 1,
  });
}


function handleRosbridgeMessage(rawMessage) {
  let message;

  try {
    message = JSON.parse(rawMessage);
  } catch {
    addLog(
      "Received malformed rosbridge message.",
      "warning",
    );
    return;
  }

  if (
    message.op === "publish"
    && message.topic === "/control/active_source"
    && message.msg
  ) {
    const source = String(
      message.msg.data ?? "unknown"
    );

    updateActiveSource(source);
    return;
  }

  if (
    message.op === "publish"
    && message.topic === "/simulation/status"
    && message.msg
  ) {
    const simulationState = String(
      message.msg.data ?? "unknown"
    );

    updateSimulationState(simulationState);
    return;
  }

  if (
    message.op === "publish"
    && message.topic === "/simulation/environment_status"
    && message.msg
  ) {
    handleEnvironmentStatus(message.msg.data);
    return;
  }

  if (
    message.op === "publish"
    && message.topic === "/mode/status"
    && message.msg
  ) {
    const modeState = String(
      message.msg.data ?? "stopped"
    );

    updateModeState(modeState);
    return;
  }

  if (
    message.op === "publish"
    && message.topic === "/mapping/save_status"
    && message.msg
  ) {
    handleMapSaveStatus(message.msg.data);
    return;
  }

  if (
    message.op === "publish"
    && message.topic === "/mapping/saved_maps"
    && message.msg
  ) {
    handleSavedMaps(message.msg.data);
    return;
  }

  if (
    message.op === "publish"
    && message.topic === "/localization/status"
    && message.msg
  ) {
    handleLocalizationStatus(message.msg.data);
    return;
  }

  if (
    message.op === "publish"
    && message.topic === "/localization/selected_map"
    && message.msg
  ) {
    handleSelectedMap(message.msg.data);
    return;
  }

  if (
    message.op === "publish"
    && message.topic === "/navigation/status"
    && message.msg
  ) {
    handleNavigationStatus(message.msg.data);
    return;
  }

  if (
    message.op === "publish"
    && message.topic === "/navigation/feedback"
    && message.msg
  ) {
    handleNavigationFeedback(message.msg.data);
    return;
  }

  if (
    message.op === "service_response"
    && message.id
  ) {
    handleServiceResponse(message);
  }
}




function requestEnvironment(environmentName) {
  const normalizedEnvironment =
    String(environmentName).trim().toLowerCase();

  if (!state.connected) {
    setEnvironmentMessage(
      "ROS is disconnected.",
      "danger",
    );
    return;
  }

  if (state.environmentSelectionLocked) {
    setEnvironmentMessage(
      "Stop the simulation before changing environments.",
      "warning",
    );
    return;
  }

  if (
    !state.availableEnvironments.includes(
      normalizedEnvironment
    )
  ) {
    setEnvironmentMessage(
      `Unsupported environment: ${normalizedEnvironment}`,
      "danger",
    );
    return;
  }

  if (
    normalizedEnvironment
    === state.selectedEnvironment
  ) {
    setEnvironmentMessage(
      `${formatEnvironmentName(normalizedEnvironment)} `
      + "is already selected.",
      "",
    );
    return;
  }

  setEnvironmentControlsBusy(true);

  setEnvironmentMessage(
    `Selecting ${formatEnvironmentName(normalizedEnvironment)}…`,
    "warning",
  );

  const sent = sendRosbridgeMessage({
    op: "publish",
    topic: "/simulation/environment_request",
    msg: {
      data: normalizedEnvironment,
    },
  });

  if (!sent) {
    setEnvironmentControlsBusy(false);

    setEnvironmentMessage(
      "Unable to send environment request.",
      "danger",
    );
  }
}


function handleEnvironmentStatus(rawPayload) {
  let payload;

  try {
    payload = JSON.parse(rawPayload);
  } catch {
    state.environmentState = "error";
    state.environmentSelectionLocked = true;

    setEnvironmentMessage(
      "Received invalid environment status.",
      "danger",
    );

    updateEnvironmentControls();
    return;
  }

  const previousEnvironment =
    state.selectedEnvironment;

  state.environmentState =
    String(payload.state ?? "unknown");

  state.selectedEnvironment =
    String(
      payload.selected_environment
      ?? state.selectedEnvironment
    );

  state.environmentWorldFile =
    String(payload.world_file ?? "");

  state.environmentSelectionLocked =
    Boolean(payload.selection_locked);

  if (Array.isArray(payload.available_environments)) {
    state.availableEnvironments =
      payload.available_environments.map(
        (environment) =>
          String(environment).toLowerCase()
      );
  }

  const statusMessage =
    String(
      payload.message
      ?? "Environment status updated"
    );

  const level =
    state.environmentState === "error"
    || state.environmentState === "invalid_request"
      ? "danger"
      : state.environmentState === "locked"
        ? "warning"
        : state.environmentState === "selected"
        || state.environmentState === "ready"
        || state.environmentState === "running"
          ? "success"
          : "";

  setEnvironmentMessage(
    statusMessage,
    level,
  );

  updateEnvironmentDisplay();
  renderSavedMaps();
  updateEnvironmentControls();

  if (
    previousEnvironment
    !== state.selectedEnvironment
  ) {
    addLog(
      "Environment: "
      + `${formatEnvironmentName(previousEnvironment)} → `
      + `${formatEnvironmentName(
        state.selectedEnvironment
      )}`,
      "success",
    );
  }
}


function formatEnvironmentName(environmentName) {
  const normalized =
    String(environmentName || "unknown")
      .replaceAll("_", " ")
      .trim();

  return normalized
    ? normalized[0].toUpperCase()
      + normalized.slice(1)
    : "Unknown";
}


function updateEnvironmentDisplay() {
  elements.selectedEnvironmentLabel.textContent =
    state.selectedEnvironment
      .replaceAll("_", " ")
      .toUpperCase();

  elements.environmentWorldFile.textContent =
    state.environmentWorldFile || "—";

  elements.environmentLockBadge.textContent =
    state.environmentSelectionLocked
      ? "LOCKED"
      : "UNLOCKED";

  elements.environmentLockBadge.className =
    "environment-lock-badge "
    + (
      state.environmentSelectionLocked
        ? "locked"
        : "unlocked"
    );

  elements.environmentButtons.forEach((button) => {
    const buttonEnvironment =
      String(button.dataset.environment);

    button.classList.toggle(
      "active",
      buttonEnvironment
      === state.selectedEnvironment,
    );
  });
}


function updateEnvironmentControls() {
  const simulationBusy =
    state.simulationState === "starting"
    || state.simulationState === "running"
    || state.simulationState === "stopping"
    || state.serviceRequests.size > 0;

  const selectionEnabled =
    state.connected
    && !state.environmentSelectionLocked
    && !simulationBusy;

  const configuredEnvironments =
    new Set([
      "warehouse",
      "hospital",
      ...state.availableEnvironments.map(
        (environment) =>
          String(environment).trim().toLowerCase()
      ),
    ]);

  elements.environmentButtons.forEach((button) => {
    const buttonEnvironment =
      String(button.dataset.environment)
        .trim()
        .toLowerCase();

    const environmentAvailable =
      configuredEnvironments.has(
        buttonEnvironment
      );

    button.disabled =
      !selectionEnabled
      || !environmentAvailable
      || buttonEnvironment
        === state.selectedEnvironment;
  });
}


function setEnvironmentControlsBusy(busy) {
  if (busy) {
    elements.environmentButtons.forEach((button) => {
      button.disabled = true;
    });
    return;
  }

  updateEnvironmentControls();
}


function setEnvironmentMessage(
  message,
  level = "",
) {
  elements.environmentMessage.textContent =
    message;

  elements.environmentMessage.className =
    `environment-message ${level}`.trim();
}


function makeServiceRequestId(action) {
  return (
    `simulation-${action}-`
    + `${Date.now()}-`
    + `${Math.random().toString(16).slice(2)}`
  );
}


function callSimulationService(action) {
  if (!state.connected) {
    setSimulationMessage(
      "ROS is disconnected.",
      "danger",
    );
    return;
  }

  const service = `/simulation/${action}`;
  const requestId = makeServiceRequestId(action);

  state.serviceRequests.set(
    requestId,
    action,
  );

  setLifecycleButtonsBusy(true);
  setModeButtonsBusy(true);

  setSimulationMessage(
    `${action[0].toUpperCase()}${action.slice(1)} request sent…`,
    "warning",
  );

  const sent = sendRosbridgeMessage({
    op: "call_service",
    service,
    type: "std_srvs/srv/Trigger",
    args: {},
    id: requestId,
  });

  if (!sent) {
    state.serviceRequests.delete(requestId);
    setLifecycleButtonsBusy(false);

    setSimulationMessage(
      "Unable to send service request.",
      "danger",
    );
  }
}


function handleServiceResponse(message) {
  const action = state.serviceRequests.get(
    message.id
  );

  if (!action) {
    return;
  }

  state.serviceRequests.delete(message.id);

  const values = message.values ?? {};

  if (action.startsWith("mode:")) {
    handleModeServiceResponse(
      action,
      values,
    );

    if (state.serviceRequests.size === 0) {
      setModeButtonsBusy(false);
      updateModeControls();
    }

    return;
  }

  const successful = Boolean(values.success);
  const responseMessage = String(
    values.message
    ?? `${action} request completed`
  );

  setSimulationMessage(
    responseMessage,
    successful ? "success" : "danger",
  );

  addLog(
    `Simulation ${action}: ${responseMessage}`,
    successful ? "success" : "danger",
  );

  if (state.serviceRequests.size === 0) {
    setLifecycleButtonsBusy(false);
    setEnvironmentControlsBusy(false);
    setModeButtonsBusy(false);
    updateSimulationControls();
    updateEnvironmentControls();
    updateModeControls();
  }
}


function updateSimulationState(simulationState) {
  state.simulationState = simulationState;

  elements.simulationState.textContent =
    simulationState.toUpperCase();

  elements.simulationStateIndicator.className =
    `simulation-state-indicator ${simulationState}`;

  updateSimulationControls();
  updateEnvironmentControls();
  updateModeControls();

  if (simulationState !== "running") {
    setModeMessage(
      "Start the simulation before selecting a mode.",
      "",
    );
  }
  updateMappingControls();
  updateLocalizationControls();
  updateNavigationControls();
}


function updateSimulationControls() {
  const busy =
    state.serviceRequests.size > 0
    || state.simulationState === "starting"
    || state.simulationState === "stopping";

  const running =
    state.simulationState === "running";

  elements.startSimulationButton.disabled =
    busy || running || !state.connected;

  elements.stopSimulationButton.disabled =
    busy || !running || !state.connected;

  elements.resetSimulationButton.disabled =
    busy || !running || !state.connected;
}


function setLifecycleButtonsBusy(busy) {
  if (busy) {
    elements.startSimulationButton.disabled = true;
    elements.stopSimulationButton.disabled = true;
    elements.resetSimulationButton.disabled = true;
    return;
  }

  updateSimulationControls();
}


function setSimulationMessage(
  message,
  level = "",
) {
  elements.simulationMessage.textContent = message;
  elements.simulationMessage.className =
    `simulation-message ${level}`.trim();
}


function callModeService(mode) {
  if (!state.connected) {
    setModeMessage(
      "ROS is disconnected.",
      "danger",
    );
    return;
  }

  if (state.simulationState !== "running") {
    setModeMessage(
      "Start the simulation before selecting a mode.",
      "warning",
    );
    return;
  }

  const requestId =
    `mode-${mode}-${Date.now()}-`
    + `${Math.random().toString(16).slice(2)}`;

  state.serviceRequests.set(
    requestId,
    `mode:${mode}`,
  );

  setModeButtonsBusy(true);

  const actionLabel =
    mode === "stop"
      ? "Stopping active mode"
      : `Starting ${mode} mode`;

  setModeMessage(
    `${actionLabel}…`,
    "warning",
  );

  const sent = sendRosbridgeMessage({
    op: "call_service",
    service: `/mode/${mode}`,
    type: "std_srvs/srv/Trigger",
    args: {},
    id: requestId,
  });

  if (!sent) {
    state.serviceRequests.delete(requestId);
    updateModeControls();

    setModeMessage(
      "Unable to send mode request.",
      "danger",
    );
  }
}


function handleModeServiceResponse(
  action,
  values,
) {
  const mode = action.slice("mode:".length);
  const successful = Boolean(values.success);

  const responseMessage = String(
    values.message
    ?? `${mode} request completed`
  );

  setModeMessage(
    responseMessage,
    successful ? "success" : "danger",
  );

  addLog(
    `Mode ${mode}: ${responseMessage}`,
    successful ? "success" : "danger",
  );
}


function updateModeState(modeState) {
  state.modeState = modeState;

  elements.modeState.textContent =
    modeState.toUpperCase();

  elements.modeStateIndicator.className =
    `mode-state-indicator ${modeState}`;

  updateModeControls();
  updateMappingControls();
  updateLocalizationControls();
  updateNavigationControls();
}


function updateModeControls() {
  const simulationRunning =
    state.simulationState === "running";

  const busy =
    state.serviceRequests.size > 0
    || state.modeState === "starting"
    || state.modeState === "stopping";

  const enabled =
    state.connected
    && simulationRunning
    && !busy;

  const activeModes = [
    "manual",
    "mapping",
    "localization",
    "navigation",
  ];

  const activeMode =
    activeModes.includes(state.modeState);

  const buttons = {
    manual: elements.manualModeButton,
    mapping: elements.mappingModeButton,
    localization: elements.localizationModeButton,
    navigation: elements.navigationModeButton,
  };

  Object.entries(buttons).forEach(
    ([mode, button]) => {
      const requiresSelectedMap =
        (
          mode === "localization"
          || mode === "navigation"
        )
        && !state.selectedMapPath;

      button.disabled =
        !enabled
        || activeMode
        || requiresSelectedMap;

      button.classList.toggle(
        "active",
        state.modeState === mode,
      );
    },
  );

  elements.stopModeButton.disabled =
    !enabled || !activeMode;
}


function setModeButtonsBusy(busy) {
  if (busy) {
    elements.manualModeButton.disabled = true;
    elements.mappingModeButton.disabled = true;
    elements.localizationModeButton.disabled = true;
    elements.navigationModeButton.disabled = true;
    elements.stopModeButton.disabled = true;
    return;
  }

  updateModeControls();
}


function setModeMessage(
  message,
  level = "",
) {
  elements.modeMessage.textContent = message;
  elements.modeMessage.className =
    `mode-message ${level}`.trim();
}


function saveMap() {
  const mapName =
    elements.mapNameInput.value.trim();

  if (!mapName) {
    setMapSaveMessage(
      "Enter a map name.",
      "warning",
    );
    return;
  }

  const validName =
    /^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/.test(
      mapName
    );

  if (!validName) {
    setMapSaveMessage(
      "Use letters, numbers, underscores, or hyphens only.",
      "danger",
    );
    return;
  }

  if (
    !state.connected
    || state.simulationState !== "running"
    || state.modeState !== "mapping"
  ) {
    setMapSaveMessage(
      "Mapping mode must be active.",
      "warning",
    );
    return;
  }

  const sent = sendRosbridgeMessage({
    op: "publish",
    topic: "/mapping/save_request",
    msg: {
      data: mapName,
    },
  });

  if (!sent) {
    setMapSaveMessage(
      "Unable to send map-save request.",
      "danger",
    );
    return;
  }

  state.mapSaveState = "saving";

  setMapSaveMessage(
    `Saving map '${mapName}'…`,
    "warning",
  );

  updateMappingControls();
}


function handleMapSaveStatus(rawPayload) {
  let payload;

  try {
    payload = JSON.parse(rawPayload);
  } catch {
    state.mapSaveState = "error";

    setMapSaveMessage(
      "Received invalid map-save status.",
      "danger",
    );

    updateMappingControls();
    return;
  }

  state.mapSaveState =
    String(payload.status ?? "error");

  const level =
    state.mapSaveState === "success"
      ? "success"
      : state.mapSaveState === "saving"
        ? "warning"
        : state.mapSaveState === "error"
          ? "danger"
          : "";

  setMapSaveMessage(
    String(
      payload.message
      ?? "Map-save status updated"
    ),
    level,
  );

  if (state.mapSaveState === "success") {
    elements.mapNameInput.value = "";
  }

  updateMappingControls();
}


function handleSavedMaps(rawPayload) {
  try {
    const maps = JSON.parse(rawPayload);

    state.savedMaps =
      Array.isArray(maps)
        ? maps
        : [];
  } catch {
    state.savedMaps = [];

    setMapSaveMessage(
      "Received an invalid saved-map list.",
      "danger",
    );
  }

  renderSavedMaps();
}


function mapsForSelectedEnvironment() {
  return state.savedMaps.filter((map) => {
    const environment =
      String(map.environment ?? "legacy")
        .trim()
        .toLowerCase();

    const legacy =
      Boolean(map.legacy)
      || environment === "legacy";

    return (
      legacy
      || environment
        === state.selectedEnvironment
    );
  });
}


function renderSavedMaps() {
  const visibleMaps =
    mapsForSelectedEnvironment();

  elements.savedMapCount.textContent =
    `${visibleMaps.length} `
    + `${visibleMaps.length === 1
      ? "MAP"
      : "MAPS"}`;

  if (visibleMaps.length === 0) {
    elements.savedMapList.innerHTML =
      '<p class="empty-map-list">'
      + "No maps saved for this environment."
      + "</p>";
  } else {
    elements.savedMapList.innerHTML =
      visibleMaps
        .map((map) => {
          const mapName =
            String(map.name ?? "");

          const environment =
            String(
              map.environment ?? "legacy"
            );

          const legacy =
            Boolean(map.legacy)
            || environment === "legacy";

          const complete =
            Boolean(map.complete);

          const environmentLabel =
            legacy
              ? "Legacy map"
              : formatEnvironmentName(
                  environment
                );

          return `
            <div class="saved-map-item">
              <strong>${escapeHtml(mapName)}</strong>
              <small>
                ${escapeHtml(environmentLabel)}
                · ${complete ? "Ready" : "Incomplete"}
              </small>
            </div>
          `;
        })
        .join("");
  }

  renderLocalizationMapOptions();
  updateLocalizationControls();
}


function updateMappingControls() {
  const enabled =
    state.connected
    && state.simulationState === "running"
    && state.modeState === "mapping"
    && state.mapSaveState !== "saving";

  elements.mapNameInput.disabled = !enabled;
  elements.saveMapButton.disabled = !enabled;
}


function setMapSaveMessage(
  message,
  level = "",
) {
  elements.mapSaveMessage.textContent = message;

  elements.mapSaveMessage.className =
    `map-save-message ${level}`.trim();
}


function selectLocalizationMap() {
  const rawValue =
    String(
      elements.localizationMapSelect.value
      ?? ""
    ).trim();

  if (!rawValue) {
    setLocalizationMessage(
      "Choose a saved map.",
      "warning",
    );
    return;
  }

  let decodedValue = rawValue;

  const decoder =
    document.createElement("textarea");

  decoder.innerHTML = rawValue;
  decodedValue = decoder.value;

  let selection = null;

  try {
    selection = JSON.parse(decodedValue);
  } catch {
    const matchingMap =
      mapsForSelectedEnvironment().find(
        (map) =>
          String(map.name ?? "")
          === decodedValue
      );

    if (matchingMap) {
      const mapEnvironment =
        String(
          matchingMap.environment
          ?? state.selectedEnvironment
        ).trim().toLowerCase();

      const legacy =
        Boolean(matchingMap.legacy)
        || mapEnvironment === "legacy";

      selection = {
        name: String(matchingMap.name ?? ""),
        environment:
          legacy
            ? state.selectedEnvironment
            : mapEnvironment,
      };
    }
  }

  if (
    !selection
    || typeof selection !== "object"
  ) {
    setLocalizationMessage(
      "Invalid map selection.",
      "danger",
    );
    return;
  }

  const mapName =
    String(selection.name ?? "").trim();

  const environment =
    String(
      selection.environment
      ?? state.selectedEnvironment
    ).trim().toLowerCase();

  if (!mapName || !environment) {
    setLocalizationMessage(
      "Invalid map name or environment.",
      "danger",
    );
    return;
  }

  const sent = sendRosbridgeMessage({
    op: "publish",
    topic: "/localization/select_map_request",
    msg: {
      data: JSON.stringify({
        name: mapName,
        environment,
      }),
    },
  });

  if (!sent) {
    setLocalizationMessage(
      "Unable to send map-selection request.",
      "danger",
    );
    return;
  }

  setLocalizationMessage(
    `Selecting map '${mapName}' for `
    + `${formatEnvironmentName(environment)}…`,
    "warning",
  );
}

function setInitialPose() {
  const x = Number(
    elements.initialPoseX.value
  );
  const y = Number(
    elements.initialPoseY.value
  );
  const yaw = Number(
    elements.initialPoseYaw.value
  );

  if (![x, y, yaw].every(Number.isFinite)) {
    setLocalizationMessage(
      "Initial pose values must be numeric.",
      "danger",
    );
    return;
  }

  const sent = sendRosbridgeMessage({
    op: "publish",
    topic: "/localization/initial_pose_request",
    msg: {
      data: JSON.stringify({
        x,
        y,
        yaw,
      }),
    },
  });

  if (!sent) {
    setLocalizationMessage(
      "Unable to send initial-pose request.",
      "danger",
    );
    return;
  }

  setLocalizationMessage(
    "Initial pose request sent…",
    "warning",
  );
}


function handleLocalizationStatus(
  rawPayload
) {
  try {
    const payload = JSON.parse(rawPayload);

    const status =
      String(payload.status ?? "");

    const level =
      status === "success"
        ? "success"
        : status === "error"
          ? "danger"
          : "";

    setLocalizationMessage(
      String(
        payload.message
        ?? "Localization status updated"
      ),
      level,
    );
  } catch {
    setLocalizationMessage(
      "Received invalid localization status.",
      "danger",
    );
  }
}


function handleSelectedMap(rawPayload) {
  try {
    const payload = JSON.parse(rawPayload);

    state.selectedMapName =
      String(payload.name ?? "");

    state.selectedMapPath =
      String(payload.yaml_path ?? "");

    state.selectedMapEnvironment =
      String(payload.environment ?? "")
        .trim()
        .toLowerCase();
  } catch {
    state.selectedMapName = "";
    state.selectedMapPath = "";
    state.selectedMapEnvironment = "";

    setLocalizationMessage(
      "Received invalid selected-map data.",
      "danger",
    );
  }

  elements.selectedMapLabel.textContent =
    state.selectedMapName
      ? (
          state.selectedMapName.toUpperCase()
          + (
              state.selectedMapEnvironment
                ? " · "
                  + state.selectedMapEnvironment
                    .replaceAll("_", " ")
                    .toUpperCase()
                : ""
            )
        )
      : "NO MAP SELECTED";

  renderLocalizationMapOptions();
  updateLocalizationControls();
  updateModeControls();
}


function renderLocalizationMapOptions() {
  const completeMaps =
    mapsForSelectedEnvironment().filter(
      (map) => Boolean(map.complete)
    );

  const previousValue =
    elements.localizationMapSelect.value;

  elements.localizationMapSelect
    .replaceChildren();

  const placeholderOption =
    document.createElement("option");

  placeholderOption.value = "";
  placeholderOption.textContent =
    "Select a saved map";

  elements.localizationMapSelect.appendChild(
    placeholderOption
  );

  completeMaps.forEach((map) => {
    const mapName =
      String(map.name ?? "").trim();

    const mapEnvironment =
      String(
        map.environment
        ?? state.selectedEnvironment
      ).trim().toLowerCase();

    const legacy =
      Boolean(map.legacy)
      || mapEnvironment === "legacy";

    const requestEnvironment =
      legacy
        ? state.selectedEnvironment
        : mapEnvironment;

    const option =
      document.createElement("option");

    option.value = JSON.stringify({
      name: mapName,
      environment: requestEnvironment,
    });

    option.textContent =
      legacy
        ? `${mapName} (Legacy)`
        : (
            `${mapName} (`
            + `${formatEnvironmentName(
              mapEnvironment
            )})`
          );

    elements.localizationMapSelect.appendChild(
      option
    );
  });

  const selectedValue =
    state.selectedMapName
      ? JSON.stringify({
          name: state.selectedMapName,
          environment:
            state.selectedMapEnvironment
            || state.selectedEnvironment,
        })
      : previousValue;

  const matchingOption =
    Array.from(
      elements.localizationMapSelect.options
    ).some(
      (option) =>
        option.value === selectedValue
    );

  if (matchingOption) {
    elements.localizationMapSelect.value =
      selectedValue;
  }
}

function updateLocalizationControls() {
  const completeMapCount =
    mapsForSelectedEnvironment().filter(
      (map) => Boolean(map.complete)
    ).length;

  elements.localizationMapSelect.disabled =
    !state.connected
    || completeMapCount === 0;

  elements.selectLocalizationMapButton.disabled =
    !state.connected
    || !elements.localizationMapSelect.value;

  const poseEnabled =
    state.connected
    && state.simulationState === "running"
    && (
      state.modeState === "localization"
      || state.modeState === "navigation"
    )
    && Boolean(state.selectedMapPath);

  elements.initialPoseX.disabled =
    !poseEnabled;

  elements.initialPoseY.disabled =
    !poseEnabled;

  elements.initialPoseYaw.disabled =
    !poseEnabled;

  elements.setInitialPoseButton.disabled =
    !poseEnabled;
}


function setLocalizationMessage(
  message,
  level = "",
) {
  elements.localizationMessage.textContent =
    message;

  elements.localizationMessage.className =
    `localization-message ${level}`.trim();
}



function sendNavigationGoal() {
  if (!state.connected) {
    setNavigationGoalMessage(
      "ROS is disconnected.",
      "danger",
    );
    return;
  }

  if (state.simulationState !== "running") {
    setNavigationGoalMessage(
      "Simulation must be running.",
      "warning",
    );
    return;
  }

  if (state.modeState !== "navigation") {
    setNavigationGoalMessage(
      "Navigation mode must be active.",
      "warning",
    );
    return;
  }

  if (
    state.navigationGoalActive
    || state.navigationRequestPending
  ) {
    setNavigationGoalMessage(
      "Cancel the active goal before sending another.",
      "warning",
    );
    return;
  }

  const x = Number(
    elements.navigationGoalX.value
  );

  const y = Number(
    elements.navigationGoalY.value
  );

  const yaw = Number(
    elements.navigationGoalYaw.value
  );

  if (![x, y, yaw].every(Number.isFinite)) {
    setNavigationGoalMessage(
      "Goal X, Y, and yaw must be finite numbers.",
      "danger",
    );
    return;
  }

  const sent = sendRosbridgeMessage({
    op: "publish",
    topic: "/navigation/goal_request",
    msg: {
      data: JSON.stringify({
        x,
        y,
        yaw,
      }),
    },
  });

  if (!sent) {
    setNavigationGoalMessage(
      "Unable to send navigation goal.",
      "danger",
    );
    return;
  }

  state.navigationRequestPending = true;
  state.navigationResult = "";

  setNavigationGoalMessage(
    `Goal request sent: x=${x.toFixed(2)}, `
    + `y=${y.toFixed(2)}, `
    + `yaw=${yaw.toFixed(2)} rad`,
    "warning",
  );

  updateNavigationControls();

  addLog(
    `Navigation goal requested: `
    + `x=${x.toFixed(2)}, `
    + `y=${y.toFixed(2)}, `
    + `yaw=${yaw.toFixed(2)}`,
    "info",
  );
}


function cancelNavigationGoal() {
  if (!state.connected) {
    setNavigationGoalMessage(
      "ROS is disconnected.",
      "danger",
    );
    return;
  }

  if (state.modeState !== "navigation") {
    setNavigationGoalMessage(
      "Navigation mode is not active.",
      "warning",
    );
    return;
  }

  if (
    !state.navigationGoalActive
    && !state.navigationRequestPending
  ) {
    setNavigationGoalMessage(
      "There is no active navigation goal.",
      "warning",
    );
    return;
  }

  const sent = sendRosbridgeMessage({
    op: "publish",
    topic: "/navigation/cancel_request",
    msg: {
      data: JSON.stringify({
        cancel: true,
      }),
    },
  });

  if (!sent) {
    setNavigationGoalMessage(
      "Unable to send cancellation request.",
      "danger",
    );
    return;
  }

  setNavigationGoalMessage(
    "Cancel request sent…",
    "warning",
  );

  addLog(
    "Navigation goal cancellation requested.",
    "warning",
  );
}


function handleNavigationStatus(rawPayload) {
  let payload;

  try {
    payload = JSON.parse(rawPayload);
  } catch {
    state.navigationState = "error";
    state.navigationGoalActive = false;
    state.navigationRequestPending = false;

    setNavigationGoalMessage(
      "Received invalid navigation status.",
      "danger",
    );

    updateNavigationDisplay();
    updateNavigationControls();
    return;
  }

  const navigationState =
    String(payload.state ?? "unknown");

  const previousState =
    state.navigationState;

  state.navigationState = navigationState;

  state.navigationGoalActive =
    Boolean(payload.goal_active);

  state.navigationRequestPending =
    navigationState === "waiting_for_server"
    || navigationState === "sending";

  state.navigationResult =
    String(payload.result ?? "");

  const terminalNavigationStates = new Set([
    "succeeded",
    "canceled",
    "aborted",
    "rejected",
    "invalid_request",
    "server_unavailable",
  ]);

  if (terminalNavigationStates.has(navigationState)) {
    state.navigationFeedback.distanceRemaining = 0.0;
    state.navigationFeedback.estimatedTimeRemaining = 0.0;

  }

  if (
    payload.feedback
    && typeof payload.feedback === "object"
    && Object.keys(payload.feedback).length > 0
  ) {
    updateNavigationFeedbackValues(
      payload.feedback
    );
  }

  if (terminalNavigationStates.has(navigationState)) {
    state.navigationFeedback.distanceRemaining = 0.0;
    state.navigationFeedback.estimatedTimeRemaining = 0.0;
  }

  const level =
    navigationState === "succeeded"
      ? "success"
      : (
          navigationState === "aborted"
          || navigationState === "rejected"
          || navigationState === "invalid_request"
          || navigationState === "server_unavailable"
        )
        ? "danger"
        : (
            navigationState === "waiting_for_server"
            || navigationState === "sending"
            || navigationState === "accepted"
            || navigationState === "canceling"
            || navigationState === "cancel_pending"
            || navigationState === "canceled"
          )
          ? "warning"
          : "";

  const statusMessage = String(
    payload.message
    ?? "Navigation status updated"
  );

  setNavigationGoalMessage(
    statusMessage,
    level,
  );

  updateNavigationDisplay();
  updateNavigationControls();

  if (
    previousState !== navigationState
    && [
      "succeeded",
      "canceled",
      "aborted",
      "rejected",
      "server_unavailable",
      "invalid_request",
    ].includes(navigationState)
  ) {
    addLog(
      `Navigation ${navigationState}: `
      + statusMessage,
      navigationState === "succeeded"
        ? "success"
        : navigationState === "canceled"
          ? "warning"
          : "danger",
    );
  }
}


function handleNavigationFeedback(rawPayload) {
  if (
    !state.navigationGoalActive
    || state.navigationState === "succeeded"
    || state.navigationState === "canceled"
    || state.navigationState === "aborted"
    || state.navigationState === "rejected"
    || state.navigationState === "invalid_request"
    || state.navigationState === "server_unavailable"
  ) {
    return;
  }

  try {
    const payload = JSON.parse(rawPayload);

    updateNavigationFeedbackValues(payload);
    updateNavigationDisplay();
  } catch {
    setNavigationGoalMessage(
      "Received invalid navigation feedback.",
      "danger",
    );
  }
}

function updateNavigationFeedbackValues(payload) {
  const finiteOrNull = (value) => {
    if (value === null || value === undefined) {
      return null;
    }

    const number = Number(value);

    return Number.isFinite(number)
      ? number
      : null;
  };

  state.navigationFeedback.distanceRemaining =
    finiteOrNull(payload.distance_remaining);

  state.navigationFeedback.estimatedTimeRemaining =
    finiteOrNull(payload.estimated_time_remaining);

  state.navigationFeedback.navigationTime =
    finiteOrNull(payload.navigation_time);

  const recoveryCount =
    Number(payload.recovery_count);

  state.navigationFeedback.recoveryCount =
    Number.isInteger(recoveryCount)
    && recoveryCount >= 0
      ? recoveryCount
      : 0;
}


function formatNavigationDistance(value) {
  return Number.isFinite(value)
    ? `${value.toFixed(2)} m`
    : "—";
}


function formatNavigationTime(value) {
  if (!Number.isFinite(value)) {
    return "—";
  }

  if (value < 60.0) {
    return `${value.toFixed(1)} s`;
  }

  const minutes = Math.floor(value / 60.0);
  const seconds = value - minutes * 60.0;

  return `${minutes}m ${seconds.toFixed(1)}s`;
}


function updateNavigationDisplay() {
  const displayState =
    state.modeState === "navigation"
      ? state.navigationState
      : "inactive";

  elements.navigationGoalState.textContent =
    displayState
      .replaceAll("_", " ")
      .toUpperCase();

  elements.navigationStateIndicator.className =
    `navigation-state-indicator ${displayState}`;

  elements.navigationDistanceRemaining.textContent =
    formatNavigationDistance(
      state.navigationFeedback.distanceRemaining
    );

  elements.navigationEstimatedTime.textContent =
    formatNavigationTime(
      state.navigationFeedback.estimatedTimeRemaining
    );

  elements.navigationElapsedTime.textContent =
    formatNavigationTime(
      state.navigationFeedback.navigationTime
    );

  elements.navigationRecoveryCount.textContent =
    String(
      state.navigationFeedback.recoveryCount
    );
}


function updateNavigationControls() {
  const navigationModeActive =
    state.connected
    && state.simulationState === "running"
    && state.modeState === "navigation";

  const goalBusy =
    state.navigationGoalActive
    || state.navigationRequestPending;

  elements.navigationGoalX.disabled =
    !navigationModeActive || goalBusy;

  elements.navigationGoalY.disabled =
    !navigationModeActive || goalBusy;

  elements.navigationGoalYaw.disabled =
    !navigationModeActive || goalBusy;

  elements.sendNavigationGoalButton.disabled =
    !navigationModeActive || goalBusy;

  elements.cancelNavigationGoalButton.disabled =
    !navigationModeActive || !goalBusy;

  updateNavigationDisplay();

  if (
    !navigationModeActive
    && !goalBusy
  ) {
    setNavigationGoalMessage(
      "Enter Navigation mode to send a goal.",
      "",
    );
  }
}


function setNavigationGoalMessage(
  message,
  level = "",
) {
  elements.navigationGoalMessage.textContent =
    message;

  elements.navigationGoalMessage.className =
    `navigation-goal-message ${level}`.trim();
}


function escapeHtml(value) {
  const temporaryElement =
    document.createElement("div");

  temporaryElement.textContent =
    String(value);

  return temporaryElement.innerHTML;
}


function updateConnectionStatus(status) {
  elements.connectionIndicator.className =
    `status-indicator ${status}`;

  if (status === "connected") {
    elements.connectionText.textContent = "ROS connected";
    updateSimulationControls();
    updateEnvironmentControls();
  updateMappingControls();
  updateLocalizationControls();
    updateMappingControls();
    updateLocalizationControls();
    updateModeControls();
    updateNavigationControls();
    return;
  }

  if (status === "connecting") {
    elements.connectionText.textContent =
      "Connecting to ROS…";

    setLifecycleButtonsBusy(true);
    setEnvironmentControlsBusy(true);
    setModeButtonsBusy(true);
    return;
  }

  elements.connectionText.textContent =
    "ROS disconnected";

  setLifecycleButtonsBusy(true);
  setEnvironmentControlsBusy(true);

  setSimulationMessage(
    "Simulation controls unavailable while ROS is disconnected.",
    "danger",
  );
}


function updateActiveSource(source) {
  if (source === state.activeSource) {
    return;
  }

  const previousSource = state.activeSource;
  state.activeSource = source;

  elements.activeSource.textContent =
    source.replaceAll("_", " ").toUpperCase();

  addLog(
    `Control source: ${previousSource} → ${source}`,
    source === "emergency_stop" ? "danger" : "info",
  );
}


function makeTwistStamped(linearX, angularZ) {
  const now = Date.now();
  const seconds = Math.floor(now / 1000);
  const nanoseconds = (now % 1000) * 1_000_000;

  return {
    header: {
      stamp: {
        sec: seconds,
        nanosec: nanoseconds,
      },
      frame_id: "base_link",
    },

    twist: {
      linear: {
        x: linearX,
        y: 0.0,
        z: 0.0,
      },

      angular: {
        x: 0.0,
        y: 0.0,
        z: angularZ,
      },
    },
  };
}


function publishVelocity(linearX, angularZ) {
  const safeLinearX = state.emergencyStop
    ? 0.0
    : linearX;

  const safeAngularZ = state.emergencyStop
    ? 0.0
    : angularZ;

  sendRosbridgeMessage({
    op: "publish",
    topic: "/cmd_vel/gui",
    msg: makeTwistStamped(
      safeLinearX,
      safeAngularZ,
    ),
  });

  updateCommandDisplay(
    safeLinearX,
    safeAngularZ,
  );
}


function calculateCurrentCommand() {
  return {
    linearX:
      state.linearDirection * state.linearSpeed,

    angularZ:
      state.angularDirection * state.angularSpeed,
  };
}


function publishCurrentCommand() {
  const command = calculateCurrentCommand();

  publishVelocity(
    command.linearX,
    command.angularZ,
  );
}


function startCommandLoop() {
  if (
    state.emergencyStop
    || state.publishTimer !== null
  ) {
    return;
  }

  publishCurrentCommand();

  state.publishTimer = window.setInterval(
    publishCurrentCommand,
    COMMAND_PUBLISH_INTERVAL_MS,
  );
}


function stopCommandLoop() {
  if (state.publishTimer !== null) {
    window.clearInterval(state.publishTimer);
    state.publishTimer = null;
  }
}


function publishStopBurst() {
  let remaining = STOP_BURST_COUNT;

  const publishStop = () => {
    publishVelocity(0.0, 0.0);
    remaining -= 1;

    if (remaining > 0) {
      window.setTimeout(
        publishStop,
        STOP_BURST_INTERVAL_MS,
      );
    }
  };

  publishStop();
}


function stopMotion(logEvent = true) {
  state.linearDirection = 0;
  state.angularDirection = 0;
  state.pressedKeys.clear();

  stopCommandLoop();
  clearActiveButton();
  publishStopBurst();

  if (logEvent) {
    addLog("Stop command published.", "info");
  }
}


function setMotion(linearDirection, angularDirection) {
  if (state.emergencyStop) {
    return;
  }

  state.linearDirection = linearDirection;
  state.angularDirection = angularDirection;

  startCommandLoop();
}


function updateCommandDisplay(linearX, angularZ) {
  elements.linearCommand.textContent =
    `${linearX.toFixed(2)} m/s`;

  elements.angularCommand.textContent =
    `${angularZ.toFixed(2)} rad/s`;
}


function publishEmergencyStop(enabled) {
  sendRosbridgeMessage({
    op: "publish",
    topic: "/control/emergency_stop",
    msg: {
      data: enabled,
    },
  });
}


function toggleEmergencyStop() {
  state.emergencyStop = !state.emergencyStop;

  if (state.emergencyStop) {
    stopMotion(false);
    publishEmergencyStop(true);

    elements.emergencyStopButton.classList.add(
      "engaged",
    );

    elements.emergencyButtonTitle.textContent =
      "RELEASE EMERGENCY STOP";

    elements.emergencyButtonSubtitle.textContent =
      "Robot motion is currently disabled";

    elements.safetyState.textContent = "E-STOP";
    elements.safetyState.className =
      "status-value danger";

    addLog("Emergency stop activated.", "danger");
    return;
  }

  publishEmergencyStop(false);

  elements.emergencyStopButton.classList.remove(
    "engaged",
  );

  elements.emergencyButtonTitle.textContent =
    "EMERGENCY STOP";

  elements.emergencyButtonSubtitle.textContent =
    "Immediately disable robot motion";

  elements.safetyState.textContent = "READY";
  elements.safetyState.className =
    "status-value safe";

  addLog("Emergency stop released.", "success");
}


function activatePointerButton(button) {
  clearActiveButton();

  state.activePointerButton = button;
  button.classList.add("active");

  const linear = Number(button.dataset.linear);
  const angular = Number(button.dataset.angular);

  setMotion(linear, angular);
}


function clearActiveButton() {
  if (state.activePointerButton) {
    state.activePointerButton.classList.remove(
      "active",
    );

    state.activePointerButton = null;
  }
}


function handlePointerRelease() {
  if (!state.activePointerButton) {
    return;
  }

  clearActiveButton();
  stopMotion(false);
}


function normalizedControlKey(event) {
  const key = event.key.toLowerCase();

  const keyMap = {
    w: "forward",
    arrowup: "forward",

    s: "reverse",
    arrowdown: "reverse",

    a: "left",
    arrowleft: "left",

    d: "right",
    arrowright: "right",
  };

  return keyMap[key] ?? null;
}


function commandFromPressedKeys() {
  const forward = state.pressedKeys.has("forward");
  const reverse = state.pressedKeys.has("reverse");
  const left = state.pressedKeys.has("left");
  const right = state.pressedKeys.has("right");

  let linearDirection = 0;
  let angularDirection = 0;

  if (forward !== reverse) {
    linearDirection = forward ? 1 : -1;
  }

  if (left !== right) {
    angularDirection = left ? 1 : -1;
  }

  return {
    linearDirection,
    angularDirection,
  };
}


function updateMotionFromKeyboard() {
  const command = commandFromPressedKeys();

  if (
    command.linearDirection === 0
    && command.angularDirection === 0
  ) {
    stopMotion(false);
    return;
  }

  setMotion(
    command.linearDirection,
    command.angularDirection,
  );
}


function shouldIgnoreKeyboardEvent(event) {
  const target = event.target;

  return (
    target instanceof HTMLInputElement
    || target instanceof HTMLTextAreaElement
    || target instanceof HTMLSelectElement
  );
}


function handleKeyDown(event) {
  if (shouldIgnoreKeyboardEvent(event)) {
    return;
  }

  if (event.code === "Space") {
    event.preventDefault();
    stopMotion();
    return;
  }

  const controlKey = normalizedControlKey(event);

  if (!controlKey || state.emergencyStop) {
    return;
  }

  event.preventDefault();

  state.pressedKeys.add(controlKey);
  updateMotionFromKeyboard();
}


function handleKeyUp(event) {
  const controlKey = normalizedControlKey(event);

  if (!controlKey) {
    return;
  }

  event.preventDefault();

  state.pressedKeys.delete(controlKey);
  updateMotionFromKeyboard();
}


function addLog(message, level = "info") {
  const entry = document.createElement("p");
  entry.className = `event-entry ${level}`;

  const timestamp = document.createElement("span");
  timestamp.className = "event-time";
  timestamp.textContent =
    new Date().toLocaleTimeString();

  const text = document.createElement("span");
  text.textContent = message;

  entry.append(timestamp, text);
  elements.eventLog.prepend(entry);

  while (elements.eventLog.children.length > 40) {
    elements.eventLog.lastElementChild.remove();
  }
}


function registerEventListeners() {
  elements.environmentButtons.forEach((button) => {
    button.addEventListener(
      "click",
      () => {
        requestEnvironment(
          button.dataset.environment
        );
      },
    );
  });

  elements.linearSpeed.addEventListener(
    "input",
    () => {
      state.linearSpeed =
        Number(elements.linearSpeed.value);

      elements.linearSpeedValue.textContent =
        `${state.linearSpeed.toFixed(2)} m/s`;
    },
  );

  elements.angularSpeed.addEventListener(
    "input",
    () => {
      state.angularSpeed =
        Number(elements.angularSpeed.value);

      elements.angularSpeedValue.textContent =
        `${state.angularSpeed.toFixed(2)} rad/s`;
    },
  );

  elements.driveButtons.forEach((button) => {
    button.addEventListener(
      "pointerdown",
      (event) => {
        event.preventDefault();

        try {
          button.setPointerCapture(event.pointerId);
        } catch {
          // Pointer capture is optional.
        }

        activatePointerButton(button);
      },
    );

    button.addEventListener(
      "pointerup",
      handlePointerRelease,
    );

    button.addEventListener(
      "pointercancel",
      handlePointerRelease,
    );

    button.addEventListener(
      "lostpointercapture",
      handlePointerRelease,
    );
  });

  elements.stopButton.addEventListener(
    "click",
    () => stopMotion(),
  );

  elements.emergencyStopButton.addEventListener(
    "click",
    toggleEmergencyStop,
  );

  elements.clearLogButton.addEventListener(
    "click",
    () => {
      elements.eventLog.replaceChildren();
      addLog("Activity log cleared.", "info");
    },
  );

  window.addEventListener(
    "keydown",
    handleKeyDown,
  );

  window.addEventListener(
    "keyup",
    handleKeyUp,
  );

  window.addEventListener(
    "blur",
    () => {
      stopMotion(false);
      addLog(
        "Window focus lost; motion stopped.",
        "warning",
      );
    },
  );

  document.addEventListener(
    "visibilitychange",
    () => {
      if (document.hidden) {
        stopMotion(false);

        addLog(
          "Dashboard hidden; motion stopped.",
          "warning",
        );
      }
    },
  );

  window.addEventListener(
    "beforeunload",
    () => {
      publishVelocity(0.0, 0.0);
    },
  );

  elements.startSimulationButton.addEventListener(
    "click",
    () => callSimulationService("start"),
  );

  elements.stopSimulationButton.addEventListener(
    "click",
    () => callSimulationService("stop"),
  );

  elements.resetSimulationButton.addEventListener(
    "click",
    () => callSimulationService("reset"),
  );

  elements.manualModeButton.addEventListener(
    "click",
    () => callModeService("manual"),
  );

  elements.mappingModeButton.addEventListener(
    "click",
    () => callModeService("mapping"),
  );

  elements.localizationModeButton.addEventListener(
    "click",
    () => callModeService("localization"),
  );

  elements.navigationModeButton.addEventListener(
    "click",
    () => callModeService("navigation"),
  );

  elements.stopModeButton.addEventListener(
    "click",
    () => callModeService("stop"),
  );
  elements.saveMapButton.addEventListener(
    "click",
    saveMap,
  );

  elements.mapNameInput.addEventListener(
    "keydown",
    (event) => {
      if (event.key === "Enter") {
        saveMap();
      }
    },
  );

  elements.selectLocalizationMapButton
    .addEventListener(
      "click",
      selectLocalizationMap,
    );

  elements.localizationMapSelect
    .addEventListener(
      "change",
      updateLocalizationControls,
    );

  elements.setInitialPoseButton
    .addEventListener(
      "click",
      setInitialPose,
    );

  elements.sendNavigationGoalButton
    .addEventListener(
      "click",
      sendNavigationGoal,
    );

  elements.cancelNavigationGoalButton
    .addEventListener(
      "click",
      cancelNavigationGoal,
    );

  [
    elements.navigationGoalX,
    elements.navigationGoalY,
    elements.navigationGoalYaw,
  ].forEach((input) => {
    input.addEventListener(
      "keydown",
      (event) => {
        if (event.key === "Enter") {
          sendNavigationGoal();
        }
      },
    );
  });

}


function initialize() {
  registerEventListeners();
  updateCommandDisplay(0.0, 0.0);
  updateNavigationDisplay();
  updateNavigationControls();
  connectRosbridge();
}


initialize();