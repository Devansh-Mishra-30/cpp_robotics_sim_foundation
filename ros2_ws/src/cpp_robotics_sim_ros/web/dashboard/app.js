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
  modeState: "stopped",
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
    subscribeToModeStatus();

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


function subscribeToModeStatus() {
  sendRosbridgeMessage({
    op: "subscribe",
    topic: "/mode/status",
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
    message.op === "service_response"
    && message.id
  ) {
    handleServiceResponse(message);
  }
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
    updateSimulationControls();
  }
}


function updateSimulationState(simulationState) {
  state.simulationState = simulationState;

  elements.simulationState.textContent =
    simulationState.toUpperCase();

  elements.simulationStateIndicator.className =
    `simulation-state-indicator ${simulationState}`;

  updateSimulationControls();
  updateModeControls();

  if (simulationState !== "running") {
    setModeMessage(
      "Start the simulation before selecting a mode.",
      "",
    );
  }
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

  const buttons = {
    manual: elements.manualModeButton,
    mapping: elements.mappingModeButton,
    localization: elements.localizationModeButton,
    navigation: elements.navigationModeButton,
  };

  Object.entries(buttons).forEach(
    ([mode, button]) => {
      button.disabled =
        !enabled || state.modeState === mode;

      button.classList.toggle(
        "active",
        state.modeState === mode,
      );
    },
  );

  const activeMode = [
    "manual",
    "mapping",
    "localization",
    "navigation",
  ].includes(state.modeState);

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


function updateConnectionStatus(status) {
  elements.connectionIndicator.className =
    `status-indicator ${status}`;

  if (status === "connected") {
    elements.connectionText.textContent = "ROS connected";
    updateSimulationControls();
    updateModeControls();
    return;
  }

  if (status === "connecting") {
    elements.connectionText.textContent =
      "Connecting to ROS…";

    setLifecycleButtonsBusy(true);
    setModeButtonsBusy(true);
    return;
  }

  elements.connectionText.textContent =
    "ROS disconnected";

  setLifecycleButtonsBusy(true);

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
}


function initialize() {
  registerEventListeners();
  updateCommandDisplay(0.0, 0.0);
  connectRosbridge();
}


initialize();